
import json
import os
import openai
from config import LLM_API_KEY, LLM_PROVIDER, LLM_BASE_URL
from command_registry import registry

class LLMEngine:
    def __init__(self):
        self.api_key = LLM_API_KEY
        self.client = None
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=LLM_BASE_URL)

    def parse_intent(self, user_input: str):
        """
        Analyzes user input and returns a structured command JSON.
        """
        if not self.client:
            return self._fallback_parser(user_input)

        system_prompt = f"""
        You are the brain of a local AI assistant. 
        Your ONLY job is to map user intent to one of the following commands:
        {registry.list_commands()}
        
        Output MUST be valid JSON with this format:
        {{
            "command": "command_name",
            "args": {{ "arg_name": "value" }}
        }}
        
        If the intent is unclear or unsafe, return:
        {{ "command": "unknown", "args": {{}} }}
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.0
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"LLM Error: {e}")
            return self._fallback_parser(user_input)

    def _fallback_parser(self, text: str):
        """Simple keyword matching for testing without API keys."""
        text = text.lower()
        if "google" in text:
            return {"command": "google_search", "args": {"query": text.replace("google", "").strip()}}
        if "browser" in text or "open" in text:
             return {"command": "open_browser", "args": {"url": "https://google.com"}}
        if "time" in text:
            return {"command": "get_time", "args": {}}
        if "system" in text:
            return {"command": "system_info", "args": {}}
        return {"command": "unknown", "args": {}}
