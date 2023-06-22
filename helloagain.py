import os
import pyaudio
import wave
import io
import openai
import google.cloud.texttospeech as tts
import google.cloud.speech as stt
from pydub import AudioSegment
from pydub.playback import play


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\pc\\MYprojects\\HelloAgain\\helloagain-386707-b72ca861d6f6.json"

openai.api_key = "your openai api"

def record_voice_input():

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "voice_input.wav"

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    return WAVE_OUTPUT_FILENAME

def convert_voice_to_text(voice_input):

    client = stt.SpeechClient()

    with io.open(voice_input, "rb") as audio_file:
        content = audio_file.read()

    audio = stt.RecognitionAudio(content=content)
    config = stt.RecognitionConfig(
        encoding=stt.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        return result.alternatives[0].transcript

def get_gpt_response(text_input):

    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=text_input,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )

    return response.choices[0].text.strip()

def convert_text_to_speech(text_response):

    client = tts.TextToSpeechClient()

    input_text = tts.SynthesisInput(text=text_response)
    voice = tts.VoiceSelectionParams(
        language_code="en-US",
        ssml_gender=tts.SsmlVoiceGender.FEMALE,
    )
    audio_config = tts.AudioConfig(
        audio_encoding=tts.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)

    return "output.mp3"

def play_audio_response(audio_response):

    audio = AudioSegment.from_mp3(audio_response)
    play(audio)

def main():
    voice_input = record_voice_input()
    text_input = convert_voice_to_text(voice_input)
    gpt_response = get_gpt_response(text_input)
    audio_response = convert_text_to_speech(gpt_response)
    play_audio_response(audio_response)

if __name__ == "__main__":
    main()
