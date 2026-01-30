import socket
import asyncio
from typing import Optional
from app.config import get_settings


class PrinterConnectionError(Exception):
    """Error de conexión con la impresora"""
    pass


class PrinterService:
    """Servicio para comunicación con impresora térmica via socket TCP"""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        settings = get_settings()
        self.host = host or settings.host_ribetec_printer
        self.port = port or settings.printer_port
        self.timeout = 10  # segundos

    async def send_zpl(self, zpl_code: str) -> bool:
        """
        Envía código ZPL a la impresora de forma asíncrona.

        Args:
            zpl_code: Código ZPL a enviar

        Returns:
            True si el envío fue exitoso

        Raises:
            PrinterConnectionError: Si hay error de conexión
        """
        try:
            # Ejecutar la operación de socket en un executor para no bloquear
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._send_sync, zpl_code)
            return True
        except socket.timeout:
            raise PrinterConnectionError(
                f"Timeout al conectar con la impresora en {self.host}:{self.port}"
            )
        except socket.error as e:
            raise PrinterConnectionError(
                f"Error de conexión con la impresora: {e}"
            )
        except Exception as e:
            raise PrinterConnectionError(
                f"Error inesperado al enviar a la impresora: {e}"
            )

    def _send_sync(self, zpl_code: str) -> None:
        """Envía código ZPL de forma síncrona"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            sock.sendall(zpl_code.encode("utf-8"))

    def test_connection(self) -> bool:
        """
        Prueba la conexión con la impresora.

        Returns:
            True si la conexión es exitosa
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect((self.host, self.port))
                return True
        except Exception:
            return False

    async def test_connection_async(self) -> bool:
        """Prueba la conexión de forma asíncrona"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.test_connection)

    async def print_test_page(self) -> bool:
        """
        Imprime una página de prueba.

        Returns:
            True si la impresión fue exitosa
        """
        test_zpl = """
^XA
^PW480
^LL320
^LH0,0
^FO50,30
^A0N,40,40
^FDTest de Impresion^FS
^FO50,90
^A0N,25,25
^FDRibetec RT-420ME^FS
^FO50,130
^A0N,25,25
^FDConexion exitosa!^FS
^FO50,180
^BQN,2,5
^FDQA,API-RIBETEC-PRINTER^FS
^PQ1
^XZ
"""
        return await self.send_zpl(test_zpl)
