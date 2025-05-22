import asyncio
import json
import uuid
import websockets
import os
import torchaudio
import io
import sounddevice as sd
import threading

import torch  # para guardar como tensor

WS_URL = "ws://localhost:6800/synthesize"
OUTPUT_DIR = "debug_received_chunks"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def play_audio_tensor(audio_tensor, sample_rate):
    """Reproduce un tensor de audio (torch.Tensor [1, T]) como sonido."""
    waveform = audio_tensor.squeeze(0).numpy()
    sd.play(waveform, sample_rate)
    sd.wait()


async def main():
    uid = str(uuid.uuid4())

    async with websockets.connect(WS_URL, max_size=None) as ws:
        # Enviar texto completo
        payload = json.dumps({
            "id": uid,
            "text": "<|en|>Hello, how are you doing today?",
            "lang": "en",
            "speaker": "josh_v1"
        })
        await ws.send(payload)

        # Recibir encabezado con parámetros de audio
        header_raw = await ws.recv()
        header = json.loads(header_raw)
        print("🔈 Header:", header)

        sample_rate = header["sample_rate"]

        chunk_counter = 0

        print("🔊 Reproduciendo...\n")

        try:
            while True:
                chunk = await ws.recv()
                audio_tensor, sr = torchaudio.load(io.BytesIO(chunk))

                # Guardar en disco
                path = os.path.join(OUTPUT_DIR, f"chunk_{chunk_counter:02d}.wav")
                torchaudio.save(path, audio_tensor, sr)
                print(f"💾 Guardado: {path}")

                # Reproducir en hilo separado para evitar bloqueo
                threading.Thread(target=play_audio_tensor, args=(audio_tensor, sr)).start()

                chunk_counter += 1

        except websockets.exceptions.ConnectionClosed:
            print("✅ Conexión cerrada por el servidor.")


if __name__ == "__main__":
    asyncio.run(main())
