
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
import skills.workflows

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
        if config.VOICE_OUTPUT:
            try:
                self.engine = pyttsx3.init()
                # Set voice
                voices = self.engine.getProperty('voices')
                if voices:
                    self.engine.setProperty('voice', voices[0].id) 
            except Exception:
                self.engine = None
                print("TTS Engine failed to initialize. Output will be text-only.")
        else:
            self.engine = None
            print("Voice Output is disabled in config.")

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
        if config.VOICE_OUTPUT and self.engine:
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
            self.recognizer.pause_threshold = 1.2  # Wait slightly longer for complex commands
            self.recognizer.energy_threshold = 350
            
            try:
                audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=15)
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
        
        # Voice Mode: REQUIRE wake word (or conversational trigger)
        if self.mic:
            # Expanded triggers so you don't ALWAYS have to say strict "RJ"
            wake_word_variants = [
                WAKE_WORD.lower(), "rj", "r j", "are jay", "archie", "rg", # Name variants
                "hey", "hi", "hello", "okay", "ok", # Greetings
                "can you", "could you", "please", "tell me" # Politeness
            ]
            
            triggered = False
            for trigger in wake_word_variants:
                if text.startswith(trigger): # Check if sentence STARTS with these
                    # Remove the trigger but keep the rest
                    # e.g. "Can you open browser" -> "open browser"
                    if trigger in text: 
                         cleaned_text = text.replace(trigger, "", 1).strip()
                    triggered = True
                    break
            
            # If strictly configured to ONLY use RJ, you can remove the list above.
            # But for natural conversation, this check is better:
            if not triggered and WAKE_WORD.lower() not in text:
                print(f"Ignored (No wake word): '{text}'")
                return
            
            # If wake word was in the middle of sentence (e.g. "Open google RJ")
            if not triggered and WAKE_WORD.lower() in text:
                 cleaned_text = text.replace(WAKE_WORD.lower(), "").strip()

        # Text Mode: Optional wake word

        # Text Mode: Optional wake word
        else:
            if WAKE_WORD in text:
                cleaned_text = text.split(WAKE_WORD, 1)[1].strip()
        
        if not cleaned_text:
            self.speak("Yes?")
            return

        # 1. Analyze intent (LLM or Regex Fallback)
        intent = self.llm.parse_intent(cleaned_text)
        
        # 2. Extract Response and Action
        verbal_response = intent.get("response")
        cmd_name = intent.get("command")
        args = intent.get("args", {})

        # Speak LLM's personality response first
        if verbal_response:
             self.speak(verbal_response)

        # 3. Handle Unknowns
        if not cmd_name or cmd_name == "unknown":
            if not verbal_response:
                self.speak("I'm not sure how to do that.")
            return

        # 4. Execute via Registry if it's not JUST a chat
        if cmd_name != "chat":
            # Global Permission Check
            if config.ALWAYS_ASK_PERMISSION:
                self.speak(f"Sir, I'm about to {cmd_name.replace('_', ' ')}. Is that permitted?")
                confirm = input(f"Allow {cmd_name}? (y/n): ").lower()
                if confirm != 'y':
                    self.speak("Cancelled, Sir.")
                    return

            result = registry.execute(cmd_name, **args)
            
            # Special Handling for Workflows
            if isinstance(result, dict) and result.get("is_workflow"):
                steps = result.get("steps", [])
                self.speak(f"Sir, I have retrieved the procedure. It involves {len(steps)} steps. Shall I proceed?")
                confirm = input("Proceed with workflow? (y/n): ").lower()
                if confirm == 'y':
                    self.speak("Executing procedure now.")
                    for i, step in enumerate(steps):
                        s_cmd = step.get("command")
                        s_args = step.get("args", {})
                        self.speak(f"Step {i+1}: {s_cmd.replace('_', ' ')}")
                        s_res = registry.execute(s_cmd, **s_args)
                        print(f"Step {i+1} Output: {s_res}")
                    self.speak("Procedure complete, Sir.")
                else:
                    self.speak("Workflow cancelled.")
                return

            # Special Handling for Information Retrieval
            if isinstance(result, dict) and result.get("is_info_retrieval"):
                link = result.get("first_link")
                query = result.get("query")
                context = ""
                if link:
                    self.speak(f"Fetching details from the web, Sir.")
                    context = registry.execute("get_page_text", url=link)
                else:
                    context = "No direct links found, but you can try to answer from your training data if you are sure."
                
                new_intent = self.llm.parse_intent(f"Based on this info, answer: {query}", context=context)
                new_response = new_intent.get("response")
                if new_response:
                    self.speak(new_response)
                return

            print(f"Action Output: {result}")
            
            # If the command returned something important (like time or diagnostics), 
            # and it wasn't already in the verbal response, speak it.
            if result and str(result) not in str(verbal_response):
                 self.speak(f"{result}")
        elif not verbal_response:
            # Fallback for chat if no 'response' field was provided
            result = registry.execute(cmd_name, **args)
            self.speak(result)

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
