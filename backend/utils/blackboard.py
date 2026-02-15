import httpx
from typing import List, Dict
from config.settings import Config

class BlackboardClient:
    def __init__(self):
        self.api_key = Config.BLACKBOARD_API_KEY
        self.base_url = Config.BLACKBOARD_BASE_URL
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
        self.storage = {}
    
    async def create_collection(self, case_id: str):
        self.storage[case_id] = {}
        return {"status": "created"}
    
    async def delete_collection(self, case_id: str):
        if case_id in self.storage:
            del self.storage[case_id]
        return {"status": "deleted"}
    
    async def store_evidence(self, case_id: str, namespace: str, evidence: Dict):
        if case_id not in self.storage:
            self.storage[case_id] = {}
        if namespace not in self.storage[case_id]:
            self.storage[case_id][namespace] = []
        self.storage[case_id][namespace].append(evidence)
        return {"status": "stored"}
    
    async def query_namespace(self, case_id: str, namespace: str, query: str, top_k: int = 5) -> List[Dict]:
        if case_id in self.storage and namespace in self.storage[case_id]:
            return self.storage[case_id][namespace][:top_k]
        return []
    
    async def web_search(self, query: str, top_k: int = 5) -> List[Dict]:
        if not self.api_key or self.api_key.startswith('demo'):
            return [
                {"url": "https://example.com/source1", "title": "Relevant source", "snippet": "Mock search result for: " + query},
                {"url": "https://example.com/source2", "title": "Another source", "snippet": "Additional context"}
            ]
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.base_url}/search/web",
                    headers=self.headers,
                    json={"query": query, "top_k": top_k}
                )
                return response.json().get("results", [])
        except:
            return [
                {"url": "https://example.com/source1", "title": "Relevant source", "snippet": "Mock search result for: " + query}
            ]

blackboard = BlackboardClient()
