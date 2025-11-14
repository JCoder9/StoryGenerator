"""
Adaptive Story Engine - Uses Pre-trained GPT-2 Model
Dynamically adapts story based on user decisions while maintaining narrative coherence
"""

from transformers import GPT2LMHeadModel, GPT2Tokenizer
import torch
import re
from typing import List, Dict, Tuple, Optional
from enum import Enum


class StoryBeat(Enum):
    """Narrative structure following classic storytelling"""
    EXPOSITION = "exposition"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


class AdaptiveStoryEngine:
    """
    Main engine for adaptive storytelling with user choice integration
    """
    
    def __init__(self, model_name='gpt2'):
        """
        Initialize the story engine with a pre-trained model
        
        Args:
            model_name: Hugging Face model name (default: 'gpt2')
                       Options: 'gpt2', 'distilgpt2' (faster for old hardware)
        """
        print(f"🔄 Loading pre-trained model: {model_name}")
        print("   (This may take a minute on first run...)")
        
        try:
            self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
            self.model = GPT2LMHeadModel.from_pretrained(model_name)
            
            # Set padding token
            self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("✓ Model loaded successfully!\n")
        except Exception as e:
            print(f"\n❌ Failed to load model '{model_name}'")
            print(f"   Error: {e}")
            print("\n💡 Troubleshooting:")
            print("   1. Ensure you have internet connection (first-time download ~350MB)")
            print("   2. Check ~/.cache/huggingface/ has write permissions")
            print("   3. Try using 'distilgpt2' instead (smaller, faster)")
            print("\n   Example: AdaptiveStoryEngine(model_name='distilgpt2')")
            raise RuntimeError(f"Model initialization failed: {e}")
        
        # Story state
        self.story_history: List[str] = []
        self.user_actions: List[str] = []
        self.characters: Dict[str, Dict] = {}
        self.locations: set = set()
        self.current_beat = StoryBeat.EXPOSITION
        self.beat_counter = 0
        
        # Narrative parameters
        self.max_context_length = 1024  # GPT-2 max tokens
        self.generation_length = 100
        self.temperature = 0.8
        
    def start_story(self, initial_prompt: Optional[str] = None) -> str:
        """
        Start a new story with an optional custom prompt
        
        Args:
            initial_prompt: Custom story opening, or None for default
            
        Returns:
            Generated story opening
        """
        if initial_prompt:
            self.story_history = [initial_prompt]
            prompt = initial_prompt
        else:
            # Default story openings
            prompts = [
                "It was a pleasant afternoon when John decided to take a walk through the park.",
                "The old mansion on the hill had been abandoned for years, until today.",
                "Sarah received a mysterious letter that would change everything.",
                "In the quiet town of Millbrook, nothing exciting ever happened. Until now."
            ]
            import random
            prompt = random.choice(prompts)
            self.story_history = [prompt]
        
        # Generate initial continuation
        continuation = self._generate_text(
            prompt,
            system_instruction="Begin an engaging narrative story with clear characters and setting."
        )
        
        self.story_history.append(continuation)
        self._extract_story_elements(prompt + " " + continuation)
        
        return prompt + " " + continuation
    
    def process_user_action(self, user_input: str) -> Tuple[str, str]:
        """
        Process user's decision/action and adapt the story accordingly
        
        Args:
            user_input: User's choice/action in the story
            
        Returns:
            Tuple of (validation_status, story_continuation)
            validation_status: "accepted", "adapted", or "rejected"
        """
        # Validate user input
        validation = self._validate_user_input(user_input)
        
        if validation["status"] == "rejected":
            return "rejected", validation["message"]
        
        # Add user action to history
        self.user_actions.append(user_input)
        
        # Adapt story based on user action
        adapted_story = self._adapt_story_to_action(user_input, validation)
        
        # Update story history
        self.story_history.append(f"User action: {user_input}")
        self.story_history.append(adapted_story)
        
        # Update narrative beat
        self._update_story_beat()
        
        return validation["status"], adapted_story
    
    def _validate_user_input(self, user_input: str) -> Dict:
        """
        Validate if user input can be integrated into the story
        
        Returns:
            Dict with 'status' and 'message' or 'severity'
        """
        user_lower = user_input.lower().strip()
        
        # Check for empty input
        if len(user_lower) < 3:
            return {
                "status": "rejected",
                "message": "❌ Error: Please provide a meaningful action or choice."
            }
        
        # Check for meta/breaking inputs
        meta_phrases = [
            "what is", "how do i", "can you", "tell me",
            "explain", "define", "who are you", "what are you"
        ]
        
        if any(phrase in user_lower for phrase in meta_phrases):
            return {
                "status": "rejected",
                "message": "❌ Error: Please stay in character. Describe what your character does, not meta questions."
            }
        
        # Check for extreme absurdity that breaks narrative possibility
        absurd_markers = [
            "turns into", "becomes god", "teleports to mars",
            "destroys the universe", "time travel", "magic powers"
        ]
        
        # Allow some absurdity but flag it
        absurdity_level = sum(1 for marker in absurd_markers if marker in user_lower)
        
        if absurdity_level > 2:
            return {
                "status": "rejected",
                "message": "❌ Error: This action is too unrealistic for the story to continue coherently. Try something more grounded."
            }
        elif absurdity_level > 0:
            return {
                "status": "adapted",
                "severity": "high",
                "message": "⚠️  Adapting your unusual choice into the narrative..."
            }
        
        # Check for violence/dark actions - allow but flag
        dark_markers = ["kills", "murder", "destroys", "attack", "stab", "shoot"]
        if any(marker in user_lower for marker in dark_markers):
            return {
                "status": "adapted",
                "severity": "dark",
                "message": "⚠️  Processing dramatic turn of events..."
            }
        
        # Normal input
        return {
            "status": "accepted",
            "severity": "normal"
        }
    
    def _adapt_story_to_action(self, user_action: str, validation: Dict) -> str:
        """
        Adapt the story continuation based on user's action
        
        Args:
            user_action: What the user chose to do
            validation: Validation result from _validate_user_input
            
        Returns:
            Story continuation that incorporates the user action
        """
        # Get recent context
        context = self._build_context()
        
        # Determine how to frame the user action based on severity
        severity = validation.get("severity", "normal")
        
        if severity == "dark":
            # Handle dark/violent actions with consequences
            prompt = f"{context}\n\nUnexpectedly, {user_action}. The consequences of this action would be severe."
            system_instruction = (
                "Continue the story showing realistic consequences of this dark action. "
                "The narrative should address the gravity of what happened, show character reactions, "
                "and move toward either justice, redemption, or tragedy. Maintain narrative coherence."
            )
        elif severity == "high":
            # Handle absurd actions by grounding them or showing they don't work as expected
            prompt = f"{context}\n\n{user_action}"
            system_instruction = (
                "The character attempts something unusual. Show what realistically happens - "
                "either it doesn't work as expected, or there's a more mundane explanation. "
                "Maintain story believability while acknowledging the attempt."
            )
        else:
            # Normal action - integrate naturally
            prompt = f"{context}\n\n{user_action}"
            system_instruction = (
                "Continue the story naturally from this character action. "
                "Show consequences, reactions from other characters, and move the plot forward. "
                "Maintain narrative tension and pacing."
            )
        
        # Generate adapted continuation
        continuation = self._generate_text(
            prompt,
            system_instruction=system_instruction,
            temperature=self.temperature
        )
        
        return continuation
    
    def _generate_text(
        self,
        prompt: str,
        system_instruction: str = "",
        temperature: float = 0.8,
        max_length: int = None
    ) -> str:
        """
        Generate text using the pre-trained model
        
        Args:
            prompt: Input prompt
            system_instruction: Guidance for generation style
            temperature: Sampling temperature (higher = more creative)
            max_length: Maximum tokens to generate
            
        Returns:
            Generated text
        """
        if max_length is None:
            max_length = self.generation_length
        
        # Combine system instruction and prompt if provided
        if system_instruction:
            full_prompt = f"[Instruction: {system_instruction}]\n\n{prompt}\n\n"
        else:
            full_prompt = prompt
        
        # Tokenize
        inputs = self.tokenizer.encode(
            full_prompt,
            return_tensors='pt',
            max_length=self.max_context_length,
            truncation=True
        )
        
        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                inputs,
                max_length=inputs.shape[1] + max_length,
                num_return_sequences=1,
                temperature=temperature,
                top_p=0.9,  # Nucleus sampling
                top_k=50,   # Top-k sampling
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                repetition_penalty=1.2,  # Avoid repetition
                no_repeat_ngram_size=3
            )
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the prompt part
        if system_instruction:
            # Remove system instruction and prompt
            generated_text = generated_text.replace(full_prompt, "").strip()
        else:
            generated_text = generated_text.replace(prompt, "").strip()
        
        # Clean up
        generated_text = self._clean_generated_text(generated_text)
        
        return generated_text
    
    def _clean_generated_text(self, text: str) -> str:
        """Clean and format generated text"""
        # Remove incomplete sentences at the end
        sentences = re.split(r'[.!?]+', text)
        
        # Keep only complete sentences
        if len(sentences) > 1 and len(sentences[-1].strip()) < 10:
            sentences = sentences[:-1]
        
        cleaned = '. '.join(s.strip() for s in sentences if s.strip())
        
        # Ensure proper ending punctuation
        if cleaned and cleaned[-1] not in '.!?':
            cleaned += '.'
        
        return cleaned
    
    def _build_context(self, max_sentences: int = 5) -> str:
        """
        Build context from recent story history
        
        Args:
            max_sentences: Maximum number of recent story segments to include
            
        Returns:
            Context string
        """
        # Get last few story segments
        recent = self.story_history[-max_sentences:]
        return " ".join(recent)
    
    def _extract_story_elements(self, text: str):
        """Extract and track story elements like characters and locations"""
        # Simple character extraction (capitalized names)
        potential_names = re.findall(r'\b([A-Z][a-z]+)\b', text)
        
        for name in potential_names:
            if name not in self.characters and len(name) > 2:
                self.characters[name] = {
                    "introduced": len(self.story_history),
                    "mentioned": 1
                }
            elif name in self.characters:
                self.characters[name]["mentioned"] += 1
    
    def _update_story_beat(self):
        """Update current narrative beat based on story progression"""
        self.beat_counter += 1
        
        # Progress through story beats
        if self.beat_counter > 15:
            self.current_beat = StoryBeat.RESOLUTION
        elif self.beat_counter > 12:
            self.current_beat = StoryBeat.FALLING_ACTION
        elif self.beat_counter > 8:
            self.current_beat = StoryBeat.CLIMAX
        elif self.beat_counter > 5:
            self.current_beat = StoryBeat.RISING_ACTION
        elif self.beat_counter > 2:
            self.current_beat = StoryBeat.INCITING_INCIDENT
    
    def get_story_summary(self) -> str:
        """Get a summary of the current story state"""
        summary = f"""
        📖 Story Summary
        ───────────────────────────────────────
        Current Beat: {self.current_beat.value.replace('_', ' ').title()}
        Actions Taken: {len(self.user_actions)}
        Characters: {', '.join(self.characters.keys()) if self.characters else 'None identified'}
        
        Recent Story:
        {self._build_context(max_sentences=3)}
        ───────────────────────────────────────
        """
        return summary
    
    def suggest_actions(self) -> List[str]:
        """Suggest possible actions based on current story state"""
        # This would be enhanced with more sophisticated logic
        suggestions = [
            "Continue the current path",
            "Investigate further",
            "Talk to another character",
            "Make a different choice",
            "Try to resolve the situation"
        ]
        return suggestions


def main():
    """Main interactive loop"""
    print("=" * 70)
    print("  ADAPTIVE INTERACTIVE STORY GENERATOR")
    print("  Powered by GPT-2 Pre-trained Model")
    print("=" * 70)
    print()
    
    # Initialize engine (use 'distilgpt2' for faster performance on old hardware)
    engine = AdaptiveStoryEngine(model_name='distilgpt2')
    
    print("📚 INSTRUCTIONS:")
    print("   - The AI will generate story segments")
    print("   - You decide what happens next")
    print("   - Your choices affect the narrative")
    print("   - Type 'summary' to see story state")
    print("   - Type 'quit' to exit")
    print("=" * 70)
    print()
    
    # Start the story
    print("🎬 Starting your story...\n")
    initial_story = engine.start_story()
    
    print("📖 STORY:")
    print("─" * 70)
    print(initial_story)
    print("─" * 70)
    print()
    
    # Main interaction loop
    while True:
        print("❓ What happens next? (What does your character do?)")
        user_input = input("→ ").strip()
        
        if not user_input:
            print("⚠️  Please provide an action.\n")
            continue
        
        if user_input.lower() == 'quit':
            print("\n👋 Thank you for playing! Your story ends here.")
            break
        
        if user_input.lower() == 'summary':
            print(engine.get_story_summary())
            continue
        
        # Process user action
        print("\n🤔 Processing your choice...\n")
        status, continuation = engine.process_user_action(user_input)
        
        if status == "rejected":
            print(continuation)
            print()
            continue
        
        # Display story continuation
        print("📖 STORY CONTINUES:")
        print("─" * 70)
        print(f"[You: {user_input}]")
        print()
        print(continuation)
        print("─" * 70)
        print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Story interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
