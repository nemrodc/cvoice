from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    HOST: str = "0.0.0.0"
    PORT: int = 6800

    MODEL_PATH: Path = Path("pretrained_models/CosyVoice2-0.5B")
    DEVICE: str = "cuda"          # "cpu" para fallback

    CHUNK_MS: int = 20            # tamaño de audio que se envía‑devuelve
    SAMPLE_RATE: int = 24000      # CosyVoice2 default

settings = Settings()
