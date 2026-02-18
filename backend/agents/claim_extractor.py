from config.state import TrialState
from utils.llm_clients import llm_clients
import json

CLAIM_EXTRACTOR_PROMPT = """You are a claim extraction specialist. Break down the following content into atomic, independently verifiable claims.

Content: {content}

For each claim, provide:
1. text: The exact claim statement
2. category: The type of claim (factual, opinion, prediction, etc.)
3. verifiability_score: 0-100 score on how verifiable this claim is
4. priority: 0-100 score on importance (based on potential harm if false and virality risk)

Return ONLY a JSON array of claims in this exact format:
[{{"text": "claim text", "category": "factual", "verifiability_score": 85, "priority": 90}}]
"""

async def claim_extractor(state: TrialState) -> TrialState:
    """Extract atomic claims from input content"""
    input_type = state["input_type"]
    raw_input = state["raw_input"]
    
    # Auto-detect URLs in text input
    if input_type == "text" and raw_input.strip().startswith(("http://", "https://")):
        print(f"[CLAIM EXTRACTOR] Auto-detected URL in text input, switching to URL mode")
        input_type = "url"
        state["input_type"] = "url"
    
    # Extract content based on input type
    if input_type == "url":
        print(f"[CLAIM EXTRACTOR] Processing URL: {raw_input}")
        # Extract content from URL using Gemini
        content = await llm_clients.analyze_url_content(
            raw_input,
            "Extract the main text content from this article or webpage. Return only the article text, including the headline and main body. Do not include navigation, ads, or other non-content elements."
        )
        print(f"[CLAIM EXTRACTOR] Extracted {len(content)} characters from URL")
        # Now extract claims from the content
        prompt = CLAIM_EXTRACTOR_PROMPT.format(content=content)
        response = await llm_clients.generate_gemini_pro(prompt, temperature=0.3)
    elif input_type == "video":
        print(f"[CLAIM EXTRACTOR] Processing video: {raw_input}")
        # Analyze video and extract claims directly
        # Store the video file for later reuse by investigator
        response, video_file = await llm_clients.analyze_video_with_file(
            raw_input,
            CLAIM_EXTRACTOR_PROMPT.format(
                content="Analyze this video comprehensively. Extract all factual claims made in the video, including both spoken statements and visual information presented."
            )
        )
        # Store video file in state for investigator to reuse
        state["uploaded_video_file"] = video_file
    elif input_type == "image":
        print(f"[CLAIM EXTRACTOR] Processing image: {raw_input}")
        # Analyze image and extract claims
        response = await llm_clients.analyze_image(
            raw_input,
            CLAIM_EXTRACTOR_PROMPT.format(
                content="Analyze this image comprehensively. Extract all factual claims visible in the image, including text, graphics, charts, and any other information presented."
            )
        )
    else:  # text, social_post
        print(f"[CLAIM EXTRACTOR] Processing {input_type} input")
        # Existing logic for text-based inputs
        prompt = CLAIM_EXTRACTOR_PROMPT.format(content=raw_input)
        response = await llm_clients.generate_gemini_pro(prompt, temperature=0.3)
    
    try:
        # Extract JSON from response
        json_start = response.find('[')
        json_end = response.rfind(']') + 1
        claims = json.loads(response[json_start:json_end])
        print(f"[CLAIM EXTRACTOR] Extracted {len(claims)} claims")
    except Exception as e:
        print(f"[CLAIM EXTRACTOR] Error parsing claims: {e}")
        claims = [{"text": raw_input[:200], "category": "factual", "verifiability_score": 50, "priority": 50}]
    
    state["claims"] = claims
    return state
