
import json
import os
import openai
import google.generativeai as genai
import config
from command_registry import registry

class LLMEngine:
    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.client = None
        self.model = ""

        # Auto-detect logic
        if self.provider == "auto":
            if config.KEYS["openai"]:
                self.provider = "openai"
                self.model = "gpt-3.5-turbo"
            elif config.KEYS["gemini"]:
                self.provider = "gemini"
                self.model = "gemini-pro"
            elif config.KEYS["anthropic"]:
                self.provider = "anthropic"
                self.model = "claude-3-opus-20240229"
            elif config.KEYS["groq"]:
                self.provider = "groq"
                self.model = "llama3-70b-8192"
            elif config.KEYS["openrouter"]:
                self.provider = "openrouter"
                self.model = "openai/gpt-3.5-turbo" # Default free/cheap model on OpenRouter
            else:
                self.provider = "local" # Default to local if no keys

        # Initialize Client based on Provider
        if self.provider == "openai":
            self.client = openai.OpenAI(api_key=config.KEYS["openai"])
            self.model = "gpt-3.5-turbo"
            
        elif self.provider == "gemini":
            genai.configure(api_key=config.KEYS["gemini"])
            self.model = genai.GenerativeModel('gemini-pro')
            
        elif self.provider == "anthropic":
            from anthropic import Anthropic
            self.client = Anthropic(api_key=config.KEYS["anthropic"])
            self.model = "claude-3-opus-20240229"

        elif self.provider == "groq":
            self.client = openai.OpenAI(
                base_url="https://api.groq.com/openai/v1",
                api_key=config.KEYS["groq"]
            )
            self.model = "llama3-70b-8192"

        elif self.provider == "openrouter":
            self.client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=config.KEYS["openrouter"]
            )
            # You can change this to any model supported by OpenRouter
            self.model = "openai/gpt-3.5-turbo"
            
        elif self.provider == "local" or self.provider == "ollama":
            self.client = openai.OpenAI(
                base_url=config.LOCAL_LLM_URL,
                api_key="lm-studio" # Dummy key
            )
            self.model = "local-model"

        print(f"LLM Engine Initialized: Provider={self.provider}, Model={self.model}")

    def parse_intent(self, user_input: str):
        """
        Analyzes user input and returns a structured command JSON.
        """
        # If no client initialized (e.g. no keys and local server down), use fallback
        if not self.client and self.provider != "gemini":
             return self._fallback_parser(user_input)

        system_prompt = f"""
        You are an AI Assistant. Map user intent to:
        {registry.list_commands()}
        
        Strict JSON Output: {{ "command": "cmd_name", "args": {{ "key": "value" }} }}
        If unclear/unsafe, use "unknown".
        """

        try:
            response_text = ""
            
            # --- OPENAI / GROQ / LOCAL / OPENROUTER ---
            if self.provider in ["openai", "groq", "local", "ollama", "openrouter"]:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_input}
                    ],
                    temperature=0.0
                )
                response_text = response.choices[0].message.content

            # --- GEMINI ---
            elif self.provider == "gemini":
                chat = self.model.start_chat(history=[])
                response = chat.send_message(system_prompt + "\nUSER: " + user_input)
                response_text = response.text

            # --- ANTHROPIC ---
            elif self.provider == "anthropic":
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=100,
                    system=system_prompt,
                    messages=[{"role": "user", "content": user_input}]
                )
                response_text = message.content[0].text

            # Cleanup JSON (sometimes models add markdown ```json ... ```)
            clean_json = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)

        except Exception as e:
            print(f"LLM Error ({self.provider}): {e}")
            return self._fallback_parser(user_input)

    def _fallback_parser(self, text: str):
        """Robust backup parser when LLM is offline."""
        text = text.lower().strip()
        print(f"Fallback Parser: Analying '{text}'")

        # --- BROWSER ---
        if "google" in text or "search" in text:
            query = text.replace("google", "").replace("search", "").strip()
            return {"command": "google_search", "args": {"query": query}}
        
        if "open youtube" in text:
             return {"command": "open_browser", "args": {"url": "https://youtube.com"}}

        if "close tab" in text or "close this tab" in text:
            return {"command": "close_tab", "args": {}}
        
        if "close browser" in text or "close window" in text:
            return {"command": "close_browser", "args": {}}

        # Generic "Open X" logic
        if "open" in text:
             target = text.split("open", 1)[1].strip()
             if "browser" in target or target == "":
                 url = "https://google.com"
             elif "http" in target or ".com" in target:
                 url = target 
             else:
                 # Try to guess URL if not explicit
                 url = f"https://{target.replace(' ', '')}.com"
             
             return {"command": "open_browser", "args": {"url": url}}

        # --- NOTES ---
        if "take note" in text or "write note" in text or "save this" in text:
            content = text.replace("take note", "").replace("write note", "").replace("save this", "").strip()
            return {"command": "take_note", "args": {"content": content}}
            
        if "read notes" in text or "last note" in text:
            return {"command": "read_notes", "args": {}}

        # --- SYSTEM ---
        if "time" in text or "date" in text:
            return {"command": "get_time", "args": {}}
        
        if "system" in text or "cpu" in text or "ram" in text:
            return {"command": "system_info", "args": {}}
            
        return {"command": "unknown", "args": {}}
