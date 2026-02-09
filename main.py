
import os
import sys
import threading
import speech_recognition as sr
import pyttsx3
import config
from config import WAKE_WORD, MICROPHONE_INDEX, REMOTE_CONFIG
from command_registry import registry
from llm_engine import LLMEngine
import skills.browser
import skills.system
import skills.files
import skills.media
import skills.input

import logging
import skills.notes # Ensure notes skill is registered

# Setup Logging
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/debug.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Remote Integrations
try:
    from integrations.discord_bot import run_discord
    from integrations.telegram_bot import run_telegram
except ImportError:
    pass

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
            # Use specific microphone index if configured:
            mic_index = getattr(config, 'MICROPHONE_INDEX', None) 
            self.mic = sr.Microphone(device_index=mic_index)
        except Exception as e:
            print(f"Microphone init failed: {e}. Switching to text mode.")

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
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.recognizer.pause_threshold = 1.0  # Wait 1s of silence before ending
            self.recognizer.energy_threshold = 300  # Lower sensitivity (default ~300-400)
            
            try:
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"Heard: '{text}'") # Debug print
                    return text.lower()
                except sr.UnknownValueError:
                    # print("...") # Ignore unrecognizable sounds
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
            # Common mishearings for "RJ"
            wake_word_variants = [WAKE_WORD.lower(), "are jay", "r j", "rg", "archie", "rj"]
            
            triggered = False
            for trigger in wake_word_variants:
                if trigger in text:
                    cleaned_text = text.split(trigger, 1)[1].strip()
                    triggered = True
                    break
            
            if not triggered:
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

def select_provider():
    """Forces user to select an AI provider at startup."""
    print("\n" + "="*30)
    print("   AI PROVIDER SELECTION")
    print("="*30)
    print("[1] OpenAI")
    print("[2] Gemini")
    print("[3] Anthropic")
    print("[4] Groq")
    print("[5] OpenRouter")
    print("[6] Local (Ollama)")
    print("[Enter] Auto-Detect (Default)")
    
    choice = input("\nSelect Provider (1-6): ").strip()
    
    mapping = {
        "1": "openai",
        "2": "gemini",
        "3": "anthropic",
        "4": "groq",
        "5": "openrouter",
        "6": "local"
    }
    
    provider = mapping.get(choice, "auto")
    
    # Override config in memory
    config.LLM_PROVIDER = provider
    print(f"Selected: {provider.upper()}\n")

if __name__ == "__main__":
    select_provider()

    # Start Remote Listeners in Background Threads
    if REMOTE_CONFIG.get("discord_token"):
        threading.Thread(target=run_discord, daemon=True).start()
        
    if REMOTE_CONFIG.get("telegram_token"):
        # Telegram usually needs to run in main thread or asyncio loop, 
        # but for simple polling, threading often works.
        threading.Thread(target=run_telegram, daemon=True).start()

    assistant = AI_Assistant()
    assistant.run()
