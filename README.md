# Jarvis Voice Assistant

A single-file Python voice assistant built as a tutorial-inspired learning project. It demonstrates speech recognition, text-to-speech, web shortcuts, screenshots, Wikipedia lookup, camera preview, and a few safe desktop actions.

## Features

- Voice input using your microphone
- Text-to-speech responses
- Open Google and YouTube
- Search Google or YouTube from a spoken command
- Read short Wikipedia summaries
- Show your public IP address
- Take screenshots
- Open a local webcam preview
- Tell the current time and date
- Lock the computer screen

## Project Structure

```text
jarvis-voice-assistant/
├── jarvis.py
└── README.md
```

## Requirements

Install Python 3.10 or newer.

Install the main packages:

```bash
pip install pyttsx3 SpeechRecognition pyautogui requests wikipedia opencv-python
```

For microphone support, you may also need PyAudio:

```bash
pip install PyAudio
```

If PyAudio fails on Windows, install it using a wheel or through a Python distribution that includes audio support.

## How to Run

```bash
python jarvis.py
```

Then try commands like:

```text
help
what time is it
open google
search google for python projects
search youtube for python voice assistant
wikipedia artificial intelligence
take screenshot
open camera
lock screen
exit
```

## Notes

This project is intended for learning and portfolio practice. It is inspired by common Python voice-assistant tutorials and rewritten as a clean single-file implementation with safer command handling.

The assistant may ask for microphone, camera, and screen-capture permissions depending on your operating system.
