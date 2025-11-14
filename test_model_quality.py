"""
Quick Model Quality Test
Compare GPT-2-large vs Llama-3.2-1B for story coherence
"""

from adaptive_story_engine_enhanced import AdaptiveStoryEngine
import time

def test_model_quality(model_name: str):
    """Test story generation quality"""
    print(f"\n{'='*70}")
    print(f"Testing: {model_name}")
    print(f"{'='*70}\n")
    
    start_time = time.time()
    
    # Initialize engine
    print("Loading model...")
    engine = AdaptiveStoryEngine(
        model_name=model_name,
        use_enhanced_prompts=True
    )
    
    load_time = time.time() - start_time
    print(f"✓ Model loaded in {load_time:.1f} seconds\n")
    
    # Start story
    print("📖 Starting mystery story...\n")
    opening = engine.start_story(genre="mystery")
    print(f"OPENING:\n{opening}\n")
    
    # Test 3 user actions for coherence
    actions = [
        "I examine the letter closely for any hidden details",
        "I call my partner at the precinct to check missing persons reports",
        "I drive to the lighthouse mentioned in the message"
    ]
    
    for i, action in enumerate(actions, 1):
        print(f"\n{'─'*70}")
        print(f"ACTION {i}: {action}")
        print(f"{'─'*70}\n")
        
        gen_start = time.time()
        status, continuation = engine.process_user_action(action)
        gen_time = time.time() - gen_start
        
        print(f"RESPONSE ({gen_time:.1f}s):\n{continuation}\n")
    
    # Get final summary
    print(f"\n{'='*70}")
    print("STORY SUMMARY:")
    print(f"{'='*70}\n")
    print(engine.get_story_summary())
    
    total_time = time.time() - start_time
    print(f"\n⏱️  Total test time: {total_time:.1f} seconds")
    print(f"📊 Character coherence: {len(engine.characters)} characters tracked")
    print(f"🎭 Player archetype: {engine.player_profile.get_archetype()}")

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                   STORY COHERENCE TEST                          ║
║                                                                  ║
║  This will test two models side-by-side:                        ║
║  1. gpt2-large (your current model)                             ║
║  2. meta-llama/Llama-3.2-1B-Instruct (recommended upgrade)      ║
║                                                                  ║
║  First time running Llama will download ~2GB model              ║
║  (one-time, takes 5-10 minutes)                                 ║
╚══════════════════════════════════════════════════════════════════╝
    """)
    
    choice = input("Test which model? [1=gpt2-large, 2=Llama-3.2-1B, 3=both]: ").strip()
    
    if choice == "1":
        test_model_quality("gpt2-large")
    elif choice == "2":
        test_model_quality("meta-llama/Llama-3.2-1B-Instruct")
    elif choice == "3":
        print("\n🔄 Testing GPT-2-Large first...\n")
        test_model_quality("gpt2-large")
        
        print("\n\n")
        input("Press Enter to test Llama-3.2-1B (will download ~2GB if first time)...")
        
        print("\n🔄 Testing Llama-3.2-1B-Instruct...\n")
        test_model_quality("meta-llama/Llama-3.2-1B-Instruct")
        
        print("""
        
╔══════════════════════════════════════════════════════════════════╗
║                        COMPARISON COMPLETE                       ║
║                                                                  ║
║  Look for these quality indicators:                             ║
║  ✓ Consistent character names across responses                  ║
║  ✓ Location continuity (lighthouse stays lighthouse)            ║
║  ✓ Plot advancement (not just repeating same info)              ║
║  ✓ Logical cause-and-effect (actions have consequences)         ║
║  ✓ Rich sensory details (not generic descriptions)              ║
║                                                                  ║
║  Llama-3.2-1B should show significant improvement!              ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    else:
        print("Invalid choice. Run again with 1, 2, or 3.")
