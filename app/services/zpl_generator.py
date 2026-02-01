from app.models.label import (
    LabelRequest,
    SimpleLabelRequest,
    TextElement,
    BarcodeElement,
    QRCodeElement,
    LineElement,
    BarcodeType,
    LabelSize,
    TextAlignment,
)


class ZPLGenerator:
    """Generador de código ZPL para impresoras térmicas Zebra/compatibles"""

    # 203 DPI = 8 dots por mm
    DOTS_PER_MM = 8

    # Tamaños predefinidos de etiquetas (ancho x alto en mm)
    LABEL_SIZES = {
        LabelSize.SMALL: (50, 25),
        LabelSize.MEDIUM: (60, 40),
        LabelSize.LARGE: (100, 50),
    }

    def __init__(self):
        self.zpl_commands: list[str] = []

    def _mm_to_dots(self, mm: int) -> int:
        """Convierte milímetros a dots"""
        return mm * self.DOTS_PER_MM

    def _start_label(self, width_mm: int, height_mm: int) -> None:
        """Inicia una nueva etiqueta"""
        width_dots = self._mm_to_dots(width_mm)
        height_dots = self._mm_to_dots(height_mm)

        self.zpl_commands = [
            "^XA",  # Inicio de formato
            "^CI28",  # UTF-8 encoding para caracteres especiales (ñ, acentos, etc.)
            "^MNW",  # Media tracking: Web sensing (detección de gap para etiquetas troqueladas)
            f"^PW{width_dots}",  # Ancho de impresión
            f"^LL{height_dots}",  # Largo de etiqueta
            "^LH0,0",  # Home position
            # "^JMA",  # Reimprime automáticamente después de error (evita pausas)
        ]

    def _end_label(self, copies: int = 1) -> None:
        """Finaliza la etiqueta"""
        self.zpl_commands.append(f"^PQ{copies}")  # Cantidad de copias
        self.zpl_commands.append("^XZ")  # Fin de formato

    def _add_text(self, element: TextElement) -> None:
        """Añade un elemento de texto"""
        self.zpl_commands.append(f"^FO{element.x},{element.y}")
        # ^A0N = Fuente escalable, orientación Normal
        # Para simular negrita, aumentamos ligeramente el ancho de la fuente
        if element.bold:
            # Ancho mayor que alto simula negrita
            font_width = int(element.font_size * 1.2)
            self.zpl_commands.append(f"^A0N,{element.font_size},{font_width}")
        else:
            self.zpl_commands.append(f"^A0N,{element.font_size},{element.font_size}")
        self.zpl_commands.append(f"^FD{element.text}^FS")

    def _add_barcode(self, element: BarcodeElement) -> None:
        """Añade un código de barras"""
        self.zpl_commands.append(f"^FO{element.x},{element.y}")

        # Configurar según tipo de código de barras
        show_interpretation = "Y" if element.show_text else "N"

        if element.barcode_type == BarcodeType.CODE128:
            self.zpl_commands.append(f"^BY{element.width}")
            self.zpl_commands.append(f"^BCN,{element.height},{show_interpretation},N,N")
        elif element.barcode_type == BarcodeType.CODE39:
            self.zpl_commands.append(f"^BY{element.width}")
            self.zpl_commands.append(f"^B3N,N,{element.height},{show_interpretation},N")
        elif element.barcode_type == BarcodeType.EAN13:
            self.zpl_commands.append(f"^BY{element.width}")
            self.zpl_commands.append(f"^BEN,{element.height},{show_interpretation},N")
        elif element.barcode_type == BarcodeType.EAN8:
            self.zpl_commands.append(f"^BY{element.width}")
            self.zpl_commands.append(f"^B8N,{element.height},{show_interpretation},N")
        elif element.barcode_type == BarcodeType.UPCA:
            self.zpl_commands.append(f"^BY{element.width}")
            self.zpl_commands.append(f"^BUN,{element.height},{show_interpretation},N,N")

        self.zpl_commands.append(f"^FD{element.data}^FS")

    def _encode_qr_data(self, data: str) -> str:
        """Codifica datos para QR con soporte de caracteres especiales y saltos de línea.

        Usa ^FH (Field Hexadecimal) con _ como indicador de escape.
        Los saltos de línea se codifican como _0D_0A (CR+LF) para máxima compatibilidad.
        """
        encoded = []
        for char in data:
            if char == '\n':
                # CR+LF para máxima compatibilidad con lectores QR
                encoded.append("_0D_0A")
            elif char == '\r':
                # Ignorar CR sueltos si ya vienen en el texto
                continue
            elif char == '_':
                # Escapar el carácter de escape
                encoded.append("_5F")
            elif char == '^':
                # Escapar el carácter de control ZPL
                encoded.append("_5E")
            else:
                encoded.append(char)
        return "".join(encoded)

    def _add_qr_code(self, element: QRCodeElement) -> None:
        """Añade un código QR con soporte para saltos de línea"""
        self.zpl_commands.append(f"^FO{element.x},{element.y}")
        self.zpl_commands.append(f"^BQN,2,{element.size}")

        # Usar ^FH para habilitar codificación hexadecimal si hay caracteres especiales
        if '\n' in element.data or '\r' in element.data or '_' in element.data or '^' in element.data:
            encoded_data = self._encode_qr_data(element.data)
            self.zpl_commands.append(f"^FH_^FDQA,{encoded_data}^FS")
        else:
            self.zpl_commands.append(f"^FDQA,{element.data}^FS")

    def _add_line(self, element: LineElement) -> None:
        """Añade una línea o rectángulo"""
        self.zpl_commands.append(f"^FO{element.x},{element.y}")
        self.zpl_commands.append(f"^GB{element.width},{element.height},{element.thickness}^FS")

    def generate_from_request(self, request: LabelRequest) -> str:
        """Genera código ZPL a partir de una solicitud completa"""
        self._start_label(request.label_width_mm, request.label_height_mm)

        # Añadir todos los elementos
        for text in request.texts:
            self._add_text(text)

        for barcode in request.barcodes:
            self._add_barcode(barcode)

        for qr in request.qr_codes:
            self._add_qr_code(qr)

        for line in request.lines:
            self._add_line(line)

        self._end_label(request.copies)

        return "\n".join(self.zpl_commands)

    def generate_simple_label(self, request: SimpleLabelRequest) -> str:
        """Genera código ZPL a partir de una solicitud simplificada"""
        # Determinar tamaño de etiqueta
        if request.label_size == LabelSize.CUSTOM:
            width_mm = request.custom_width_mm or 60
            height_mm = request.custom_height_mm or 40
        else:
            width_mm, height_mm = self.LABEL_SIZES[request.label_size]

        self._start_label(width_mm, height_mm)

        current_y = 30

        # Título
        title_element = TextElement(
            x=50,
            y=current_y,
            text=request.title,
            font_size=60,
            bold=True
        )
        self._add_text(title_element)
        current_y += 50

        # Subtítulo
        if request.subtitle:
            subtitle_element = TextElement(
                x=50,
                y=current_y,
                text=request.subtitle,
                font_size=45,
                bold=False
            )
            self._add_text(subtitle_element)
            current_y += 40

        # Código de barras
        if request.barcode_data:
            barcode_element = BarcodeElement(
                x=50,
                y=current_y,
                data=request.barcode_data,
                barcode_type=request.barcode_type,
                height=60,
                width=2,
                show_text=True
            )
            self._add_barcode(barcode_element)
            current_y += 90

        # Código QR
        if request.qr_data:
            qr_element = QRCodeElement(
                x=50,
                y=current_y,
                data=request.qr_data,
                size=4
            )
            self._add_qr_code(qr_element)

        self._end_label(request.copies)

        return "\n".join(self.zpl_commands)
