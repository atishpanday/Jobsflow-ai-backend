from deepgram import (
    DeepgramClient,
    DeepgramClientOptions,
    LiveOptions,
    LiveTranscriptionEvents,
)
import threading


class DG_Client:
    def __init__(self, api_key):
        config = DeepgramClientOptions(options={"keepalive": "true"})
        self.deepgram = DeepgramClient(api_key, config)
        self.dg_connection = None
        self.connection_open = False
        self.audio_data = bytearray()
        self.transcription = ""
        self.lock = threading.Lock()

    def connect(self):
        self.dg_connection = self.deepgram.listen.live.v("1")
        options = LiveOptions(punctuate=True, interim_results=False, language="en-US")
        self.dg_connection.start(options)
        self.connection_open = True

        send_thread = threading.Thread(target=self.send_audio, daemon=True)
        receive_thread = threading.Thread(
            target=self.receive_transcription, daemon=True
        )
        send_thread.start()
        receive_thread.start()

    def add_audio(self, data: bytearray):
        if len(data) > 0:
            with self.lock:
                self.audio_data.extend(data)

    def send_audio(self):
        while self.connection_open:
            with self.lock:
                if len(self.audio_data) > 0:
                    self.dg_connection.send(self.audio_data)
                    self.audio_data = bytearray()

    def receive_transcription(self):
        outer_self = self

        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            with outer_self.lock:
                outer_self.transcription = sentence

        self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)

    def reset_transcription(self):
        self.transcription = ""
