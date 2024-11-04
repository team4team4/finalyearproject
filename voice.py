import os
import wave
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import spacy

# Load Vosk model (make sure to download and specify the path to the model)
model = Model("./vosk-model-small-en-in-0.4/")  # Replace with your model path
recognizer = KaldiRecognizer(model, 16000)

nlp = spacy.load("en_core_web_sm")

# Define command templates
commands = {
    "open_file": "xdg-open {file_name}",
    "list_directory": "ls {directory}",
    "check_time": "date",
    "create_file": "touch {file_name}"
}

def listen_for_command():
    # Setup for microphone input
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Listening for command...")
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            text = json.loads(result).get("text", "")
            print(f"Recognized text: {text}")
            return text

    stream.stop_stream()
    stream.close()
    p.terminate()

def identify_intent_and_arguments(text):
    doc = nlp(text)
    intent = None
    args = {}

    if "open" in text:
        intent = "open_file"
        args["file_name"] = extract_entity(doc, "NOUN")  # Extracting file name
    elif "list" in text and "directory" in text:
        intent = "list_directory"
        args["directory"] = "."  # Default to current directory
    elif "time" in text:
        intent = "check_time"
    elif "create file" in text:
        intent = "create_file"
        args["file_name"] = extract_entity(doc, "NOUN")

    return intent, args

def extract_entity(doc, label):
    for token in doc:
        if token.pos_ == label:
            return token.text
    return None

def execute_command(intent, args):
    if intent in commands:
        command_template = commands[intent]
        command = command_template.format(**args)
        print(f"Executing: {command}")
        os.system(command)
    else:
        print("Command not recognized.")

# Main loop
while True:
    text = listen_for_command()  # Get text from Vosk
    intent, args = identify_intent_and_arguments(text)
    execute_command(intent, args)

