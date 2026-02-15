#!/usr/bin/env python3
"""
Simple test script to verify No Cap Your Honor setup
"""

import asyncio
from workflow import create_initial_state, trial_graph

async def test_trial():
    """Run a simple test trial"""
    
    # Test claim
    test_content = "NASA confirmed that aliens exist on Mars last Tuesday."
    
    print("🏛️  Starting test trial...")
    print(f"📝 Test claim: {test_content}\n")
    
    # Create initial state
    state = create_initial_state(test_content, "text")
    print(f"✅ Created case: {state['case_id']}\n")
    
    # Run the workflow
    print("🔄 Running trial workflow...\n")
    
    try:
        async for event in trial_graph.astream(state):
            node_name = list(event.keys())[0]
            node_state = event[node_name]
            
            if node_name == "claim_extractor":
                claims = node_state.get('claims', [])
                print(f"📋 Extracted {len(claims)} claims")
                for i, claim in enumerate(claims, 1):
                    print(f"   {i}. {claim.get('text', 'N/A')}")
                print()
            
            elif node_name == "investigator":
                evidence_count = len(node_state.get('investigator_evidence', []))
                print(f"🔍 Gathered {evidence_count} pieces of evidence\n")
            
            elif node_name == "prosecutor_turn":
                round_num = node_state['current_round']
                conf = node_state.get('prosecutor_confidence', 0)
                print(f"⚖️  Round {round_num} - Prosecutor (Confidence: {conf}%)")
                transcript = node_state.get('trial_transcript', [])
                if transcript:
                    latest = transcript[-1]
                    print(f"   {latest['argument_text'][:150]}...\n")
            
            elif node_name == "defendant_turn":
                conf = node_state.get('defendant_confidence', 0)
                print(f"🛡️  Round {node_state['current_round']} - Defendant (Confidence: {conf}%)")
                transcript = node_state.get('trial_transcript', [])
                if transcript:
                    latest = transcript[-1]
                    print(f"   {latest['argument_text'][:150]}...\n")
            
            elif node_name == "verdict_aggregator":
                verdict = node_state.get('aggregated_verdict')
                if verdict:
                    print(f"\n🎯 VERDICT: {verdict['category']}")
                    print(f"📊 Score: {verdict['score']}/100")
                    print(f"📝 {verdict['summary']}\n")
            
            elif node_name == "cleanup":
                print("🧹 Cleaned up case data")
        
        print("\n✅ Test trial completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during trial: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("No Cap Your Honor - Test Script")
    print("=" * 60)
    print()
    
    asyncio.run(test_trial())
