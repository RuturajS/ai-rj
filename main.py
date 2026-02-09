
import os
import sys
import time
import json
import threading
import speech_recognition as sr
import pyttsx3
from config import WAKE_WORD
from command_registry import registry
from llm_engine import LLMEngine

# Import skills to register commands
import skills.browser
import skills.system
import skills.files
import skills.media
import skills.input

class AI_Assistant:
    def __init__(self):
        try:
            self.engine = pyttsx3.init()
            # Set voice
            voices = self.engine.getProperty('voices')
            if voices:
                self.engine.setProperty('voice', voices[0].id) 
        except Exception:
            self.engine = None
            print("TTS Engine failed to initialize. Output will be text-only.")

        self.recognizer = sr.Recognizer()
        self.mic = None
        try:
            self.mic = sr.Microphone()
        except Exception:
            print("Microphone not found. Switching to text mode.")

        self.llm = LLMEngine()
        self.running = True

    def speak(self, text):
        print(f"AI: {text}")
        if self.engine:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass

    def listen(self):
        if not self.mic:
            return input("Type command: ")
        
        with self.mic as source:
            print(f"\nListening (Say '{WAKE_WORD}'...)...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"Heard: {text}")
                    return text.lower()
                except sr.UnknownValueError:
                    return None
            except sr.WaitTimeoutError:
                return None
            except Exception as e:
                print(f"Error listening: {e}")
                return None

    def execute_command(self, text):
        """Processes the command logic."""
        # print(f"Debug: Processing '{text}'")
        
        cleaned_text = text
        
        # Voice Mode: REQUIRE wake word
        if self.mic:
            if WAKE_WORD in text:
                cleaned_text = text.split(WAKE_WORD, 1)[1].strip()
            else:
                # Ignore input without wake word
                return

        # Text Mode: Optional wake word
        else:
            if WAKE_WORD in text:
                cleaned_text = text.split(WAKE_WORD, 1)[1].strip()
        
        if not cleaned_text:
            self.speak("Yes?")
            return

        # 1. Analyze intent (LLM or Regex Fallback)
        intent = self.llm.parse_intent(cleaned_text)
        
        # 2. Extract Action
        cmd_name = intent.get("command")
        args = intent.get("args", {})

        # 3. Handle Unknowns
        if not cmd_name or cmd_name == "unknown":
            self.speak("I'm not sure how to do that.")
            return

        # 4. Execute via Registry
        self.speak(f"Executing {cmd_name}...")
        result = registry.execute(cmd_name, **args)
        
        # 5. Report Result
        # print(f"Result: {result}")
        self.speak(str(result))

    def run(self):
        self.speak("System online.")
        try:
            while self.running:
                text = self.listen()
                if text:
                    if "stop listening" in text or "exit" in text:
                        self.speak("Shutting down.")
                        self.running = False
                        break
                    
                    self.execute_command(text)
                    
        except KeyboardInterrupt:
            self.running = False
            print("\nStopping...")

if __name__ == "__main__":
    assistant = AI_Assistant()
    assistant.run()
