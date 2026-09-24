"""
security.py
-----------
Utilidades de seguridad compartidas por toda la API:

- Detección del entorno (desarrollo / producción).
- Limitador de intentos (anti fuerza bruta) para login y registro.
- Cabeceras HTTP de seguridad en todas las respuestas.

NOTA: el limitador guarda los intentos en la memoria del proceso. Si se
ejecutan varios workers/contenedores, cada uno lleva su propia cuenta; en ese
caso conviene mover el conteo a Redis o limitar también desde Nginx.
"""
import logging
import os
import threading
import time
from collections import deque
from typing import Deque, Dict, Tuple

from fastapi import FastAPI, HTTPException, Request, status

logger = logging.getLogger("agrocontrol.security")

ENTORNO = os.getenv("ENVIRONMENT", "development").strip().lower()
ES_PRODUCCION = ENTORNO in {"production", "produccion", "prod"}


# ---------------------------------------------------------------------------
# IP del cliente
# ---------------------------------------------------------------------------
def ip_cliente(request: Request) -> str:
    """
    IP del cliente. Detrás de Nginx/proxy, activar TRUST_PROXY_HEADERS=true
    para leer X-Forwarded-For (se usa la última entrada, la que agregó nuestro
    proxy; las anteriores pueden venir falsificadas por el cliente).
    """
    if os.getenv("TRUST_PROXY_HEADERS", "false").strip().lower() == "true":
        reenviado = request.headers.get("x-forwarded-for", "")
        if reenviado:
            ultimo = reenviado.split(",")[-1].strip()
            if ultimo:
                return ultimo
    return request.client.host if request.client else "desconocido"


# ---------------------------------------------------------------------------
# Limitador de intentos (ventana deslizante)
# ---------------------------------------------------------------------------
class LimitadorIntentos:
    def __init__(self, max_intentos: int, ventana_segundos: int):
        self.max_intentos = max_intentos
        self.ventana = ventana_segundos
        self._eventos: Dict[str, Deque[float]] = {}
        self._lock = threading.Lock()

    def _podar(self, clave: str, ahora: float):
        cola = self._eventos.get(clave)
        if cola is None:
            return None
        while cola and ahora - cola[0] > self.ventana:
            cola.popleft()
        if not cola:
            del self._eventos[clave]
            return None
        return cola

    def segundos_bloqueado(self, clave: str) -> int:
        """0 si puede intentar; si no, segundos que faltan para reintentar."""
        ahora = time.monotonic()
        with self._lock:
            cola = self._podar(clave, ahora)
            if cola is None or len(cola) < self.max_intentos:
                return 0
            return max(1, int(self.ventana - (ahora - cola[0])) + 1)

    def registrar(self, clave: str) -> None:
        ahora = time.monotonic()
        with self._lock:
            if len(self._eventos) > 20000:  # evita crecimiento sin límite de memoria
                for k in list(self._eventos):
                    self._podar(k, ahora)
                if len(self._eventos) > 50000:
                    self._eventos.clear()
            cola = self._podar(clave, ahora)
            if cola is None:
                cola = self._eventos.setdefault(clave, deque())
            cola.append(ahora)

    def reiniciar(self, clave: str) -> None:
        with self._lock:
            self._eventos.pop(clave, None)


def exigir_sin_bloqueo(*pares: Tuple[LimitadorIntentos, str]) -> None:
    """Lanza 429 si alguno de los (limitador, clave) está bloqueado."""
    espera = max((lim.segundos_bloqueado(clave) for lim, clave in pares), default=0)
    if espera:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos. Espera unos minutos antes de volver a intentarlo.",
            headers={"Retry-After": str(espera)},
        )


# ---------------------------------------------------------------------------
# Cabeceras de seguridad
# ---------------------------------------------------------------------------
def instalar_cabeceras_seguridad(app: FastAPI) -> None:
    @app.middleware("http")
    async def cabeceras_seguridad(request: Request, call_next):
        respuesta = await call_next(request)
        h = respuesta.headers
        h.setdefault("X-Content-Type-Options", "nosniff")
        h.setdefault("X-Frame-Options", "DENY")
        h.setdefault("Referrer-Policy", "no-referrer")
        h.setdefault("Permissions-Policy", "geolocation=(), camera=(), microphone=()")
        if ES_PRODUCCION:
            h.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        if request.url.path.startswith("/api/"):
            # Respuestas de la API: JSON, nunca deben guardarse en caché ni incrustarse.
            h.setdefault("Cache-Control", "no-store")
            h.setdefault("Content-Security-Policy", "default-src 'none'; frame-ancestors 'none'")
        return respuesta
