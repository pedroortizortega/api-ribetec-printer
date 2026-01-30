from fastapi import APIRouter, HTTPException, Query
from app.models import LabelRequest, SimpleLabelRequest, PrintResponse
from app.services import PrinterService, PrinterConnectionError, ZPLGenerator
import logging

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/print", tags=["Printing"])


@router.post("/label", response_model=PrintResponse)
async def print_label(request: LabelRequest, preview_only: bool = Query(False)):
    """
    Imprime una etiqueta personalizada con control total sobre los elementos.

    - **label_width_mm**: Ancho de la etiqueta en milímetros
    - **label_height_mm**: Alto de la etiqueta en milímetros
    - **copies**: Número de copias a imprimir
    - **texts**: Lista de elementos de texto
    - **barcodes**: Lista de códigos de barras
    - **qr_codes**: Lista de códigos QR
    - **lines**: Lista de líneas/rectángulos
    - **preview_only**: Si es True, solo devuelve el ZPL sin imprimir
    """
    generator = ZPLGenerator()
    zpl_code = generator.generate_from_request(request)
    if preview_only:
        logger.info(f"Etiqueta enviada correctamente ({dict(request)})")
        return PrintResponse(
            success=True,
            message="Vista previa generada (no se envió a la impresora)",
            zpl_preview=zpl_code
        )

    printer = PrinterService()
    try:
        await printer.send_zpl(zpl_code)
        logger.info(f"Etiqueta enviada correctamente ({dict(request)})")
        return PrintResponse(
            success=True,
            message=f"Etiqueta enviada correctamente ({request.copies} copia(s))",
            zpl_preview=zpl_code
        )
    except PrinterConnectionError as e:
        logger.error(f"Error al enviar la etiqueta: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/simple", response_model=PrintResponse)
async def print_simple_label(request: SimpleLabelRequest, preview_only: bool = Query(False)):
    """
    Imprime una etiqueta usando un formato simplificado.

    - **title**: Título principal de la etiqueta
    - **subtitle**: Subtítulo opcional
    - **barcode_data**: Datos para código de barras (opcional)
    - **barcode_type**: Tipo de código de barras (code128, code39, ean13, etc.)
    - **qr_data**: Datos para código QR (opcional)
    - **copies**: Número de copias
    - **label_size**: Tamaño predefinido (small, medium, large, custom)
    - **preview_only**: Si es True, solo devuelve el ZPL sin imprimir
    """
    generator = ZPLGenerator()
    zpl_code = generator.generate_simple_label(request)

    if preview_only:
        return PrintResponse(
            success=True,
            message="Vista previa generada (no se envió a la impresora)",
            zpl_preview=zpl_code
        )

    printer = PrinterService()
    try:
        await printer.send_zpl(zpl_code)
        return PrintResponse(
            success=True,
            message=f"Etiqueta enviada correctamente ({request.copies} copia(s))",
            zpl_preview=zpl_code
        )
    except PrinterConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.post("/raw", response_model=PrintResponse)
async def print_raw_zpl(zpl_code: str):
    """
    Envía código ZPL directamente a la impresora.

    Útil para etiquetas pre-diseñadas o código ZPL generado externamente.
    """
    if not zpl_code.strip():
        raise HTTPException(status_code=400, detail="El código ZPL no puede estar vacío")

    printer = PrinterService()
    try:
        await printer.send_zpl(zpl_code)
        return PrintResponse(
            success=True,
            message="Código ZPL enviado correctamente"
        )
    except PrinterConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/test", response_model=PrintResponse)
async def print_test_page():
    """
    Imprime una página de prueba para verificar la conexión con la impresora.
    """
    printer = PrinterService()
    try:
        await printer.print_test_page()
        return PrintResponse(
            success=True,
            message="Página de prueba enviada correctamente"
        )
    except PrinterConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/status")
async def check_printer_status():
    """
    Verifica el estado de conexión con la impresora.
    """
    printer = PrinterService()
    is_connected = await printer.test_connection_async()

    return {
        "printer_host": printer.host,
        "printer_port": printer.port,
        "connected": is_connected,
        "status": "online" if is_connected else "offline"
    }
