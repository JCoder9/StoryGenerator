"""
Example Usage and Test Cases for Adaptive Story Engine

This demonstrates how the engine handles different types of user inputs,
including normal actions, dark choices, and absurd decisions.
"""

from adaptive_story_engine import AdaptiveStoryEngine


def example_normal_story():
    """Example of a normal story progression"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Normal Story Flow")
    print("="*70 + "\n")
    
    engine = AdaptiveStoryEngine(model_name='distilgpt2')
    
    # Custom starting scenario
    initial = engine.start_story(
        "It was a nice day. John's friend Michael came to say hello."
    )
    print("📖 Initial Story:")
    print(initial)
    print()
    
    # User makes a normal choice
    print("User action: 'John invites Michael inside for coffee'\n")
    status, continuation = engine.process_user_action(
        "John invites Michael inside for coffee"
    )
    print(f"Status: {status}")
    print(f"📖 Story continues:\n{continuation}\n")


def example_dark_choice():
    """Example of handling a dark/violent user choice"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Dark/Violent Choice (Your Example)")
    print("="*70 + "\n")
    
    engine = AdaptiveStoryEngine(model_name='distilgpt2')
    
    # Your exact scenario
    initial = engine.start_story(
        "It was a nice day. John's friend Michael came to say hello."
    )
    print("📖 Initial Story:")
    print(initial)
    print()
    
    # User makes dark choice
    print("User action: 'John pushes Michael into slurry pit and he drowns'\n")
    status, continuation = engine.process_user_action(
        "John pushes Michael into the slurry pit and he drowns"
    )
    print(f"Status: {status}")
    print(f"📖 Story adapts and continues:\n{continuation}\n")
    print("Note: The story acknowledges the dark action and shows consequences")


def example_absurd_choice():
    """Example of handling absurd user choices"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Absurd Choice")
    print("="*70 + "\n")
    
    engine = AdaptiveStoryEngine(model_name='distilgpt2')
    
    initial = engine.start_story(
        "Sarah was walking through the park when she saw a mysterious box."
    )
    print("📖 Initial Story:")
    print(initial)
    print()
    
    # User makes absurd choice
    print("User action: 'Sarah turns into a dragon and flies away'\n")
    status, continuation = engine.process_user_action(
        "Sarah turns into a dragon and flies away"
    )
    print(f"Status: {status}")
    print(f"📖 Story adapts (grounding the absurdity):\n{continuation}\n")
    print("Note: The engine tries to ground absurd actions or show they don't work")


def example_rejected_input():
    """Example of inputs that get rejected"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Rejected Inputs")
    print("="*70 + "\n")
    
    engine = AdaptiveStoryEngine(model_name='distilgpt2')
    
    initial = engine.start_story()
    print("📖 Initial Story:")
    print(initial)
    print()
    
    # Meta question (rejected)
    print("User action: 'What is the weather like?'\n")
    status, continuation = engine.process_user_action(
        "What is the weather like?"
    )
    print(f"Status: {status}")
    print(f"Response: {continuation}\n")
    
    # Too absurd (rejected)
    print("User action: 'Character destroys the universe with magic powers'\n")
    status, continuation = engine.process_user_action(
        "Character destroys the universe with magic powers and teleports to Mars"
    )
    print(f"Status: {status}")
    print(f"Response: {continuation}\n")


def example_story_progression():
    """Example showing how story beats progress"""
    print("\n" + "="*70)
    print("EXAMPLE 5: Full Story Progression")
    print("="*70 + "\n")
    
    engine = AdaptiveStoryEngine(model_name='distilgpt2')
    
    # Start story
    initial = engine.start_story(
        "Detective Miller received a call about a missing person case."
    )
    print(f"📖 Story ({engine.current_beat.value}):")
    print(initial)
    print()
    
    # Series of user actions
    actions = [
        "Miller decides to investigate the victim's house",
        "Miller finds a mysterious note hidden under the floorboard",
        "Miller confronts the suspect at their workplace",
        "The suspect tries to escape through the back door",
        "Miller catches the suspect and recovers the evidence"
    ]
    
    for action in actions:
        print(f"User action: '{action}'")
        status, continuation = engine.process_user_action(action)
        print(f"📖 Story continues ({engine.current_beat.value}):")
        print(continuation)
        print("\n" + "-"*70 + "\n")


def run_all_examples():
    """Run all examples"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "ADAPTIVE STORY ENGINE - EXAMPLES" + " "*21 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\nThese examples demonstrate how the engine handles different scenarios.")
    print("The model will download on first run (~500MB for distilgpt2)")
    print("\nPress Enter to start...")
    input()
    
    try:
        example_normal_story()
        input("Press Enter for next example...")
        
        example_dark_choice()
        input("Press Enter for next example...")
        
        example_absurd_choice()
        input("Press Enter for next example...")
        
        example_rejected_input()
        input("Press Enter for next example...")
        
        example_story_progression()
        
        print("\n" + "="*70)
        print("✓ All examples completed!")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Examples interrupted")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
