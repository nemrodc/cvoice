import sys
import torchaudio
from cosyvoice.cli.cosyvoice import CosyVoice2
from cosyvoice.utils.file_utils import load_wav

sys.path.append('third_party/Matcha-TTS')

# Cargar modelo
cosyvoice = CosyVoice2('pretrained_models/CosyVoice2-0.5B')
    

# Cargar prompt de voz y transcripción
prompt_audio = load_wav('asset/zero_shot_prompt3.wav', 16000)
texto = "<|en|>Hi, my name is Josh Hutcherson and this is my voice."
transcripcion = "<|en|>What is Josh Hutcherson known for?"
spk_id="josh_v1"


# save zero_shot spk for future usage
assert cosyvoice.add_zero_shot_spk(
    transcripcion, 
    prompt_audio, 
    spk_id) is True
for i, j in enumerate(cosyvoice.inference_zero_shot(
    texto, 
    transcripcion, 
    prompt_audio, 
    stream=False)):
    torchaudio.save('zero_shot_{}.wav'.format(i), j['tts_speech'], cosyvoice.sample_rate)
cosyvoice.save_spkinfo()


print(f"✅ Hablante '{spk_id}' guardado correctamente.")

