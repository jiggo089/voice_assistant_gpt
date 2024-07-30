
from openai import OpenAI
import pyaudio
import wave
from dotenv import load_dotenv
import os
import warnings
# Ignore DeprecationWarning
warnings.filterwarnings("ignore", category=DeprecationWarning)


load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

client = OpenAI(api_key=api_key)


# Function to record audio from the microphone
def record_audio(filename, duration=5):
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 44100  # Record at 44100 samples per second

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print("Recording...")

    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    for _ in range(0, int(fs / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print("Recording complete")

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()


# Function to transcribe audio using Whisper API
def transcribe_audio(filename):
    with open(filename, "rb") as audio_file:
        try:
            transcription = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
            )
            # Assuming the response object has an attribute `text`
            return transcription.text
        except Exception as e:
            print(f"An error occurred: {e}")
            return None


# Record and transcribe audio
audio_filename = "recorded_audio.wav"
record_audio(audio_filename)
transcribed_text = transcribe_audio(audio_filename)
print(f"Transcribed Text: {transcribed_text}")

# Create an assistant
assistant = client.beta.assistants.create(
    name="Chad",
    instructions="You are a personal voice assistant. Talk to people.",
    tools=[{"type": "code_interpreter"}],
    model="gpt-4",
)

# Create a thread
thread = client.beta.threads.create()

# Send the transcribed text as a message to the assistant
message = client.beta.threads.messages.create(
    thread_id=thread.id,
    role="user",
    content=transcribed_text
)

# Define the event handler class
from typing_extensions import override
from openai import AssistantEventHandler


class EventHandler(AssistantEventHandler):
    @override
    def on_text_created(self, text) -> None:
        print(f"\nassistant > ", end="", flush=True)

    @override
    def on_text_completed(self, text):
        print(text)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == 'code_interpreter':
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)


# Stream the assistant's response
with client.beta.threads.runs.stream(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Be creative.",
        event_handler=EventHandler(),
) as stream:
    for event in stream:
        if (event.event == "thread.message.completed"):
            response = client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=event.data.content[0].text.value,
            )
            response.stream_to_file("output.mp3")

    stream.until_done()
