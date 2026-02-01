import socket
import psycopg
import logging
import os


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IpService:
    def __init__(self, database_url: str | None = None):
        self.ip_local = self.obtener_ip_local()
        self.database_url = database_url
        
    def obtener_ip_local(self):
        try:
            ip_local = os.getenv("HOST_LAN_IP")
            if ip_local is None:
                # Crea un socket temporal y conecta a una dirección inexistente
                # Esto no requiere conexión real, pero permite obtener la IP local
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))  # Google DNS (no se envía tráfico real)
                ip_local = s.getsockname()[0]
                s.close()
            return ip_local
        except Exception:
            return "127.0.0.1"  # Fallback si falla

    def update_ip_local(self):
        """
        Actualiza la IP local en la BD (Postgres).

        Requiere `database_url` (ej: postgresql://...).
        """
        if not self.database_url:
            return False
        with psycopg.connect(self.database_url) as conn:
            logger.info(f"Ejecutando consulta en la BD")
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE public.configuracion_printers SET ip = %s WHERE id = %s",
                    (self.ip_local, 1),
                )
                conn.commit()
                logger.info(f"Columnas afectadas: {cur.rowcount}")
                if cur.rowcount > 0:
                    logger.info(f"IP local actualizada en la BD")
                else:
                    logger.error(f"IP local no actualizada en la BD")
                    return False
                
        return True

if __name__ == "__main":
    ip_service = IpService()
    ip_service.update_ip_local()
    print("IP local:", ip_service.obtener_ip_local())   