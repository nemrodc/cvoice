import sys
import os
sys.path.append(os.path.abspath("third_party/Matcha-TTS"))
import torchaudio
from cosyvoice.cli.cosyvoice import CosyVoice2
import os
import time

# Ruta de salida
OUTPUT_DIR = "debug_chunks"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cargar el modelo
print("🔧 Cargando CosyVoice2...")
cosy = CosyVoice2("pretrained_models/CosyVoice2-0.5B", use_flow_cache=True)

# Texto a sintetizar
text = "<|en|>Hello, how are you doing today? I’m testing streaming synthesis with CosyVoice."

# Sintetizar en modo streaming
print("🧠 Iniciando síntesis con stream=True...")
start = time.time()
segments = []

for i, segment in enumerate(cosy.inference_zero_shot(text, "", "", zero_shot_spk_id="josh_v1", stream=True)):
    audio = segment["tts_speech"]
    duration = audio.shape[-1] / cosy.sample_rate
    print(f"📦 Segmento {i+1}: {audio.shape[-1]} muestras → {duration:.2f} s")

    out_path = os.path.join(OUTPUT_DIR, f"chunk_{i:02d}.wav")
    torchaudio.save(out_path, audio, cosy.sample_rate)
    segments.append(audio)

end = time.time()
total_len = sum([s.shape[-1] for s in segments]) / cosy.sample_rate

print(f"\n✅ Completado en {end - start:.2f}s")
print(f"🔉 {len(segments)} segmentos, duración total: {total_len:.2f} segundos")
print(f"📂 Archivos guardados en: {os.path.abspath(OUTPUT_DIR)}")
