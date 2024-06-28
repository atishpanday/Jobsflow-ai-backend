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
        deepgram = DeepgramClient(api_key, config)
        self.dg_connection = deepgram.listen.live.v("1")
        self.connection_open = False
        self.audio_data = bytearray()

    def connect(self):
        options = LiveOptions(punctuate=True, interim_results=False, language="en-US")
        self.dg_connection.start(options)
        self.connection_open = True
        send_thread = threading.Thread(target=self.send_audio)
        receive_thread = threading.Thread(target=self.receive_transcriptions)
        send_thread.start()
        receive_thread.start()
        send_thread.join()
        receive_thread.join()

    def add_audio(self, data: bytearray):
        if len(data) > 0:
            self.audio_data.extend(data)

    def send_audio(self):
        while self.connection_open:
            if len(self.audio_data) > 0:
                self.dg_connection.send(self.audio_data)
                self.audio_data = bytearray()

    def receive_transcriptions(self):
        def on_message(self, result, **kwargs):
            sentence = result.channel.alternatives[0].transcript
            if len(sentence) == 0:
                return
            print(f"Transcription: {sentence}")

        while self.connection_open:
            self.dg_connection.on(LiveTranscriptionEvents.Transcript, on_message)
