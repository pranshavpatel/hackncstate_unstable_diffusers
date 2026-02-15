from google import genai
from anthropic import Anthropic
from openai import OpenAI
from together import Together
from config.settings import Config

class LLMClients:
    def __init__(self):
        self.client = genai.Client(api_key=Config.GOOGLE_API_KEY)
        self.anthropic = Anthropic(api_key=Config.ANTHROPIC_API_KEY) if Config.ANTHROPIC_API_KEY else None
        self.openai = OpenAI(api_key=Config.OPENAI_API_KEY) if Config.OPENAI_API_KEY else None
        self.together = Together(api_key=Config.TOGETHER_API_KEY) if Config.TOGETHER_API_KEY else None
    
    async def generate_gemini_pro(self, prompt: str, temperature: float = 0.7) -> str:
        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={'temperature': temperature}
        )
        return response.text
    
    async def generate_gemini_flash(self, prompt: str, temperature: float = 0.7) -> str:
        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={'temperature': temperature}
        )
        return response.text
    
    async def generate_claude(self, prompt: str, temperature: float = 0.7) -> str:
        if not self.anthropic:
            return "Claude API not configured"
        message = self.anthropic.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            temperature=temperature,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text
    
    async def generate_gpt4(self, prompt: str, temperature: float = 0.7) -> str:
        if not self.openai:
            return "OpenAI API not configured"
        response = self.openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content
    
    async def generate_llama(self, prompt: str, temperature: float = 0.7) -> str:
        if not self.together:
            return "Together API not configured"
        response = self.together.chat.completions.create(
            model="meta-llama/Llama-3-70b-chat-hf",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature
        )
        return response.choices[0].message.content

llm_clients = LLMClients()
