from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class BarcodeType(str, Enum):
    CODE128 = "code128"
    CODE39 = "code39"
    EAN13 = "ean13"
    EAN8 = "ean8"
    UPCA = "upca"
    QR = "qr"


class LabelSize(str, Enum):
    SMALL = "small"      # 50x25mm
    MEDIUM = "medium"    # 60x40mm
    LARGE = "large"      # 100x50mm
    CUSTOM = "custom"


class TextAlignment(str, Enum):
    LEFT = "left"
    CENTER = "center"
    RIGHT = "right"


class LabelElement(BaseModel):
    """Elemento base para la etiqueta"""
    x: int = Field(ge=0, description="Posición X en dots (203 dpi = 8 dots/mm)")
    y: int = Field(ge=0, description="Posición Y en dots")


class TextElement(LabelElement):
    """Elemento de texto"""
    text: str
    font_size: int = Field(default=30, ge=10, le=200)
    bold: bool = False
    alignment: TextAlignment = TextAlignment.LEFT


class BarcodeElement(LabelElement):
    """Elemento de código de barras"""
    data: str
    barcode_type: BarcodeType = BarcodeType.CODE128
    height: int = Field(default=50, ge=20, le=200)
    width: int = Field(default=2, ge=1, le=10, description="Ancho de las barras")
    show_text: bool = True


class QRCodeElement(LabelElement):
    """Elemento de código QR"""
    data: str
    size: int = Field(default=5, ge=15, le=300, description="Factor de magnificación")


class LineElement(LabelElement):
    """Elemento de línea/rectángulo"""
    width: int = Field(ge=1)
    height: int = Field(ge=1)
    thickness: int = Field(default=2, ge=1, le=10)


class LabelRequest(BaseModel):
    """Solicitud para imprimir una etiqueta"""
    # Configuración general
    label_width_mm: int = Field(default=60, ge=20, le=200)
    label_height_mm: int = Field(default=40, ge=10, le=200)
    copies: int = Field(default=1, ge=1, le=100)

    # Elementos de la etiqueta
    texts: list[TextElement] = Field(default_factory=list)
    barcodes: list[BarcodeElement] = Field(default_factory=list)
    qr_codes: list[QRCodeElement] = Field(default_factory=list)
    lines: list[LineElement] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "label_width_mm": 60,
                "label_height_mm": 40,
                "copies": 1,
                "texts": [
                    {"x": 50, "y": 30, "text": "Producto ABC", "font_size": 35, "bold": True},
                    {"x": 50, "y": 80, "text": "SKU: 12345", "font_size": 25}
                ],
                "barcodes": [
                    {"x": 50, "y": 120, "data": "1234567890", "barcode_type": "code128", "height": 60}
                ]
            }
        }


class SimpleLabelRequest(BaseModel):
    """Solicitud simplificada para etiquetas comunes"""
    title: str = Field(description="Título principal de la etiqueta")
    subtitle: Optional[str] = Field(default=None, description="Subtítulo o descripción")
    barcode_data: Optional[str] = Field(default=None, description="Datos para código de barras")
    barcode_type: BarcodeType = Field(default=BarcodeType.CODE128)
    qr_data: Optional[str] = Field(default=None, description="Datos para código QR")
    copies: int = Field(default=1, ge=1, le=100)
    label_size: LabelSize = Field(default=LabelSize.MEDIUM)

    # Para tamaño personalizado
    custom_width_mm: Optional[int] = Field(default=None, ge=20, le=200)
    custom_height_mm: Optional[int] = Field(default=None, ge=10, le=200)

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Producto ABC",
                "subtitle": "SKU: 12345",
                "barcode_data": "1234567890",
                "barcode_type": "code128",
                "copies": 2,
                "label_size": "medium"
            }
        }


class PrintResponse(BaseModel):
    """Respuesta de impresión"""
    success: bool
    message: str
    zpl_preview: Optional[str] = Field(default=None, description="Vista previa del código ZPL generado")
