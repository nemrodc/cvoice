import uvicorn
from .settings import settings
import sys
import signal

from .websocket_api import app, engine  # Asegúrate que esto importa correctamente tu FastAPI app y TTSEngine singleton

def shutdown_handler(signum, frame):
    print("\n🛑 Señal de interrupción recibida (Ctrl+C). Cerrando servidor...")
    # Libera recursos del TTS si es necesario (ej: cerrar modelos pesados o procesos en segundo plano)
    if hasattr(engine, "model") and engine.model is not None:
        print("🔻 Liberando modelo CosyVoice...")
        del engine.model
    sys.exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, shutdown_handler)   # Ctrl+C
    signal.signal(signal.SIGTERM, shutdown_handler)  # Cierre por sistema (opcional)

    uvicorn.run(
        "server.websocket_api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False, log_level="info",
        ws_ping_timeout=3600
    )

