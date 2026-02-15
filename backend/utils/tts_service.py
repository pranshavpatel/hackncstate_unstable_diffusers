import os
import hashlib
import httpx
from pathlib import Path
from config.settings import Config

class TTSService:
    """ElevenLabs Text-to-Speech service with caching to avoid redundant API calls"""
    
    def __init__(self):
        self.api_key = Config.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        self.cache_dir = Path("/tmp/unreliable_narrator_tts_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Voice IDs for prosecutor and defendant (using ElevenLabs premade voices)
        # These are professional-sounding voices from the ElevenLabs library
        self.voices = {
            "prosecutor": "pNInz6obpgDQGcFmaJgB",  # Adam - deep, authoritative male voice
            "defendant": "EXAVITQu4vr4xnSDxMaL"   # Bella - clear, confident female voice
        }
        
    def _get_cache_key(self, text: str, agent: str) -> str:
        """Generate cache key from text and agent"""
        content = f"{agent}:{text}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.mp3"
    
    async def generate_speech(self, text: str, agent: str) -> str:
        """
        Generate speech using ElevenLabs API with caching.
        Returns the file path to the audio file.
        Only generates for prosecutor and defendant.
        """
        # Only process for prosecutor and defendant
        if agent not in ["prosecutor", "defendant"]:
            return None
            
        # Check cache first
        cache_key = self._get_cache_key(text, agent)
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            print(f"[TTS] Using cached audio for {agent}: {cache_key}")
            return str(cache_path)
        
        # Generate new audio
        print(f"[TTS] Generating new audio for {agent}: {text[:50]}...")
        
        voice_id = self.voices.get(agent)
        if not voice_id:
            print(f"[TTS] No voice configured for agent: {agent}")
            return None
        
        url = f"{self.base_url}/text-to-speech/{voice_id}"
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "model_id": "eleven_flash_v2_5",  # Fast, low-cost model
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=data, headers=headers)
                response.raise_for_status()
                
                # Save to cache
                with open(cache_path, "wb") as f:
                    f.write(response.content)
                
                print(f"[TTS] Audio generated and cached: {cache_key}")
                return str(cache_path)
                
        except Exception as e:
            print(f"[TTS] Error generating speech: {e}")
            return None
    
    def get_audio_url(self, file_path: str, case_id: str) -> str:
        """Convert file path to URL that frontend can access"""
        if not file_path:
            return None
        
        # Extract filename from path
        filename = Path(file_path).name
        # Return URL that will be served by the backend
        return f"/api/trial/{case_id}/audio/{filename}"


# Singleton instance
tts_service = TTSService()
