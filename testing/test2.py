import sys
import torchaudio
from cosyvoice.cli.cosyvoice import CosyVoice2

sys.path.append('third_party/Matcha-TTS')

# Cargar el modelo
cosyvoice = CosyVoice2('pretrained_models/CosyVoice2-0.5B')
    
# Texto a sintetizar usando el hablante guardado
texto = "<|en|>I can't believe it... [sigh] This is unbelievable. [laughter] But it's true."

# Inferencia usando solo el ID del hablante
for i, segment in enumerate(cosyvoice.inference_zero_shot(
    texto,
    "",  # no transcripción
    "",  # no audio
    zero_shot_spk_id="josh_v1",
    stream=False
)):
    torchaudio.save(f"josh_output_{i}.wav", segment['tts_speech'], cosyvoice.sample_rate)

print("✅ Audio generado usando hablante guardado.")
