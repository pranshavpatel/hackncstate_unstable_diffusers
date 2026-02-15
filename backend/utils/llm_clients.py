from google import genai
from anthropic import Anthropic
from openai import OpenAI
from together import Together
from config.settings import Config
import asyncio
import time

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
    
    # async def generate_gemini_grounded(self, prompt: str) -> str:
    #     """Generate response using Gemini with Google Search grounding"""
    #     response = self.client.models.generate_content(
    #         model='gemini-2.0-flash',
    #         contents=prompt,
    #         config={
    #             'temperature': 0.3,
    #             'response_modalities': ['TEXT'],
    #         },
    #         tools=[{'google_search': {}}]  # Enable Google Search grounding
    #     )
    #     return response.text

    async def generate_gemini_flash(self, prompt: str, temperature: float = 0.7) -> str:
        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=prompt,
            config={'temperature': temperature}
        )
        return response.text
    
    async def generate_gemini_grounded(self, prompt: str) -> str:
        """Generate grounded response using Gemini with Google Search"""
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "temperature": 0.3,
                "tools": [{"google_search": {}}],
                "automatic_function_calling": {"disable": False}
            }
        )
        
        # # Print grounding metadata (search results)
        # print("\n" + "="*60)
        # print("GOOGLE SEARCH GROUNDING RESULTS")
        # print("="*60)
        
        # if hasattr(response, 'candidates') and response.candidates:
        #     for idx, candidate in enumerate(response.candidates):
        #         if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
        #             metadata = candidate.grounding_metadata
        #             print(f"\nCandidate {idx + 1}:")
        #             print(f"Grounding Metadata: {metadata}")
                    
        #             # Try to extract search entries if available
        #             if hasattr(metadata, 'search_entry_point'):
        #                 print(f"Search Entry Point: {metadata.search_entry_point}")
        #             if hasattr(metadata, 'grounding_chunks'):
        #                 print(f"Grounding Chunks: {metadata.grounding_chunks}")
        #             if hasattr(metadata, 'web_search_queries'):
        #                 print(f"Web Search Queries: {metadata.web_search_queries}")
        #         else:
        #             print(f"\nCandidate {idx + 1}: No grounding metadata found")
        # else:
        #     print("No candidates with grounding metadata found")
        
        # print("="*60 + "\n")
        
        if hasattr(response, "text") and response.text:
            return response.text
        
        if response.candidates:
            parts = response.candidates[0].content.parts
            return "".join(part.text for part in parts if hasattr(part, "text"))
        
        return ""
    
    async def analyze_url_content(self, url: str, prompt: str) -> str:
        """Analyze content from a URL using Gemini"""
        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[url, prompt],
            config={'temperature': 0.3}
        )
        return response.text
    
    async def analyze_video(self, video_file_path: str, prompt: str) -> str:
        """Analyze video content using Gemini"""
        # Upload video file to Gemini
        print(f"[VIDEO] Uploading video: {video_file_path}")
        video_file = self.client.files.upload(file=video_file_path)
        print(f"[VIDEO] Upload complete. File name: {video_file.name}")
        print(f"[VIDEO] Processing state: {video_file.state}")
        
        # Wait for processing
        while video_file.state == "PROCESSING":
            print("[VIDEO] Waiting for video processing...")
            await asyncio.sleep(2)
            video_file = self.client.files.get(name=video_file.name)
        
        if video_file.state == "FAILED":
            raise Exception(f"Video processing failed: {video_file.name}")
        
        print(f"[VIDEO] Processing complete. Generating content...")
        
        # Generate content from video
        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[video_file, prompt],
            config={'temperature': 0.3}
        )
        
        # Clean up uploaded file
        try:
            self.client.files.delete(name=video_file.name)
            print(f"[VIDEO] Cleaned up uploaded file: {video_file.name}")
        except:
            pass
        
        return response.text
    
    async def analyze_image(self, image_file_path: str, prompt: str) -> str:
        """Analyze image content using Gemini"""
        print(f"[IMAGE] Uploading image: {image_file_path}")
        
        # Upload image file to Gemini
        image_file = self.client.files.upload(file=image_file_path)
        print(f"[IMAGE] Upload complete. File name: {image_file.name}")
        
        # Generate content from image
        response = self.client.models.generate_content(
            model='gemini-2.0-flash',
            contents=[image_file, prompt],
            config={'temperature': 0.3}
        )
        
        # Clean up uploaded file
        try:
            self.client.files.delete(name=image_file.name)
            print(f"[IMAGE] Cleaned up uploaded file: {image_file.name}")
        except:
            pass
        
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
