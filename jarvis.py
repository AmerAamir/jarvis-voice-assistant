"""Jarvis Voice Assistant

A single-file Python voice assistant built as a tutorial-inspired learning project.
It supports voice input, text-to-speech responses, web shortcuts, screenshots,
Wikipedia summaries, public IP lookup, and a small set of safe desktop actions.

Install the optional dependencies listed in README.md before running.
"""

from __future__ import annotations

import datetime as dt
import os
import platform
import subprocess
import sys
import time
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

try:
    import pyttsx3
except ImportError:  # pragma: no cover - handled at runtime
    pyttsx3 = None

try:
    import speech_recognition as sr
except ImportError:  # pragma: no cover - handled at runtime
    sr = None

try:
    import pyautogui
except ImportError:  # pragma: no cover - handled at runtime
    pyautogui = None

try:
    import requests
except ImportError:  # pragma: no cover - handled at runtime
    requests = None

try:
    import wikipedia
except ImportError:  # pragma: no cover - handled at runtime
    wikipedia = None

try:
    import cv2
except ImportError:  # pragma: no cover - handled at runtime
    cv2 = None


APP_NAME = "Jarvis"
SCREENSHOT_DIR = Path.home() / "Pictures" / "JarvisScreenshots"


@dataclass(frozen=True)
class Command:
    """Maps a command phrase to a handler."""

    keywords: tuple[str, ...]
    handler: Callable[[str], None]
    description: str


class JarvisAssistant:
    """Small voice assistant with safe, easy-to-read command handlers."""

    def __init__(self) -> None:
        self.engine = self._create_tts_engine()
        self.recognizer = sr.Recognizer() if sr else None
        self.commands = self._build_commands()
        self.running = True

    def _create_tts_engine(self):
        if pyttsx3 is None:
            return None

        engine = pyttsx3.init()
        engine.setProperty("rate", 175)
        engine.setProperty("volume", 1.0)
        return engine

    def speak(self, message: str) -> None:
        """Speak and print a response."""
        print(f"{APP_NAME}: {message}")
        if self.engine is not None:
            self.engine.say(message)
            self.engine.runAndWait()

    def listen(self) -> str:
        """Listen for a command using the default microphone."""
        if sr is None or self.recognizer is None:
            self.speak("Speech recognition is not installed. Type your command instead.")
            return input("You: ").strip().lower()

        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.pause_threshold = 1
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = self.recognizer.listen(source)

        try:
            command = self.recognizer.recognize_google(audio, language="en-US")
            command = command.lower().strip()
            print(f"You: {command}")
            return command
        except sr.UnknownValueError:
            self.speak("Sorry, I could not understand that.")
        except sr.RequestError:
            self.speak("Speech recognition service is unavailable right now.")

        return ""

    def _build_commands(self) -> list[Command]:
        return [
            Command(("help", "what can you do"), self.show_help, "Show available commands"),
            Command(("time",), self.tell_time, "Tell the current time"),
            Command(("date", "today"), self.tell_date, "Tell today's date"),
            Command(("open google",), self.open_google, "Open Google"),
            Command(("open youtube",), self.open_youtube, "Open YouTube"),
            Command(("search google for", "google search"), self.search_google, "Search Google"),
            Command(("search youtube for", "youtube search"), self.search_youtube, "Search YouTube"),
            Command(("wikipedia", "who is", "what is"), self.search_wikipedia, "Read a short Wikipedia summary"),
            Command(("ip address", "public ip"), self.public_ip, "Show public IP address"),
            Command(("screenshot", "take screenshot"), self.take_screenshot, "Take a screenshot"),
            Command(("camera", "webcam"), self.open_camera_preview, "Open a local webcam preview"),
            Command(("lock computer", "lock screen"), self.lock_screen, "Lock the screen"),
            Command(("exit", "quit", "stop", "goodbye"), self.stop, "Exit the assistant"),
        ]

    def greet(self) -> None:
        hour = dt.datetime.now().hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 18:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"

        self.speak(f"{greeting}. I am {APP_NAME}. Say help to hear what I can do.")

    def run(self) -> None:
        self.greet()
        while self.running:
            command = self.listen()
            if command:
                self.handle(command)

    def handle(self, command: str) -> None:
        for item in self.commands:
            if any(keyword in command for keyword in item.keywords):
                item.handler(command)
                return

        self.speak("I do not know that command yet. Say help for examples.")

    def show_help(self, _: str = "") -> None:
        lines = [f"{description}: {keywords[0]}" for keywords, _, description in self.commands]
        self.speak("Here are some commands I understand.")
        print("\nAvailable commands:")
        for line in lines:
            print(f"- {line}")

    def tell_time(self, _: str = "") -> None:
        now = dt.datetime.now().strftime("%I:%M %p")
        self.speak(f"The time is {now}.")

    def tell_date(self, _: str = "") -> None:
        today = dt.datetime.now().strftime("%A, %B %d, %Y")
        self.speak(f"Today is {today}.")

    def open_google(self, _: str = "") -> None:
        webbrowser.open("https://www.google.com")
        self.speak("Opening Google.")

    def open_youtube(self, _: str = "") -> None:
        webbrowser.open("https://www.youtube.com")
        self.speak("Opening YouTube.")

    def _query_after_phrase(self, command: str, phrases: tuple[str, ...]) -> str:
        for phrase in phrases:
            if phrase in command:
                return command.split(phrase, 1)[1].strip()
        return ""

    def search_google(self, command: str) -> None:
        query = self._query_after_phrase(command, ("search google for", "google search"))
        if not query:
            self.speak("What should I search for?")
            query = input("Google search: ").strip()

        if query:
            webbrowser.open(f"https://www.google.com/search?q={query.replace(' ', '+')}")
            self.speak(f"Searching Google for {query}.")

    def search_youtube(self, command: str) -> None:
        query = self._query_after_phrase(command, ("search youtube for", "youtube search"))
        if not query:
            self.speak("What should I search on YouTube?")
            query = input("YouTube search: ").strip()

        if query:
            webbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}")
            self.speak(f"Searching YouTube for {query}.")

    def search_wikipedia(self, command: str) -> None:
        if wikipedia is None:
            self.speak("Wikipedia support is not installed. Install the wikipedia package first.")
            return

        query = command
        for phrase in ("wikipedia", "who is", "what is"):
            query = query.replace(phrase, "")
        query = query.strip()

        if not query:
            self.speak("What topic should I look up?")
            query = input("Wikipedia topic: ").strip()

        if not query:
            return

        try:
            summary = wikipedia.summary(query, sentences=2, auto_suggest=False)
            self.speak(summary)
        except wikipedia.DisambiguationError as exc:
            options = ", ".join(exc.options[:5])
            self.speak(f"That topic is ambiguous. Try one of these: {options}.")
        except wikipedia.PageError:
            self.speak("I could not find a Wikipedia page for that topic.")

    def public_ip(self, _: str = "") -> None:
        if requests is None:
            self.speak("Requests is not installed, so I cannot check the public IP address.")
            return

        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            response.raise_for_status()
            self.speak(f"Your public IP address is {response.text}.")
        except requests.RequestException:
            self.speak("I could not fetch the public IP address.")

    def take_screenshot(self, _: str = "") -> None:
        if pyautogui is None:
            self.speak("PyAutoGUI is not installed, so I cannot take a screenshot.")
            return

        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        filename = dt.datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
        path = SCREENSHOT_DIR / filename
        image = pyautogui.screenshot()
        image.save(path)
        self.speak(f"Screenshot saved to {path}.")

    def open_camera_preview(self, _: str = "") -> None:
        if cv2 is None:
            self.speak("OpenCV is not installed, so I cannot open the camera preview.")
            return

        self.speak("Opening camera preview. Press Q to close it.")
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            self.speak("I could not access the camera.")
            return

        while True:
            ok, frame = camera.read()
            if not ok:
                break
            cv2.imshow("Jarvis Camera Preview", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        camera.release()
        cv2.destroyAllWindows()
        self.speak("Camera preview closed.")

    def lock_screen(self, _: str = "") -> None:
        system = platform.system().lower()
        self.speak("Locking the screen.")

        try:
            if system == "windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], check=False)
            elif system == "darwin":
                subprocess.run(
                    ["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"],
                    check=False,
                )
            elif system == "linux":
                subprocess.run(["loginctl", "lock-session"], check=False)
            else:
                self.speak("Screen locking is not supported on this operating system.")
        except OSError:
            self.speak("I could not lock the screen on this system.")

    def stop(self, _: str = "") -> None:
        self.speak("Goodbye.")
        self.running = False


def check_environment() -> None:
    """Print friendly setup notes without stopping the app."""
    missing = []
    for name, module in {
        "pyttsx3": pyttsx3,
        "SpeechRecognition": sr,
        "pyautogui": pyautogui,
        "requests": requests,
        "wikipedia": wikipedia,
        "opencv-python": cv2,
    }.items():
        if module is None:
            missing.append(name)

    if missing:
        print("Missing optional packages:")
        print("  " + " ".join(missing))
        print("Install them with:")
        print("  pip install pyttsx3 SpeechRecognition pyautogui requests wikipedia opencv-python")
        print("For microphone support, PyAudio may also be required.\n")


def main() -> None:
    check_environment()
    assistant = JarvisAssistant()

    try:
        assistant.run()
    except KeyboardInterrupt:
        print("\nExiting Jarvis.")
        sys.exit(0)


if __name__ == "__main__":
    main()
