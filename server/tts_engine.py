
from typing import Iterable
from cosyvoice.cli.cosyvoice import CosyVoice2
from .settings import settings
import logging

# Configurar logging para TTSEngine
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TTSEngine:
    """Carga el modelo una sola vez y expone síntesis streaming."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        logger.info("Inicializando CosyVoice2...")
        self.model = CosyVoice2(
            str(settings.MODEL_PATH), 
            use_flow_cache=True,
        )
        logger.info("CosyVoice2 inicializado correctamente.")

    def stream(self, text_iterable: Iterable[str], speaker_id: str):
        """Genera segmentos de audio (tensor) usando CosyVoice en modo stream."""
        # Convertimos el iterable a una lista para depuración
        text_list = list(text_iterable)
        logger.info("Texto recibido para síntesis", extra={"text_list": text_list, "num_phrases": len(text_list)})
        
        if not text_list:
            logger.warning("No hay texto para sintetizar, omitiendo...")
            return

        try:
            chunk_count = 0
            for segment in self.model.inference_zero_shot(
                text_list,
                prompt_text="",
                prompt_speech_16k="",
                zero_shot_spk_id=speaker_id,
                stream=True,
            ):
                chunk_count += 1
                logger.info("Chunk de audio generado", extra={"chunk_id": chunk_count, "segment": str(segment)})
                yield segment["tts_speech"]
            logger.info("Síntesis completada", extra={"total_chunks": chunk_count})
        except Exception as e:
            logger.error("Error en la síntesis de CosyVoice2", extra={"error": str(e)})
            raise