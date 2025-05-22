# #! ERROR DE CONEXION CON CONTEXTO LARGO, DEBUGEANDO LLEGADA DE TEXTO


# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from .settings import settings
# from .tts_engine import TTSEngine
# from .schemas import TextSegment, AudioHeader
# import asyncio
# import structlog
# import torchaudio
# import io
# from typing import Optional
# import sys
# sys.path.append('third_party/Matcha-TTS')

# log = structlog.get_logger()
# app = FastAPI()
# engine = TTSEngine()

# @app.websocket("/synthesize")
# async def synthesize(ws: WebSocket):
#     await ws.accept()
#     log.info("client_connected", client=str(ws.client))

#     await ws.send_text(AudioHeader(sample_rate=settings.SAMPLE_RATE).model_dump_json())

#     phrase_q: asyncio.Queue[Optional[str]] = asyncio.Queue(maxsize=10)

#     async def collect_phrases():
#         buffer = ''
#         chunk_count = 0
#         while True:
#             try:
#                 raw = await ws.receive_text()
#                 chunk_count += 1
#                 log.info("received_chunk", chunk_id=chunk_count, raw=raw)
#                 seg = TextSegment.model_validate_json(raw)
#                 log.info("parsed_segment", chunk_id=chunk_count, text=seg.text, done=seg.done)
#                 buffer += seg.text
#                 log.info("buffer_state", chunk_id=chunk_count, buffer=buffer)

#                 # Segmentar y enviar frases completas inmediatamente
#                 if any(buffer.endswith(p) for p in '.!?'):
#                     phrase = buffer.strip()
#                     log.info("phrase_segmented", phrase=phrase, word_count=len(phrase.split()))
#                     await phrase_q.put(phrase)
#                     buffer = ''

#                 if seg.done:
#                     if buffer.strip():  # Enviar cualquier frase pendiente
#                         phrase = buffer.strip()
#                         log.info("final_phrase_segmented", phrase=phrase, word_count=len(phrase.split()))
#                         await phrase_q.put(phrase)
#                     await phrase_q.put(None)  # Señal de fin
#                     log.info("sent_end_signal")
#                     break

#             except WebSocketDisconnect:
#                 log.warning("client_disconnected")
#                 break

#     async def tts_worker():
#         while True:
#             phrase = await phrase_q.get()
#             if phrase is None:  # Fin de la transmisión
#                 log.info("received_end_signal")
#                 break
#             log.info("processing_phrase", phrase=phrase, word_count=len(phrase.split()))
#             try:
#                 # Procesar cada frase inmediatamente
#                 for i, audio_tensor in enumerate(engine.stream([phrase], speaker_id="josh_v1")):
#                     log.info("audio_generated", chunk_id=i+1)
#                     pcm_bytes = io.BytesIO()
#                     torchaudio.save(pcm_bytes, audio_tensor.cpu(), settings.SAMPLE_RATE, format="wav")
#                     await ws.send_bytes(pcm_bytes.getvalue())
#                     log.info("audio_sent", chunk_id=i+1)
#             except Exception as e:
#                 log.error("tts_worker_error", error=str(e))

#     # Ejecutar ambas tareas en paralelo
#     collector_task = asyncio.create_task(collect_phrases())
#     # tts_task = asyncio.create_task(tts_worker())

#     try:
#         await asyncio.gather(collector_task)
#     except asyncio.CancelledError:
#         log.info("tasks_cancelled")
#     finally:
#         collector_task.cancel()
#         # tts_task.cancel()
#         log.info("tasks_cleaned_up")

#     # Mantener la conexión abierta para futuros mensajes (si aplica)
#     try:
#         await asyncio.Future()
#     except asyncio.CancelledError:
#         log.info("connection_cancelled")




#! ORGANIZACION DE FRASES, LUEGO CHUNK DE AUDIO


# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from .settings import settings
# from .tts_engine import TTSEngine
# from .schemas import TextSegment, AudioHeader
# import asyncio
# import structlog
# import torchaudio
# import io
# from typing import Optional
# import sys
# sys.path.append('third_party/Matcha-TTS')

# log = structlog.get_logger()
# app = FastAPI()
# engine = TTSEngine()

# @app.websocket("/synthesize")
# async def synthesize(ws: WebSocket):
#     await ws.accept()
#     log.info("client_connected", client=str(ws.client))

#     await ws.send_text(AudioHeader(sample_rate=settings.SAMPLE_RATE).model_dump_json())

#     phrase_q: asyncio.Queue[Optional[str]] = asyncio.Queue(maxsize=10)

#     async def collect_phrases():
#         buffer = ''
#         chunk_count = 0
#         while True:
#             try:
#                 raw = await ws.receive_text()
#                 chunk_count += 1
#                 log.info("received_chunk", chunk_id=chunk_count, raw=raw)
#                 seg = TextSegment.model_validate_json(raw)
#                 log.info("parsed_segment", chunk_id=chunk_count, text=seg.text, done=seg.done)
#                 buffer += seg.text
#                 log.info("buffer_state", chunk_id=chunk_count, buffer=buffer)

#                 if any(buffer.endswith(p) for p in '.!?'):
#                     phrase = buffer.strip()
#                     log.info("phrase_segmented", phrase=phrase)
#                     await phrase_q.put(phrase)
#                     buffer = ''

#                 if seg.done:
#                     if buffer.strip():
#                         phrase = buffer.strip()
#                         log.info("final_phrase_segmented", phrase=phrase)
#                         await phrase_q.put(phrase)
#                     await phrase_q.put(None)
#                     log.info("sent_end_signal")
#                     buffer = ''

#             except WebSocketDisconnect:
#                 log.warning("client_disconnected")
#                 break

#     def phrase_iter(loop: asyncio.AbstractEventLoop):
#         phrase_count = 0
#         while True:
#             phrase = asyncio.run_coroutine_threadsafe(phrase_q.get(), loop).result()
#             if phrase is None:
#                 log.info("phrase_iter_finished")
#                 break
#             phrase_count += 1
#             log.info("phrase_to_model", phrase_id=phrase_count, phrase=phrase)
#             yield phrase

#     def tts_worker(loop):
#         while True:
#             try:
#                 # Recolectar todas las frases en una lista
#                 phrases = list(phrase_iter(loop))
#                 if not phrases:
#                     log.info("no_phrases_to_process")
#                     continue

#                 # Loggear el texto completo
#                 full_text = ' '.join(phrases)
#                 log.info("full_text_to_model", text=full_text)

#                 # Generar audio con las frases recolectadas
#                 for i, audio_tensor in enumerate(engine.stream(phrases, speaker_id="josh_v1")):
#                     log.info("audio_generated", chunk_id=i+1)
#                     pcm_bytes = io.BytesIO()
#                     torchaudio.save(pcm_bytes, audio_tensor.cpu(), settings.SAMPLE_RATE, format="wav")
#                     asyncio.run_coroutine_threadsafe(ws.send_bytes(pcm_bytes.getvalue()), loop).result()
#                     log.info("audio_sent", chunk_id=i+1)
#                 log.info("batch_completed")

#                 # Reiniciar el modelo después de cada lote
#                 engine.reset()
#                 log.info("model_reset")

#             except Exception as e:
#                 log.error("tts_worker_error", error=str(e))

#     loop = asyncio.get_running_loop()
#     collector_task = asyncio.create_task(collect_phrases())

#     await loop.run_in_executor(None, tts_worker, loop)

#     try:
#         await asyncio.Future()
#     except asyncio.CancelledError:
#         log.info("connection_cancelled")
#     finally:
#         collector_task.cancel()
#         log.info("tasks_cleaned_up")





# ! FUNCIONAL


# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from .settings import settings
# from .tts_engine import TTSEngine
# from .schemas import TextSegment, AudioHeader
# import asyncio
# import structlog
# import torchaudio
# import io
# import time
# from typing import Optional
# import sys
# sys.path.append('third_party/Matcha-TTS')

# log = structlog.get_logger()
# app = FastAPI()
# engine = TTSEngine()

# @app.websocket("/synthesize")
# async def synthesize(ws: WebSocket):
#     await ws.accept()
#     log.info("client_connected", client=str(ws.client))

#     await ws.send_text(AudioHeader(sample_rate=settings.SAMPLE_RATE).model_dump_json())

#     phrase_q: asyncio.Queue[Optional[str]] = asyncio.Queue(maxsize=20)

#     # ------------------------------------------------------------------------
#     # Frase collector: recibe y segmenta texto del cliente
#     # ------------------------------------------------------------------------
#     async def collect_phrases():
#         buffer = ''
#         chunk_count = 0
#         while True:
#             try:
#                 raw = await ws.receive_text()
#                 chunk_count += 1
#                 log.info("received_chunk", chunk_id=chunk_count)

#                 seg = TextSegment.model_validate_json(raw)
#                 log.info("parsed_segment", chunk_id=chunk_count, text=seg.text, done=seg.done)

#                 buffer += seg.text
#                 log.info("buffer_state", chunk_id=chunk_count, buffer=buffer[:100] + '...', qsize=phrase_q.qsize())

#                 # Si termina en . ! ? -> frase lista
#                 if any(buffer.endswith(p) for p in '.!?'):
#                     phrase = buffer.strip()
#                     log.info("phrase_segmented", phrase=phrase, word_count=len(phrase.split()))
#                     await phrase_q.put(phrase)
#                     buffer = ''

#                 # Si es el último segmento
#                 if seg.done:
#                     if buffer.strip():
#                         phrase = buffer.strip()
#                         log.info("final_phrase_segmented", phrase=phrase, word_count=len(phrase.split()))
#                         await phrase_q.put(phrase)
#                     await phrase_q.put(None)
#                     log.info("sent_end_signal")
#                     break

#             except WebSocketDisconnect:
#                 log.warning("client_disconnected")
#                 break
#             except Exception as e:
#                 log.error("collector_error", error=str(e))
#                 break


#     # ------------------------------------------------------------------------
#     # TTS worker: consume frases y responde chunks de audio
#     # ------------------------------------------------------------------------
#     async def tts_worker():
#         phrase_id = 0
#         while True:
#             phrase = await phrase_q.get()
#             if phrase is None:
#                 log.info("received_end_signal")
#                 break

#             phrase_id += 1
#             log.info("tts_start", phrase_id=phrase_id, phrase=phrase)

#             try:
#                 start_time = time.time()
#                 for i, audio_tensor in enumerate(engine.stream([phrase], speaker_id="josh_v1")):
#                     gen_time = time.time() - start_time
#                     log.info("chunk_generated", phrase_id=phrase_id, chunk_id=i+1, generation_time=f"{gen_time:.2f}s")

#                     pcm_bytes = io.BytesIO()
#                     torchaudio.save(pcm_bytes, audio_tensor.cpu(), settings.SAMPLE_RATE, format="wav")

#                     send_start = time.time()
#                     await ws.send_bytes(pcm_bytes.getvalue())
#                     send_time = time.time() - send_start
#                     log.info("chunk_sent", phrase_id=phrase_id, chunk_id=i+1, send_time=f"{send_time:.2f}s")

#                     await asyncio.sleep(0.01)  # Control de presión mínima
#                     start_time = time.time()   # Reset timer para próximo chunk

#             except Exception as e:
#                 log.error("tts_worker_error", phrase_id=phrase_id, error=str(e))


#     # ------------------------------------------------------------------------
#     # Ejecutar ambas tareas
#     # ------------------------------------------------------------------------
#     collector_task = asyncio.create_task(collect_phrases())
#     tts_task = asyncio.create_task(tts_worker())

#     try:
#         await asyncio.gather(collector_task, tts_task)
#     except asyncio.CancelledError:
#         log.warning("tasks_cancelled")
#     finally:
#         collector_task.cancel()
#         tts_task.cancel()
#         log.info("tasks_cleaned_up")

#     try:
#         await asyncio.Future()  # Mantener conexión viva si se requiere
#     except asyncio.CancelledError:
#         log.info("connection_cancelled")






# ! FUNCIONAL SIN LOGS

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .settings import settings
from .tts_engine import TTSEngine
from .schemas import TextSegment, AudioHeader
import asyncio
import structlog
import torchaudio
import io
import time
from typing import Optional
import sys
sys.path.append('third_party/Matcha-TTS')

log = structlog.get_logger()
app = FastAPI()
engine = TTSEngine()

@app.websocket("/synthesize")
async def synthesize(ws: WebSocket):
    await ws.accept()

    await ws.send_text(AudioHeader(sample_rate=settings.SAMPLE_RATE).model_dump_json())

    phrase_q: asyncio.Queue[Optional[str]] = asyncio.Queue(maxsize=20)

    # Métricas
    total_phrases = 0
    total_chunks = 0
    full_text = ""

    # ------------------------------------------------------------------------
    async def collect_phrases():
        nonlocal full_text
        buffer = ''
        while True:
            try:
                raw = await ws.receive_text()
                seg = TextSegment.model_validate_json(raw)
                full_text += seg.text
                buffer += seg.text

                if any(buffer.endswith(p) for p in '.!?'):
                    await phrase_q.put(buffer.strip())
                    buffer = ''

                if seg.done:
                    if buffer.strip():
                        await phrase_q.put(buffer.strip())
                    await phrase_q.put(None)
                    break

            except WebSocketDisconnect:
                log.warning("client_disconnected")
                break
            except Exception as e:
                log.error("collector_error", error=str(e))
                break


    # ------------------------------------------------------------------------
    async def tts_worker():
        nonlocal total_phrases, total_chunks
        while True:
            phrase = await phrase_q.get()
            if phrase is None:
                break

            total_phrases += 1
            try:
                for audio_tensor in engine.stream([phrase], speaker_id="josh_v1"):
                    total_chunks += 1

                    pcm_bytes = io.BytesIO()
                    torchaudio.save(pcm_bytes, audio_tensor.cpu(), settings.SAMPLE_RATE, format="wav")

                    await ws.send_bytes(pcm_bytes.getvalue())
                    await asyncio.sleep(0.01)
            except Exception as e:
                log.error("tts_worker_error", error=str(e))
                break

    # ------------------------------------------------------------------------
    collector_task = asyncio.create_task(collect_phrases())
    tts_task = asyncio.create_task(tts_worker())

    try:
        await asyncio.gather(collector_task, tts_task)
    except asyncio.CancelledError:
        pass
    finally:
        collector_task.cancel()
        tts_task.cancel()

    # ------------------------------------------------------------------------
    resumen = full_text.strip()
    resumen_corto = resumen[:300] + ('...' if len(resumen) > 300 else '')
    log.info("✔️ Sesión completada", frases=total_phrases, chunks=total_chunks)
    log.info("texto_procesado", resumen=resumen_corto)

 
































# from fastapi import FastAPI, WebSocket, WebSocketDisconnect
# from starlette.websockets import WebSocketState  # Importar WebSocketState
# from .settings import settings
# from .tts_engine import TTSEngine
# from .schemas import TextSegment, AudioHeader
# import asyncio
# import structlog
# import torchaudio
# import io
# from typing import Optional
# import sys
# sys.path.append('third_party/Matcha-TTS')

# log = structlog.get_logger()
# app = FastAPI()
# engine = TTSEngine()

# @app.websocket("/synthesize")
# async def synthesize(ws: WebSocket):
#     await ws.accept()
#     log.info("client_connected", client=str(ws.client))

#     await ws.send_text(AudioHeader(sample_rate=settings.SAMPLE_RATE).model_dump_json())

#     phrase_q: asyncio.Queue[Optional[str]] = asyncio.Queue(maxsize=10)

#     async def collect_phrases():
#         buffer = ''
#         chunk_count = 0
#         while True:
#             try:
#                 raw = await ws.receive_text()
#                 chunk_count += 1
#                 log.info("received_chunk", chunk_id=chunk_count, raw=raw)
#                 seg = TextSegment.model_validate_json(raw)
#                 buffer += seg.text
#                 log.info("buffer_state", chunk_id=chunk_count, buffer=buffer)

#                 if any(buffer.endswith(p) for p in '.!?'):
#                     phrase = buffer.strip()
#                     log.info("phrase_segmented", phrase=phrase, word_count=len(phrase.split()))
#                     await phrase_q.put(phrase)
#                     buffer = ''

#                 if seg.done:
#                     if buffer.strip():
#                         phrase = buffer.strip()
#                         log.info("final_phrase_segmented", phrase=phrase, word_count=len(phrase.split()))
#                         await phrase_q.put(phrase)
#                     await phrase_q.put(None)
#                     log.info("sent_end_signal")
#                     break

#             except WebSocketDisconnect:
#                 log.warning("client_disconnected")
#                 break

#     async def tts_worker():
#         phrase_count = 0
#         while True:
#             log.info("tts_worker_waiting_for_phrase", phrase_count=phrase_count, queue_size=phrase_q.qsize())
            
#             phrase = await phrase_q.get()
#             phrase_count += 1
            
#             if phrase is None:
#                 log.info("tts_worker_received_end_signal")
#                 break
            
#             log.info("tts_worker_received_phrase", phrase_count=phrase_count, phrase=phrase, word_count=len(phrase.split()))
#             log.info("tts_worker_sending_to_model", phrase_count=phrase_count, phrase=phrase)
            
#             try:
#                 audio_chunks_generated = 0
#                 for i, audio_tensor in enumerate(engine.stream([phrase], speaker_id="josh_v1")):
#                     audio_chunks_generated += 1
#                     log.info("tts_worker_audio_generated", phrase_count=phrase_count, chunk_id=i+1, tensor_shape=str(audio_tensor.shape))
                    
#                     pcm_bytes = io.BytesIO()
#                     torchaudio.save(pcm_bytes, audio_tensor.cpu(), settings.SAMPLE_RATE, format="wav")
#                     audio_data = pcm_bytes.getvalue()
#                     log.info("tts_worker_audio_converted", phrase_count=phrase_count, chunk_id=i+1, audio_bytes_len=len(audio_data))
                    
#                     log.info("tts_worker_sending_audio_to_client", phrase_count=phrase_count, chunk_id=i+1)
#                     await ws.send_bytes(audio_data)
#                     log.info("tts_worker_audio_sent", phrase_count=phrase_count, chunk_id=i+1)
  
                
#                 log.info("tts_worker_phrase_processed", phrase_count=phrase_count, total_audio_chunks=audio_chunks_generated)
            
#             except Exception as e:
#                 log.error("tts_worker_error", phrase_count=phrase_count, error=str(e), exc_info=True)
#                 break

#     collector_task = asyncio.create_task(collect_phrases())
#     tts_task = asyncio.create_task(tts_worker())

#     try:
#         await collector_task
#         await tts_task
#     except asyncio.CancelledError:
#         log.info("tasks_cancelled")
#     finally:
#         collector_task.cancel()
#         tts_task.cancel()
#         log.info("tasks_cleaned_up")

#     try:
#         await asyncio.Future()
#     except asyncio.CancelledError:
#         log.info("connection_cancelled")























        