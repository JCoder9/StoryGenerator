"""
Simple Story Generator - Generates story segments on-demand with choices
Much faster than pre-generating entire tree
"""

import json
from typing import Dict, List
from adaptive_story_engine_enhanced import AdaptiveStoryEngine


class SimpleStoryGenerator:
    """Generates story segments on-demand with built-in choices"""
    
    def __init__(self, model_name='TinyLlama/TinyLlama-1.1B-Chat-v1.0'):
        print("📖 Initializing Simple Story Generator...")
        self.engine = AdaptiveStoryEngine(model_name=model_name, use_enhanced_prompts=True)
        self.story_path = []  # Track user's path through story
        self.genre = None
        
    def start_story(self, genre: str) -> Dict:
        """
        Start a new story in the specified genre
        Returns the opening scene with choices
        """
        self.genre = genre
        self.story_path = []
        
        # Genre-specific story openings
        openings = {
            'detective': {
                'text': """Detective Sarah Chen stood at the crime scene, rain drumming on her umbrella. 
                
The victim—Marcus Thornton, investment banker—lay in his locked study. No signs of forced entry. 
A cryptic note on his desk read: 'The past always collects its debts.'

Three suspects emerged quickly:
• Jennifer Wu - His business partner, stood to inherit everything
• David Ross - Former client who lost millions in a bad deal  
• Elena Vasquez - His assistant, who was seen arguing with him yesterday""",
                'choices': [
                    'Interrogate Jennifer Wu about the business partnership',
                    'Investigate David Ross\' whereabouts last night',
                    'Search the study for hidden clues'
                ]
            },
            'scifi': {
                'text': """You wake aboard the research station Artemis, orbiting a distant exoplanet.
                
The emergency klaxons are blaring. Your head pounds. The last thing you remember is... nothing.

Through the viewport, the planet below churns with purple storms. Your tablet blinks with three urgent messages:

• LIFE SUPPORT: Critical failure in Sector 7 - 2 hours until cascade
• COMMS: Distress signal detected from planet surface
• SECURITY: Unknown life form detected in cargo bay""",
                'choices': [
                    'Rush to Sector 7 to fix life support',
                    'Investigate the distress signal from the planet',
                    'Check the cargo bay for the life form'
                ]
            },
            'horror': {
                'text': """The Ashwood Manor looms before you, its windows dark like hollow eyes.
                
You inherit this from your late aunt, but the townsfolk warned you not to come here after dark. 
Too late now - your car died a mile back, and the sun is setting.

The front door creaks open at your touch. Inside, three hallways await:

• Left corridor: A faint child's laughter echoes from the nursery
• Straight ahead: The grand staircase, where portraits seem to follow your movement  
• Right passage: The kitchen, where a candle burns despite the house being empty for years""",
                'choices': [
                    'Follow the laughter to the nursery',
                    'Climb the grand staircase to investigate',
                    'Enter the kitchen to see who lit the candle'
                ]
            },
            'war': {
                'text': """Your squad advances through the ruins of Stalingrad, winter 1942.
                
Sergeant Viktor grips your shoulder. "Listen up. Command needs intelligence on German positions. 
We've got three objectives, but we can only hit one before dark."

The ruined city stretches before you:

• North: The factory district - enemy armor spotted, but also radio equipment
• East: The apartment blocks - civilians trapped, but it's a trap zone
• West: The river dock - supply cache, heavily defended""",
                'choices': [
                    'Infiltrate the factory for intelligence',
                    'Rescue civilians from the apartments',
                    'Raid the supply cache at the docks'
                ]
            },
            'adventure': {
                'text': """The ancient temple rises from the jungle, covered in vines and mystery.
                
Your guide, Diego, points to the entrance. "The Codex of Kings is inside. But so are the traps."

You've studied the temple layout. Three entrances are visible:

• Main gate: Grand but obvious - likely the most trapped
• Water channel: Leads to underground caverns, could flood
• Collapsed wall: Recent damage, unstable but might bypass traps""",
                'choices': [
                    'Enter through the main gate carefully',
                    'Wade through the water channel',
                    'Climb through the collapsed wall'
                ]
            }
        }
        
        opening = openings.get(genre, openings['adventure'])
        
        return {
            'text': opening['text'],
            'choices': [{'text': c} for c in opening['choices']],  # Format as objects
            'is_ending': False,
            'node_id': 'start'
        }
    
    def continue_story(self, choice_text: str, previous_context: str) -> Dict:
        """
        Generate the next story segment based on user's choice
        
        Args:
            choice_text: The choice the user made
            previous_context: Previous story text for context
            
        Returns:
            Next story segment with new choices
        """
        # Add choice to story path
        self.story_path.append(choice_text)
        
        # Build context for AI - keep it SHORT so AI has tokens for output
        context = f"""{previous_context}

Player's choice: {choice_text}

Continue the story (2-3 paragraphs). Then write "Choices:" and list 3 options numbered 1, 2, 3."""
        
        # Generate continuation
        print(f"🎬 Generating story continuation...")
        print(f"📝 User choice: {choice_text}")
        story_text = self._generate_segment(context)
        print(f"📖 Generated text: {story_text[:200]}...")  # Show first 200 chars
        
        # Extract choices from generated text (or create default ones)
        print(f"📄 Full generated text:\n{story_text}\n")
        choices = self._extract_or_create_choices(story_text)
        print(f"🎯 Final choices: {choices}")
        
        # Check if this should be an ending (after 8+ choices)
        is_ending = len(self.story_path) >= 8
        
        if is_ending:
            # Generate an ending instead
            ending_context = f"""Genre: {self.genre}

Story so far:
{previous_context}

User chose: {choice_text}

Write a satisfying ENDING to this story in 2-3 paragraphs. Wrap up the plot."""
            
            story_text = self._generate_segment(ending_context)
            choices = [{'text': '🔄 Start New Story', 'action': 'restart'}]
        
        return {
            'text': story_text,
            'choices': [{'text': c} for c in choices] if isinstance(choices[0], str) else choices,
            'is_ending': is_ending,
            'node_id': f'node_{len(self.story_path)}'
        }
    
    def _generate_segment(self, context: str, max_retries: int = 2) -> str:
        """Generate a single story segment with retry logic"""
        
        for attempt in range(max_retries):
            try:
                # Use the engine's internal generation method with correct parameters
                text = self.engine._generate_text(
                    prompt=context,
                    system_instruction=f"Write a {self.genre} story continuation. End with 'Choices:' followed by exactly 3 numbered options (1. 2. 3.).",
                    max_length=300,  # Increased from 150 to give AI enough space
                    temperature=0.8
                )
                
                # Clean up the text
                text = text.strip()
                
                if len(text) > 20:  # Valid text
                    return text
                
            except Exception as e:
                print(f"⚠️  Generation attempt {attempt+1} failed: {e}")
                import traceback
                traceback.print_exc()
                if attempt == max_retries - 1:
                    return "The story continues... (Generation error, please try again)"
        
        return "The story continues..."
    
    def _extract_or_create_choices(self, text: str) -> List[str]:
        """Extract choices from generated text or create default ones"""
        
        # Split text into lines and look for choices only in the latter part
        lines = text.split('\n')
        choices = []
        in_choice_section = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Detect start of choice section (common markers)
            if any(marker in line.lower() for marker in ['choices:', 'options:', 'what do you do', 'you can:']):
                in_choice_section = True
                continue
            
            # Look for numbered or bulleted lines
            if line.startswith(('-', '*', '•', '1.', '2.', '3.', '4.', '5.')):
                in_choice_section = True
                choice = line.lstrip('-*•12345. ').strip()
                
                # Validate choice: reasonable length and ends properly
                if choice and 10 <= len(choice) <= 200:
                    # Remove any trailing punctuation that looks incomplete
                    if choice.endswith((',', ';', ':')):
                        choice = choice[:-1].strip()
                    if choice:  # Still valid after cleanup
                        choices.append(choice)
        
        # Need at least 3 choices to trust AI output
        if len(choices) >= 3:
            print(f"✅ Using AI-generated choices")
            return choices[:3]
        
        # AI didn't generate good choices - create context-aware fallback
        print(f"⚠️  AI only generated {len(choices)} choices, creating fallback choices")
        
        # Try to extract key words/concepts from the story text to make relevant choices
        story_lower = text.lower()
        
        # Create context-aware choices based on story content
        fallback_choices = []
        
        # Detection patterns for common story elements
        if any(word in story_lower for word in ['door', 'room', 'hallway', 'corridor', 'passage']):
            fallback_choices.append("Investigate the other rooms")
        elif any(word in story_lower for word in ['outside', 'exit', 'escape', 'leave']):
            fallback_choices.append("Try to find a way out")
        else:
            fallback_choices.append("Explore the area carefully")
        
        if any(word in story_lower for word in ['sound', 'noise', 'hear', 'voice', 'whisper', 'footsteps']):
            fallback_choices.append("Follow the sound")
        elif any(word in story_lower for word in ['light', 'shadow', 'dark', 'candle', 'glow']):
            fallback_choices.append("Move toward the light")
        else:
            fallback_choices.append("Search for clues")
        
        if any(word in story_lower for word in ['weapon', 'defend', 'attack', 'danger', 'threat']):
            fallback_choices.append("Prepare to defend yourself")
        elif any(word in story_lower for word in ['hide', 'run', 'flee', 'escape']):
            fallback_choices.append("Look for a hiding place")
        else:
            fallback_choices.append("Continue cautiously")
        
        return fallback_choices[:3]
