import sys
import torchaudio
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav

sys.path.append('third_party/Matcha-TTS')

# Cargar modelo
cosyvoice = CosyVoice2('pretrained_models/CosyVoice2-0.5B')

# Cargar audio de referencia 
prompt_audio = load_wav('asset/zero_shot_prompt3.wav', 16000)

# Texto a sintetizar
texto = "<|en|>This is Josh speaking. I'm an actor known for playing the fictional character named 'Peeta Mellark' in the famous Hunger Games film trilogy."
transcripcion = "<|en|>What is Josh Hutcherson known for?"

for i, segment in enumerate(cosyvoice.inference_zero_shot(
    texto, 
    transcripcion, 
    prompt_audio, 
    stream=False)):
    torchaudio.save(f"output_{i}.wav", segment['tts_speech'], cosyvoice.sample_rate)


print("✅ Audio generado con éxito.")

