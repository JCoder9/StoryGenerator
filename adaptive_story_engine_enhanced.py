"""
ENHANCED Adaptive Story Engine - With Advanced Storytelling Framework
Significantly improved narrative quality through prompt engineering and better parameters
"""

# Prevent TensorFlow from being imported by transformers (we only use PyTorch)
import os
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Import only GPT2 models to avoid triggering Auto classes that import TensorFlow
from transformers import GPT2LMHeadModel, GPT2Tokenizer
# Lazy import for Auto classes only when needed
_AutoModelForCausalLM = None
_AutoTokenizer = None

def get_auto_model():
    """Lazy import of AutoModelForCausalLM to avoid TensorFlow import on startup"""
    global _AutoModelForCausalLM
    if _AutoModelForCausalLM is None:
        from transformers import AutoModelForCausalLM
        _AutoModelForCausalLM = AutoModelForCausalLM
    return _AutoModelForCausalLM

def get_auto_tokenizer():
    """Lazy import of AutoTokenizer to avoid TensorFlow import on startup"""
    global _AutoTokenizer
    if _AutoTokenizer is None:
        from transformers import AutoTokenizer
        _AutoTokenizer = AutoTokenizer
    return _AutoTokenizer

import torch
import re
from typing import List, Dict, Tuple, Optional
from enum import Enum
from collections import defaultdict


class StoryBeat(Enum):
    """Narrative structure following classic storytelling"""
    EXPOSITION = "exposition"
    INCITING_INCIDENT = "inciting_incident"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"


class GenreConfig:
    """Genre-specific narrative constraints and structure"""
    
    DETECTIVE_MYSTERY = {
        "name": "detective",
        "beats": [
            "crime_discovered",
            "investigation_begins",
            "first_clue_found",
            "suspects_identified",
            "red_herring",
            "crucial_clue_discovered",
            "confrontation",
            "truth_revealed",
            "resolution"
        ],
        "required_elements": {
            "protagonist_type": "detective",
            "antagonist_type": "criminal",
            "macguffin": "mystery to solve",
            "setting_types": ["crime scene", "investigation location", "suspect locations"]
        },
        "tone_keywords": [
            "investigate", "clue", "evidence", "suspect", "motive",
            "alibi", "witness", "case", "detective", "crime",
            "murder", "victim", "interrogate", "deduce", "solve"
        ],
        "forbidden_keywords": [
            "wizard", "magic spell", "alien", "spaceship", "time machine",
            "vampire", "werewolf", "superpower", "fantasy realm"
        ],
        "story_elements": {
            "clues": [],
            "suspects": [],
            "red_herrings": [],
            "victim": None,
            "crime_type": None,
            "crime_location": None
        }
    }
    
    ROMANTIC_COMEDY = {
        "name": "romcom",
        "beats": [
            "meet_cute",
            "initial_attraction",
            "first_interaction",
            "growing_closer",
            "comedy_moment",
            "romantic_tension",
            "misunderstanding",
            "separation",
            "realization",
            "grand_gesture",
            "reconciliation",
            "happy_ending"
        ],
        "required_elements": {
            "protagonist_type": "romantic_lead",
            "love_interest": "romantic_partner",
            "obstacle": "relationship_conflict",
            "setting_types": ["romantic location", "workplace", "social setting"]
        },
        "tone_keywords": [
            "love", "romance", "heart", "feelings", "attraction",
            "date", "kiss", "relationship", "chemistry", "flirt",
            "awkward", "funny", "charming", "cute", "sweet"
        ],
        "forbidden_keywords": [
            "murder", "corpse", "blood", "violence", "kill",
            "horror", "terror", "monster", "death"
        ],
        "story_elements": {
            "romantic_moments": [],
            "comedy_beats": [],
            "obstacles": [],
            "relationship_stage": "strangers"
        }
    }
    
    HORROR = {
        "name": "horror",
        "beats": [
            "normal_world",
            "first_warning",
            "something_wrong",
            "denial",
            "escalation",
            "threat_revealed",
            "fight_or_flight",
            "darkest_moment",
            "final_confrontation",
            "aftermath"
        ],
        "required_elements": {
            "protagonist_type": "survivor",
            "antagonist_type": "threat",
            "macguffin": "source of horror",
            "setting_types": ["isolated location", "haunted place", "dangerous area"]
        },
        "tone_keywords": [
            "fear", "terror", "shadow", "darkness", "scream",
            "blood", "creature", "haunted", "evil", "nightmare",
            "death", "monster", "horror", "creepy", "sinister"
        ],
        "forbidden_keywords": [
            "romance", "wedding", "date", "love", "cute",
            "funny", "comedy", "laugh"
        ],
        "story_elements": {
            "threats_encountered": [],
            "victims": [],
            "safe_locations": [],
            "threat_type": None
        }
    }
    
    @staticmethod
    def get_config(genre: str) -> Dict:
        """Get configuration for specified genre"""
        genre_map = {
            "mystery": GenreConfig.DETECTIVE_MYSTERY,
            "detective": GenreConfig.DETECTIVE_MYSTERY,
            "romcom": GenreConfig.ROMANTIC_COMEDY,
            "romance": GenreConfig.ROMANTIC_COMEDY,
            "horror": GenreConfig.HORROR
        }
        return genre_map.get(genre.lower(), GenreConfig.DETECTIVE_MYSTERY)


class PlayerProfile:
    """
    Tracks player personality and decision patterns
    Adapts story based on player's demonstrated character traits
    """
    
    def __init__(self):
        # Core personality axes
        self.morality_score = 0  # -100 (evil) to +100 (good)
        self.risk_taking = 0     # -100 (cautious) to +100 (reckless)
        self.empathy = 0         # -100 (cold) to +100 (compassionate)
        self.aggression = 0      # -100 (passive) to +100 (aggressive)
        self.curiosity = 0       # -100 (avoidant) to +100 (investigative)
        
        # Decision tracking
        self.choices = defaultdict(int)
        self.action_history = []
        self.personality_keywords = defaultdict(int)
        
        # Character archetype (emerges from choices)
        self.archetype = "Unknown"
        self.archetype_confidence = 0.0
        
    def analyze_action(self, action: str) -> Dict:
        """
        Analyze user action and update personality profile
        
        Returns dict with detected traits and score adjustments
        """
        action_lower = action.lower()
        detected_traits = {}
        
        # MORALITY ANALYSIS
        good_keywords = ['help', 'save', 'protect', 'comfort', 'heal', 'rescue', 'donate', 'honest']
        evil_keywords = ['steal', 'kill', 'murder', 'betray', 'lie', 'cheat', 'harm', 'destroy']
        
        if any(kw in action_lower for kw in good_keywords):
            self.morality_score = min(100, self.morality_score + 10)
            detected_traits['morality'] = 'good'
            self.choices['moral_good'] += 1
        elif any(kw in action_lower for kw in evil_keywords):
            self.morality_score = max(-100, self.morality_score - 15)
            detected_traits['morality'] = 'evil'
            self.choices['moral_evil'] += 1
        
        # RISK TAKING ANALYSIS
        risky_keywords = ['rush', 'immediately', 'without', 'charge', 'attack', 'confront', 'dare']
        cautious_keywords = ['carefully', 'slowly', 'observe', 'wait', 'hide', 'avoid', 'plan']
        
        if any(kw in action_lower for kw in risky_keywords):
            self.risk_taking = min(100, self.risk_taking + 8)
            detected_traits['risk'] = 'bold'
            self.choices['risk_bold'] += 1
        elif any(kw in action_lower for kw in cautious_keywords):
            self.risk_taking = max(-100, self.risk_taking - 8)
            detected_traits['risk'] = 'cautious'
            self.choices['risk_cautious'] += 1
        
        # EMPATHY ANALYSIS
        empathy_keywords = ['comfort', 'listen', 'understand', 'support', 'care', 'gentle', 'kind']
        cold_keywords = ['ignore', 'dismiss', 'coldly', 'indifferent', 'uncaring', 'harsh']
        
        if any(kw in action_lower for kw in empathy_keywords):
            self.empathy = min(100, self.empathy + 10)
            detected_traits['empathy'] = 'compassionate'
            self.choices['empathy_high'] += 1
        elif any(kw in action_lower for kw in cold_keywords):
            self.empathy = max(-100, self.empathy - 10)
            detected_traits['empathy'] = 'cold'
            self.choices['empathy_low'] += 1
        
        # AGGRESSION ANALYSIS
        aggressive_keywords = ['attack', 'fight', 'punch', 'hit', 'threaten', 'yell', 'demand']
        passive_keywords = ['negotiate', 'talk', 'discuss', 'reason', 'compromise', 'calm']
        
        if any(kw in action_lower for kw in aggressive_keywords):
            self.aggression = min(100, self.aggression + 12)
            detected_traits['aggression'] = 'aggressive'
            self.choices['aggression_high'] += 1
        elif any(kw in action_lower for kw in passive_keywords):
            self.aggression = max(-100, self.aggression - 8)
            detected_traits['aggression'] = 'diplomatic'
            self.choices['aggression_low'] += 1
        
        # CURIOSITY ANALYSIS
        curious_keywords = ['investigate', 'examine', 'search', 'explore', 'ask', 'question', 'study']
        avoidant_keywords = ['leave', 'walk away', 'avoid', 'skip', 'ignore the']
        
        if any(kw in action_lower for kw in curious_keywords):
            self.curiosity = min(100, self.curiosity + 10)
            detected_traits['curiosity'] = 'investigative'
            self.choices['curiosity_high'] += 1
        elif any(kw in action_lower for kw in avoidant_keywords):
            self.curiosity = max(-100, self.curiosity - 8)
            detected_traits['curiosity'] = 'avoidant'
            self.choices['curiosity_low'] += 1
        
        # Track keywords for pattern detection
        for word in action_lower.split():
            if len(word) > 4:  # Only meaningful words
                self.personality_keywords[word] += 1
        
        # Record action
        self.action_history.append({
            'action': action,
            'traits': detected_traits,
            'timestamp': len(self.action_history)
        })
        
        # Update archetype
        self._update_archetype()
        
        return detected_traits
    
    def _update_archetype(self):
        """Determine player archetype from personality scores"""
        total_actions = len(self.action_history)
        
        if total_actions < 3:
            self.archetype = "Developing..."
            self.archetype_confidence = 0.0
            return
        
        # Define archetypes based on personality combinations
        archetypes = []
        
        # Hero (good + brave + empathetic)
        if self.morality_score > 30 and self.risk_taking > 20 and self.empathy > 20:
            archetypes.append(("Hero", 0.9))
        
        # Villain (evil + aggressive + cold)
        if self.morality_score < -30 and self.aggression > 30 and self.empathy < -20:
            archetypes.append(("Villain", 0.9))
        
        # Detective (curious + cautious + moral)
        if self.curiosity > 40 and self.risk_taking < 0 and self.morality_score > 10:
            archetypes.append(("Detective", 0.85))
        
        # Rogue (morally gray + risky + cunning)
        if abs(self.morality_score) < 30 and self.risk_taking > 30 and self.curiosity > 20:
            archetypes.append(("Rogue", 0.8))
        
        # Diplomat (empathetic + non-aggressive + cautious)
        if self.empathy > 30 and self.aggression < -20 and self.risk_taking < 0:
            archetypes.append(("Diplomat", 0.85))
        
        # Warrior (aggressive + brave + morally flexible)
        if self.aggression > 40 and self.risk_taking > 30:
            archetypes.append(("Warrior", 0.8))
        
        # Anti-Hero (morally gray + aggressive + empathetic)
        if abs(self.morality_score) < 40 and self.aggression > 20 and self.empathy > 10:
            archetypes.append(("Anti-Hero", 0.75))
        
        # Scholar (curious + cautious + passive)
        if self.curiosity > 40 and self.risk_taking < -20 and self.aggression < 0:
            archetypes.append(("Scholar", 0.8))
        
        # Survivor (cautious + avoidant + practical)
        if self.risk_taking < -30 and self.curiosity < 0 and abs(self.morality_score) < 20:
            archetypes.append(("Survivor", 0.75))
        
        # Chaotic Neutral (unpredictable, all scores near zero)
        if all(abs(score) < 30 for score in [self.morality_score, self.risk_taking, 
                                               self.empathy, self.aggression, self.curiosity]):
            archetypes.append(("Wildcard", 0.6))
        
        if archetypes:
            # Sort by confidence and pick highest
            archetypes.sort(key=lambda x: x[1], reverse=True)
            self.archetype, self.archetype_confidence = archetypes[0]
        else:
            self.archetype = "Complex Character"
            self.archetype_confidence = 0.5
    
    def get_profile_summary(self) -> str:
        """Get human-readable personality profile"""
        def score_to_label(score, negative_label, positive_label):
            if score > 50:
                return f"Very {positive_label}"
            elif score > 20:
                return positive_label.capitalize()
            elif score > -20:
                return "Balanced"
            elif score > -50:
                return negative_label.capitalize()
            else:
                return f"Very {negative_label}"
        
        profile = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PLAYER PERSONALITY PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎭 Archetype: {self.archetype} ({self.archetype_confidence:.0%} confidence)
📊 Actions Analyzed: {len(self.action_history)}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PERSONALITY TRAITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚖️  Morality:    {score_to_label(self.morality_score, 'ruthless', 'virtuous')}
    {'▓' * int((self.morality_score + 100) / 10)} {self.morality_score:+d}

🎲 Risk-Taking:  {score_to_label(self.risk_taking, 'cautious', 'bold')}
    {'▓' * int((self.risk_taking + 100) / 10)} {self.risk_taking:+d}

💙 Empathy:      {score_to_label(self.empathy, 'cold', 'compassionate')}
    {'▓' * int((self.empathy + 100) / 10)} {self.empathy:+d}

⚔️  Aggression:  {score_to_label(self.aggression, 'diplomatic', 'aggressive')}
    {'▓' * int((self.aggression + 100) / 10)} {self.aggression:+d}

🔍 Curiosity:    {score_to_label(self.curiosity, 'avoidant', 'investigative')}
    {'▓' * int((self.curiosity + 100) / 10)} {self.curiosity:+d}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  DECISION PATTERNS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if self.choices:
            for choice_type, count in sorted(self.choices.items(), key=lambda x: x[1], reverse=True)[:5]:
                profile += f"  • {choice_type.replace('_', ' ').title()}: {count}x\n"
        
        profile += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        
        return profile
    
    def get_narrative_guidance(self) -> str:
        """
        Get instructions for AI to adapt story based on player personality
        """
        guidance = "PLAYER PERSONALITY INSIGHTS:\n"
        guidance += f"The player has shown themselves to be a '{self.archetype}' character.\n"
        
        # Morality guidance
        if self.morality_score > 40:
            guidance += "They consistently make moral, heroic choices. Present opportunities for noble sacrifice and moral dilemmas.\n"
        elif self.morality_score < -40:
            guidance += "They embrace dark, ruthless choices. Challenge them with consequences and moral complexity.\n"
        else:
            guidance += "They walk a morally gray path. Present nuanced situations without clear right/wrong.\n"
        
        # Risk guidance
        if self.risk_taking > 40:
            guidance += "They're bold and reckless. Reward their daring with dramatic outcomes (good and bad).\n"
        elif self.risk_taking < -40:
            guidance += "They're methodical and cautious. Provide detailed environmental clues and planning opportunities.\n"
        
        # Empathy guidance
        if self.empathy > 40:
            guidance += "They care deeply about others. Include emotional character moments and relationships.\n"
        elif self.empathy < -40:
            guidance += "They're pragmatic and cold. Focus on logical outcomes over emotional appeals.\n"
        
        # Aggression guidance
        if self.aggression > 40:
            guidance += "They solve problems through force. Provide action scenes but show realistic consequences.\n"
        elif self.aggression < -40:
            guidance += "They prefer negotiation. Create opportunities for clever dialogue and peaceful resolution.\n"
        
        # Curiosity guidance
        if self.curiosity > 40:
            guidance += "They're highly investigative. Reward exploration with hidden secrets and lore.\n"
        elif self.curiosity < -40:
            guidance += "They focus on main objectives. Keep plot straightforward and action-oriented.\n"
        
        guidance += f"\nAdapt the narrative tone, NPC reactions, and story options to match this '{self.archetype}' playstyle."
        
        return guidance
    
    def to_dict(self) -> Dict:
        """Serialize profile for storage"""
        return {
            'morality_score': self.morality_score,
            'risk_taking': self.risk_taking,
            'empathy': self.empathy,
            'aggression': self.aggression,
            'curiosity': self.curiosity,
            'archetype': self.archetype,
            'archetype_confidence': self.archetype_confidence,
            'choices': dict(self.choices),
            'action_count': len(self.action_history)
        }
    
    def from_dict(self, data: Dict):
        """Restore profile from storage"""
        self.morality_score = data.get('morality_score', 0)
        self.risk_taking = data.get('risk_taking', 0)
        self.empathy = data.get('empathy', 0)
        self.aggression = data.get('aggression', 0)
        self.curiosity = data.get('curiosity', 0)
        self.archetype = data.get('archetype', 'Unknown')
        self.archetype_confidence = data.get('archetype_confidence', 0.0)
        self.choices = defaultdict(int, data.get('choices', {}))



# Storytelling Framework - Rules of Good Narrative
STORYTELLING_FRAMEWORK = """
NARRATIVE PRINCIPLES:
1. SHOW, DON'T TELL - Use vivid actions, dialogue, and sensory details instead of bland exposition
2. SENSORY IMMERSION - Include sights, sounds, smells, textures, tastes where appropriate
3. CHARACTER DEPTH - Reveal personality through behavior, dialogue, and inner conflict
4. RISING TENSION - Each scene should escalate stakes, reveal information, or deepen mystery
5. CONCRETE SPECIFICS - Use precise, tangible descriptions not vague generalities
6. NATURAL DIALOGUE - Characters speak distinctly with subtext and personality
7. CAUSE AND EFFECT - Every action has realistic, proportional consequences
8. VARIED PACING - Mix action with reflection, vary sentence rhythms
9. EMOTIONAL RESONANCE - Make readers feel what characters feel
10. MEANINGFUL DETAILS - Every description should serve character, plot, or atmosphere
"""

# Few-shot examples to prime the model
STORY_EXAMPLES = """
EXAMPLE 1 - Good Storytelling:
Action: John enters the abandoned house
Response: The floorboards groaned under John's weight, each step releasing decades of accumulated dust into the stale air. Pale moonlight filtered through cracked windows, casting skeletal shadows across peeling wallpaper. His flashlight beam caught something on the mantle—a photograph, faces frozen in time, eyes that seemed to follow him. The house wasn't as empty as he'd hoped.

EXAMPLE 2 - Good Storytelling:
Action: Sarah confronts the stranger
Response: "I know who you are," Sarah said, her voice steady despite the tremor in her hands. The stranger's smile faded, replaced by something colder, more calculating. Rain drummed against the café window between them, each drop marking the seconds of silence. "Then you know," he finally replied, "that you should have stayed away." His coffee sat untouched, steam rising like a warning.

EXAMPLE 3 - Good Storytelling:
Action: The detective finds a clue
Response: Martinez's fingers traced the edge of the photograph—torn deliberately, not aged. Someone wanted this face hidden. The lab's fluorescent lights hummed overhead as she held it to the light. There, barely visible in the corner: a reflection in a window, a figure watching. Her pulse quickened. The photographer hadn't been alone. And whoever stood in that window knew they'd been captured on film.
"""


class AdaptiveStoryEngine:
    """
    Enhanced engine for adaptive storytelling with advanced narrative quality
    """
    
    def __init__(self, model_name='gpt2-large', use_enhanced_prompts=True):
        """
        Initialize the enhanced story engine
        
        Args:
            model_name: Model to use. Options:
                       'distilgpt2' - Fastest, basic quality (82M)
                       'gpt2' - Fast, OK quality (124M) 
                       'gpt2-medium' - Balanced (355M)
                       'gpt2-large' - RECOMMENDED (774M)
                       'gpt2-xl' - Excellent but slow (1.5B)
                       'EleutherAI/gpt-neo-1.3B' - Amazing quality (1.3B)
                       'facebook/opt-1.3b' - Great quality, faster (1.3B)
            use_enhanced_prompts: Enable advanced storytelling framework
        """
        print(f"🔄 Loading enhanced story engine: {model_name}")
        print("   (This may take time on first run...)")
        
        self.model_name = model_name  # Store model name for later use
        self.use_enhanced_prompts = use_enhanced_prompts
        
        # GENRE CONSTRAINT SYSTEM
        self.current_genre = None
        self.genre_config = None
        self.genre_beat_index = 0
        self.genre_violations = []
        self.genre_elements = {}
        
        try:
            # Support different model architectures
            # Only use GPT2 classes for actual GPT-2 models
            is_gpt2_model = (
                model_name in ['distilgpt2', 'gpt2', 'gpt2-medium', 'gpt2-large', 'gpt2-xl'] or
                (model_name.startswith('gpt2') and '/' not in model_name)
            )
            
            if is_gpt2_model:
                # Standard GPT-2 models
                self.tokenizer = GPT2Tokenizer.from_pretrained(model_name)
                self.model = GPT2LMHeadModel.from_pretrained(model_name)
            else:
                # For GPT-Neo, OPT, Qwen, and other models - use Auto classes
                AutoTokenizer = get_auto_tokenizer()
                AutoModelForCausalLM = get_auto_model()
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForCausalLM.from_pretrained(model_name)
            
            # Set padding token
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
            
            print("✓ Model loaded successfully!")
            print(f"✓ Enhanced prompts: {'ENABLED' if use_enhanced_prompts else 'DISABLED'}\n")
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ Failed to load model '{model_name}'")
            print(f"   Error: {error_msg[:200]}")
            
            # Check for specific Qwen tokenizer error
            if 'Qwen2Tokenizer' in error_msg or 'Qwen' in model_name:
                print("\n💡 QWEN REQUIRES NEWER TRANSFORMERS:")
                print("   Run: python3.9 -m pip install --upgrade transformers")
                print("   (Requires transformers>=4.37.0)")
                print("\n   OR use gpt2-large for now:")
                print("   Change DEFAULT_MODEL to 'gpt2-large' in web_story_server_enhanced.py")
            else:
                print("\n💡 Troubleshooting:")
                print("   1. Ensure internet connection for first-time download")
                print("   2. Check ~/.cache/huggingface/ permissions")
                print("   3. Try 'gpt2-large' for best quality on your hardware")
            
            raise RuntimeError(f"Model initialization failed: {error_msg[:200]}")
        
        # Story state
        self.story_history: List[str] = []
        self.user_actions: List[str] = []
        self.characters: Dict[str, Dict] = {}
        self.locations: set = set()
        self.current_beat = StoryBeat.EXPOSITION
        self.beat_counter = 0
        
        # PLAYER PERSONALITY TRACKING
        self.player_profile = PlayerProfile()
        print("✓ Player profiling enabled - tracking personality and choices\n")
        
        # ENHANCED narrative parameters - BEST PRACTICES from top story models
        self.max_context_length = 2048  # TinyLlama supports longer context
        self.generation_length = 100  # Shorter, punchier responses (was 250)
        
        # Dynamic temperature (will vary by context)
        self.base_temperature = 0.85  # Higher for creativity
        self.temperature = self.base_temperature
        
        # Nucleus sampling with better balance
        self.top_p = 0.92  # Sweet spot for creative variety
        self.top_k = 50  # Allow more options
        
        # Advanced anti-repetition (frequency > repetition for stories)
        self.repetition_penalty = 1.15  # Lighter, let frequency_penalty do heavy lifting
        
        # Quality parameters
        self.no_repeat_ngram_size = 4  # Prevent 4-word phrase repetition
        self.length_penalty = 1.0  # Neutral - allow natural stopping
        self.min_new_tokens = 40  # Ensure complete thoughts (at least 1-2 sentences)
        
        # Context management for long stories
        self.key_events = []  # Track important moments to keep in context
        
    def start_story(self, initial_prompt: Optional[str] = None, genre: str = "mystery") -> str:
        """
        Start a new story with GENRE-CONSTRAINED opening
        
        Args:
            initial_prompt: Custom story opening
            genre: Story genre (mystery/detective, romcom/romance, horror)
            
        Returns:
            Generated story opening
        """
        # Initialize genre constraints
        self.current_genre = genre
        self.genre_config = GenreConfig.get_config(genre)
        self.genre_beat_index = 0
        self.genre_elements = self.genre_config["story_elements"].copy()
        
        print(f"\n📖 Starting {self.genre_config['name'].upper()} story with genre constraints")
        print(f"   Narrative beats: {len(self.genre_config['beats'])} stages")
        print(f"   Current beat: {self.genre_config['beats'][0]}\n")
        
        if initial_prompt:
            self.story_history = [initial_prompt]
            prompt = initial_prompt
        else:
            # Genre-specific CONSTRAINED openings
            openings = {
                "mystery": "Detective Sarah Chen stood at the crime scene, rain drumming on her umbrella. The victim—Marcus Thornton, investment banker—lay in his locked study, no signs of forced entry. The only clue: a cryptic note reading 'The past always collects its debts.' Sarah's instincts screamed that this murder was connected to an old case, one she thought she'd buried years ago.",
                
                "detective": "The body was discovered at 6 AM by the janitor. Detective Rodriguez examined the scene: office door locked from inside, windows sealed, victim—tech CEO James Morrison—slumped at his desk. No weapon found. The computer screen still glowed with an unsent email: 'I know what you did. Tonight, everyone knows.' This wasn't suicide. This was murder staged to look like one.",
                
                "romcom": "Emma grabbed for the last croissant at exactly the same moment as someone else. 'That's mine,' she said, not looking up. 'Actually, I was here first,' a deep voice replied. She glanced up into the most annoyingly handsome face she'd ever seen. Great. Just great. Her ex-boyfriend's best friend, Jake Morrison, the one person in Seattle she'd successfully avoided for six months. Until now.",
                
                "romance": "The coffee shop meet-cute wasn't supposed to be a disaster. But here was Alex, standing in front of Jordan with latte all over their shirt, apologizing profusely while trying not to notice how gorgeous Jordan looked even while annoyed. 'This is the worst first impression ever,' Alex stammered. Jordan's lips quirked into an almost-smile. 'Second impression might be better. I'm Jordan.' A pause. 'Want to try this again with less coffee?'",
                
                "horror": "The house on Blackwood Lane had been empty for thirty years. Everyone knew why—the Marrow family disappeared without explanation, leaving dinner on the table, doors unlocked. But Sarah needed cheap rent, and legends didn't pay bills. As she turned the key, the door swung open on its own. Inside, the smell hit her: not decay, but something older. Something wrong. And from upstairs, unmistakably, came the sound of children laughing.",
                
                "thriller": "The train would arrive in thirty seconds, and Marcus had a choice to make. The briefcase in his hands contained either salvation or damnation—he hadn't dared to look inside. The man who'd handed it to him three hours ago was now dead, a 'suicide' the news would call it. Marcus's hands trembled. Platform security cameras swiveled his direction. Twenty seconds. In his pocket, his phone buzzed: 'Open the case or they kill your daughter.' Fifteen seconds.",
                
                "drama": "Rachel hadn't spoken to her sister in eight years, but here she was, standing in the hospital hallway, holding a cup of terrible coffee, waiting for news that would change everything. The doctor emerged, expression carefully neutral. 'She's asking for you,' he said. 'But Rachel...' He hesitated. 'She doesn't remember. The accident took the last decade. She thinks it's 2015. She thinks you're still friends.'"
            }
            
            prompt = openings.get(genre, openings["mystery"])
            self.story_history = [prompt]
        
        # Generate GENRE-CONSTRAINED continuation
        current_beat = self.genre_config["beats"][self.genre_beat_index]
        
        # For GPT-2, don't use complex instructions - just let it continue the story naturally
        # The model works best by example, not by instruction
        system_instruction = ""  # GPT-2 doesn't follow instructions well
        
        # Generate initial story with auto-continuation until user choice needed
        full_story = self._generate_until_user_choice(
            prompt,
            system_instruction=system_instruction,
            current_beat=current_beat,
            recent_action=""
        )
        
        self.story_history.append(full_story)
        self._extract_story_elements(prompt + " " + full_story)
        self._extract_genre_elements(full_story)
        
        return prompt + "\n\n" + full_story
    
    def process_user_action(self, user_input: str) -> Tuple[str, str]:
        """
        Process user's action with enhanced narrative adaptation
        
        Args:
            user_input: User's choice/action
            
        Returns:
            Tuple of (status, continuation)
        """
        # Validate user input
        validation = self._validate_user_input(user_input)
        
        if validation["status"] == "rejected":
            return "rejected", validation["message"]
        
        # ANALYZE PLAYER PERSONALITY from this action
        detected_traits = self.player_profile.analyze_action(user_input)
        
        # Add user action to history
        self.user_actions.append(user_input)
        
        # Generate story continuation with enhanced context awareness
        context = self._build_context_with_story_elements(recent_action=user_input, max_history=2)
        current_beat = self.genre_config["beats"][self.genre_beat_index] if self.genre_config else "story_development"
        
        # Build system instruction
        player_guidance = self.player_profile.get_narrative_guidance()
        severity = validation.get("severity", "normal")
        
        system_instruction = self._build_continuation_instruction(severity, player_guidance, current_beat)
        
        # Generate with auto-continuation until user choice
        adapted_story = self._generate_until_user_choice(
            f"{context}\n\n[Action: {user_input}]",
            system_instruction=system_instruction,
            current_beat=current_beat,
            recent_action=user_input
        )
        
        # Update story history
        self.story_history.append(f"[{user_input}]")
        self.story_history.append(adapted_story)
        
        # Update narrative beat
        self._update_story_beat()
        
        return validation["status"], adapted_story
    
    def _validate_user_input(self, user_input: str) -> Dict:
        """Validate user input (same as original)"""
        user_lower = user_input.lower().strip()
        
        if len(user_lower) < 3:
            return {
                "status": "rejected",
                "message": "❌ Error: Please provide a meaningful action or choice."
            }
        
        meta_phrases = [
            "what is", "how do i", "can you", "tell me",
            "explain", "define", "who are you", "what are you"
        ]
        
        if any(phrase in user_lower for phrase in meta_phrases):
            return {
                "status": "rejected",
                "message": "❌ Error: Please stay in character. Describe what your character does."
            }
        
        absurd_markers = [
            "turns into", "becomes god", "teleports to mars",
            "destroys the universe", "time travel", "magic powers"
        ]
        
        absurdity_level = sum(1 for marker in absurd_markers if marker in user_lower)
        
        if absurdity_level > 2:
            return {
                "status": "rejected",
                "message": "❌ Error: Too unrealistic. Try something more grounded."
            }
        elif absurdity_level > 0:
            return {"status": "adapted", "severity": "high"}
        
        dark_markers = ["kills", "murder", "destroys", "attack", "stab", "shoot"]
        if any(marker in user_lower for marker in dark_markers):
            return {"status": "adapted", "severity": "dark"}
        
        return {"status": "accepted", "severity": "normal"}
    
    def _adapt_story_to_action(self, user_action: str, validation: Dict) -> str:
        """
        Adapt story with ENHANCED narrative guidance AND player personality
        """
        context = self._build_context()
        severity = validation.get("severity", "normal")
        
        # Get player personality guidance
        player_guidance = self.player_profile.get_narrative_guidance()
        
        if self.use_enhanced_prompts:
            # ENHANCED storytelling instructions WITH PLAYER PROFILING
            if severity == "dark":
                prompt = f"{context}\n\nAction: {user_action}"
                system_instruction = f"""
{STORYTELLING_FRAMEWORK}

{player_guidance}

A dark, consequential action has occurred. Write what happens next with:
- Visceral, immediate sensory details of the moment
- Authentic emotional reactions from characters witnessing this
- Realistic physical and psychological consequences
- Moral weight and character-revealing choices
- Build toward either justice, redemption, or tragedy
- Adapt NPC reactions based on player's personality profile

{STORY_EXAMPLES}

Continue the story:
"""
            elif severity == "high":
                prompt = f"{context}\n\nAction: {user_action}"
                system_instruction = f"""
{STORYTELLING_FRAMEWORK}

{player_guidance}

The character attempts something unusual. Write what happens with:
- Grounded, realistic outcome (may not work as expected)
- Creative problem-solving or unexpected twist
- Character's reaction to the reality vs. expectation
- Move plot forward despite (or because of) the unusual attempt
- Reflect player's demonstrated personality in the outcome

{STORY_EXAMPLES}

Continue the story:
"""
            else:
                prompt = f"{context}\n\nAction: {user_action}"
                system_instruction = f"""
{STORYTELLING_FRAMEWORK}

{player_guidance}

Continue the narrative naturally. Write the next scene with:
- Show the immediate consequence of this action
- Reveal character through behavior and dialogue
- Advance plot with new information or complications
- Build tension and reader engagement
- Use vivid sensory details and varied pacing
- Tailor story developments to match player's personality and choices

{STORY_EXAMPLES}

Continue the story:
"""
        else:
            # Basic instructions (fallback)
            prompt = f"{context}\n\n{user_action}"
            if severity == "dark":
                system_instruction = "Show realistic consequences of this dark action."
            elif severity == "high":
                system_instruction = "Show what realistically happens from this unusual action."
            else:
                system_instruction = "Continue the story naturally."
        
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
        temperature: float = None,
        max_length: int = None
    ) -> str:
        """
        Generate text with OPTIMIZED settings for instruction-tuned models
        
        Supports both GPT-2 and Llama/Phi/Mistral instruction formats
        """
        if temperature is None:
            temperature = self.temperature
        if max_length is None:
            max_length = self.generation_length
        
        # Detect if using instruction-tuned model
        is_tinyllama = 'tinyllama' in self.model_name.lower()
        is_llama = 'llama' in self.model_name.lower()
        is_instruct_model = any(x in self.model_name.lower() for x in ['llama', 'phi', 'mistral', 'instruct', 'chat'])
        
        # Format prompt based on model type
        if is_tinyllama:
            # TinyLlama uses LLaMA 2 chat format - optimized for action-driven narrative
            if system_instruction:
                full_prompt = f"""<|system|>
You are writing an action-driven {self.current_genre or 'mystery'} story. Keep it punchy and plot-focused.

RULES:
- Write 2-3 short paragraphs maximum
- Focus on actions, dialogue, and immediate events
- Avoid lengthy descriptions or exposition
- Drive the plot forward
- End with tension or a decision point

{system_instruction}</s>
<|user|>
{prompt}</s>
<|assistant|>
"""
            else:
                full_prompt = f"""<|user|>
{prompt}</s>
<|assistant|>
"""
        elif is_llama:
            # LLaMA 3.2 uses specific instruction format
            if system_instruction:
                full_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a creative storytelling AI. Write compelling, coherent narrative prose in the specified genre.
{system_instruction}<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
            else:
                full_prompt = f"""<|begin_of_text|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
        elif is_instruct_model and system_instruction:
            # Generic instruction format for other models (Phi, Mistral, etc.)
            full_prompt = f"""<|system|>
You are a creative storytelling AI. Write compelling, coherent narrative prose.
{system_instruction}<|end|>
<|user|>
{prompt}<|end|>
<|assistant|>
"""
        elif system_instruction:
            # Simplified format for GPT-2 - just the prompt, instructions confuse it
            full_prompt = prompt
        else:
            full_prompt = prompt
        
        # Tokenize with attention mask
        encoded = self.tokenizer(
            full_prompt,
            return_tensors='pt',
            max_length=self.max_context_length,
            truncation=True,
            padding=False
        )
        inputs = encoded['input_ids']
        attention_mask = encoded.get('attention_mask', None)
        
        # ADVANCED generation with techniques from best story models
        generation_kwargs = {
            'max_new_tokens': max_length,  # Use max_new_tokens instead of max_length
            'min_new_tokens': self.min_new_tokens,  # Ensure complete thoughts
            'num_return_sequences': 1,
            'pad_token_id': self.tokenizer.eos_token_id,
            'eos_token_id': self.tokenizer.eos_token_id,
            'no_repeat_ngram_size': self.no_repeat_ngram_size,
            'length_penalty': self.length_penalty,
            'early_stopping': False,
        }
        
        # Add attention mask if available
        if attention_mask is not None:
            generation_kwargs['attention_mask'] = attention_mask
        
        # Use appropriate generation method for each model
        if is_instruct_model:
            # Modern models: use nucleus sampling with good parameters
            generation_kwargs.update({
                'do_sample': True,
                'temperature': temperature,
                'top_p': self.top_p,
                'top_k': self.top_k,
                'repetition_penalty': self.repetition_penalty,
            })
        else:
            # GPT-2: traditional sampling
            generation_kwargs.update({
                'do_sample': True,
                'temperature': temperature,
                'top_p': self.top_p,
                'top_k': self.top_k,
                'repetition_penalty': self.repetition_penalty,
            })
        
        with torch.no_grad():
            outputs = self.model.generate(inputs, **generation_kwargs)
        
        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract only new content based on model type
        if is_tinyllama:
            # TinyLlama: Extract content after assistant tag
            if "<|assistant|>" in generated_text:
                generated_text = generated_text.split("<|assistant|>")[-1].strip()
            # Remove end tokens
            generated_text = generated_text.split("</s>")[0].strip()
            generated_text = generated_text.split("<|user|>")[0].strip()
        elif is_llama:
            # LLaMA 3.2: Extract content after assistant header
            if "<|start_header_id|>assistant<|end_header_id|>" in generated_text:
                generated_text = generated_text.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()
            # Remove end tokens
            generated_text = generated_text.split("<|eot_id|>")[0].strip()
            generated_text = generated_text.split("<|end_of_text|>")[0].strip()
        elif is_instruct_model:
            # For other instruct models, extract assistant response
            if "<|assistant|>" in generated_text:
                generated_text = generated_text.split("<|assistant|>")[-1].strip()
                generated_text = generated_text.split("<|end|>")[0].strip()
            else:
                # Fallback: remove prompt
                generated_text = generated_text[len(full_prompt):].strip()
        else:
            # For GPT-2: Extract new tokens only
            prompt_length = len(self.tokenizer.encode(prompt, add_special_tokens=False))
            new_tokens = outputs[0][prompt_length:]
            generated_text = self.tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
        
        # Aggressive filtering of garbage output
        if generated_text:
            # Remove incomplete sentences at the end
            sentences = generated_text.split('. ')
            if len(sentences) > 1 and not generated_text.endswith(('.', '!', '?', '"')):
                generated_text = '. '.join(sentences[:-1]) + '.'
            
            # Filter out code/HTML/gibberish
            garbage_indicators = [
                '<div', '<html', '<script', '<!--', 'function(', 'document.', 
                'var ', 'let ', 'const ', '.getElementById', 'padding:', 'margin:',
                'class=', 'id=', 'style=', '{', '}', '=>', 'import ', 'export '
            ]
            
            # Check if output contains code
            has_code = any(indicator in generated_text for indicator in garbage_indicators)
            
            if has_code:
                # This is code garbage, not a story - reject it
                print("⚠️  Model generated code/HTML instead of story - rejecting")
                return ""
            
            # Remove any meta-text that slipped through
            meta_markers = ['[edit]', '**[User', '[User response', 'Chapter ', '[Story context']
            for marker in meta_markers:
                if marker in generated_text:
                    generated_text = generated_text.split(marker)[0].strip()
            
            # Remove any text after common breaking points
            if '---' in generated_text:
                generated_text = generated_text.split('---')[0].strip()
        
        return generated_text
    
    def _get_dynamic_temperature(self, context: str, iteration: int) -> float:
        """Vary temperature based on narrative context (technique from best models)"""
        context_lower = context.lower()
        
        # Action/thriller scenes: higher temperature for unpredictability
        action_keywords = ['fight', 'chase', 'explosion', 'shot', 'ran', 'attack', 'escape']
        if any(kw in context_lower for kw in action_keywords):
            return min(1.0, self.base_temperature + 0.15)
        
        # Dialogue: lower temperature for realistic speech
        if '"' in context or '"' in context or '"' in context:
            return max(0.65, self.base_temperature - 0.2)
        
        # Mystery/investigation: medium-low for logical coherence
        investigation_keywords = ['evidence', 'clue', 'suspect', 'investigate', 'examined']
        if any(kw in context_lower for kw in investigation_keywords):
            return max(0.7, self.base_temperature - 0.15)
        
        # Later iterations: slightly lower for consistency
        if iteration > 3:
            return max(0.75, self.base_temperature - 0.1)
        
        return self.base_temperature
    
    def _calculate_perplexity(self, text: str) -> float:
        """Calculate perplexity to detect garbage or overly generic text"""
        try:
            inputs = self.tokenizer.encode(text, return_tensors='pt', truncation=True, max_length=512)
            with torch.no_grad():
                outputs = self.model(inputs, labels=inputs)
                loss = outputs.loss
                perplexity = torch.exp(loss).item()
            return perplexity
        except:
            return 0.0  # If calculation fails, assume OK
    
    def _is_quality_text(self, text: str) -> bool:
        """Check if generated text meets quality standards (perplexity-based)"""
        if not text or len(text) < 20:
            return False
        
        perplexity = self._calculate_perplexity(text)
        
        # Skip quality check if perplexity calculation failed
        if perplexity == 0.0:
            return True
        
        # Adjusted thresholds for instruction-tuned models (lower perplexity is normal)
        # Too high = garbage/nonsense
        if perplexity > 500:
            print(f"⚠️  Text rejected: perplexity too high ({perplexity:.1f}) - likely garbage")
            return False
        
        # For instruction models, very low perplexity is actually GOOD (confident, coherent)
        # Only reject if suspiciously low (< 2.0 indicates memorization)
        if perplexity < 2.0:
            print(f"⚠️  Text rejected: perplexity too low ({perplexity:.1f}) - possible memorization")
            return False
        
        return True
    
    def _generate_until_user_choice(self, prompt: str, system_instruction: str, current_beat: str, recent_action: str = "") -> str:
        """
        Generate story segments continuously until reaching a point requiring user input.
        Uses story database to inject relevant characters, locations, and events.
        
        Args:
            prompt: Current story context
            system_instruction: Generation instructions
            current_beat: Current narrative beat
            recent_action: Most recent user action (for context relevance)
            
        Returns:
            Multi-paragraph story ending with user prompt
        """
        full_continuation = ""
        max_iterations = 3  # Reduced from 5 for faster responses
        max_paragraphs = 4  # Reduced from 8 - shorter story segments
        
        for iteration in range(max_iterations):
            # Check if we've generated enough content - offer continuation
            paragraph_count = full_continuation.count('\n\n') + 1 if full_continuation else 0
            
            if paragraph_count >= max_paragraphs and iteration > 2:
                # Only ask to continue if we've done at least 3 iterations
                full_continuation += "\n\n**[Continue story? Type 'continue' or provide your response]**"
                return full_continuation.strip()
            
            # Build context for this iteration
            if iteration == 0:
                # First iteration: use the original prompt
                current_context = prompt
            else:
                # Subsequent iterations: use only the most recent generated content
                recent_parts = full_continuation.split('\n\n')
                # Take last 1-2 paragraphs to maintain context
                current_context = '\n\n'.join(recent_parts[-2:]) if len(recent_parts) > 1 else full_continuation
            
            # Dynamic temperature based on context
            context_temp = self._get_dynamic_temperature(current_context, iteration)
            
            segment = self._generate_text(
                current_context,
                system_instruction="",
                max_length=100,  # Shorter, faster responses
                temperature=context_temp
            )
            
            # Skip if segment is empty, whitespace, or was rejected as garbage
            if not segment or not segment.strip():
                print(f"⚠️  Generation failed or returned garbage on iteration {iteration + 1}")
                # If first iteration failed, try one more time with shorter length
                if iteration == 0:
                    print("   Retrying with shorter max_length...")
                    segment = self._generate_text(
                        current_context,
                        system_instruction="",
                        max_length=60  # Even shorter for retry
                    )
                    if not segment or not segment.strip():
                        break
                else:
                    break
            
            # Quality check with perplexity (skip for GPT-2, only for instruct models)
            is_instruct = any(x in self.model_name.lower() for x in ['llama', 'phi', 'mistral', 'qwen', 'instruct'])
            if is_instruct and not self._is_quality_text(segment):
                print(f"   Retrying due to quality issues...")
                # Try once more with adjusted temperature
                segment = self._generate_text(
                    current_context,
                    system_instruction="",
                    max_length=100,
                    temperature=self.base_temperature - 0.1
                )
                if not self._is_quality_text(segment):
                    continue  # Skip this iteration
            
            # Validate genre consistency
            if self.genre_config and not self._validate_genre_consistency(segment):
                print(f"⚠️  Genre drift detected, regenerating...")
                segment = self._regenerate_with_stronger_constraints(current_context, current_beat)
            
            full_continuation += "\n\n" + segment if full_continuation else segment
            
            # Track key events for sliding window context
            self._track_key_event(segment)
            
            # Check if this is a natural decision point
            # Look for indicators that the character needs to make a choice
            decision_indicators = [
                '?',  # Question posed to character
                'what will you',
                'what do you',
                'you must',
                'you need to',
                'you should',
                'you could',
                'decision',
                'choice',
                'which way',
                'what next',
            ]
            
            segment_lower = segment.lower()
            is_decision_point = any(indicator in segment_lower for indicator in decision_indicators)
            
            # Also check if it ends with a question or cliffhanger
            ends_with_question = segment.rstrip().endswith('?')
            
            if is_decision_point or ends_with_question:
                # Natural decision point reached
                full_continuation += "\n\n**[What do you do?]**"
                return full_continuation.strip()
        
        # If we've done all iterations and still no clear decision point,
        # just add a generic prompt
        full_continuation += "\n\n**[What do you do?]**"
        
        return full_continuation.strip()
    
    def _build_continuation_instruction(self, severity: str, player_guidance: str, current_beat: str) -> str:
        """
        Build system instruction for story continuation based on action severity.
        
        Args:
            severity: Action severity level
            player_guidance: Player personality guidance
            current_beat: Current narrative beat
            
        Returns:
            System instruction string
        """
        if not self.use_enhanced_prompts:
            return "Continue the story naturally and create engaging narrative."
        
        base_instruction = f"""{STORYTELLING_FRAMEWORK}

{player_guidance}

Current narrative stage: {current_beat}
"""
        
        if severity == "dark":
            return base_instruction + """
A dark, consequential action has occurred. Write what happens next with:
- Visceral, immediate sensory details
- Authentic emotional reactions from witnesses
- Realistic physical and psychological consequences
- Moral weight and character development
- Build toward justice, redemption, or tragedy
"""
        elif severity == "high":
            return base_instruction + """
The character attempts something unusual. Show:
- Grounded, realistic outcome (may surprise them)
- Creative problem-solving or unexpected twists
- Character's reaction to reality vs. expectation
- How this moves the plot forward
"""
        else:
            return base_instruction + """
Continue the narrative naturally with:
- Immediate consequence of the action
- Character revelation through behavior/dialogue  
- New information or complications
- Vivid sensory details and varied pacing
- Build tension and engagement
"""
    
    def _build_context(self, max_history: int = 3) -> str:
        """Build context from recent story history"""
        recent = self.story_history[-max_history:] if self.story_history else []
        return "\n\n".join(recent)
    
    def _track_key_event(self, text: str):
        """Track important story events for sliding window context"""
        text_lower = text.lower()
        
        # Major event indicators
        key_indicators = [
            'died', 'killed', 'murdered', 'death',
            'discovered', 'found', 'revealed', 'realized',
            'decided', 'chose', 'agreed',
            'arrived', 'left', 'escaped',
            'betrayed', 'confessed', 'admitted'
        ]
        
        # If this segment contains a key event, save it
        if any(indicator in text_lower for indicator in key_indicators):
            # Only keep the most important sentence
            sentences = text.split('.')
            for sentence in sentences:
                if any(indicator in sentence.lower() for indicator in key_indicators):
                    self.key_events.append(sentence.strip() + '.')
                    # Keep only last 5 key events
                    if len(self.key_events) > 5:
                        self.key_events.pop(0)
                    break
    
    def _build_context_with_story_elements(self, recent_action: str = "", max_history: int = 3) -> str:
        """
        Build enhanced context with SLIDING WINDOW approach (technique from best models).
        
        Keeps: Opening paragraph + key events + recent paragraphs
        This maintains story continuity while staying within context limits.
        
        Args:
            recent_action: The most recent user action or event
            max_history: Number of recent story segments to include
            
        Returns:
            Enhanced context string with story element reminders
        """
        # SLIDING WINDOW: Keep opening + key events + recent content
        context_parts = []
        
        # Always include the opening (establishes tone/setting)
        if self.story_history:
            context_parts.append(self.story_history[0])
        
        # Add key events (important moments to remember)
        if self.key_events:
            context_parts.extend(self.key_events[-3:])  # Last 3 key events
        
        # Add recent history
        recent = self.story_history[-max_history:] if len(self.story_history) > 1 else []
        context = "\n\n".join(context_parts + recent)
        
        # Extract keywords from recent action to find relevant elements
        action_lower = recent_action.lower() if recent_action else ""
        context_lower = context.lower()
        
        # Find relevant characters (mentioned recently or in action)
        relevant_chars = []
        for char_name, char_data in self.characters.items():
            char_lower = char_name.lower()
            # Character is relevant if mentioned in action or appeared multiple times
            if char_lower in action_lower or char_lower in context_lower or char_data.get('mentions', 0) > 2:
                relevant_chars.append(char_name)
        
        # Find relevant locations
        relevant_locs = []
        for location in self.locations:
            loc_lower = location.lower()
            if loc_lower in action_lower or loc_lower in context_lower:
                relevant_locs.append(location)
        
        # Build context reminder (subtle, natural language)
        # Note: For GPT-2, adding meta-text confuses it, so we DON'T inject hints
        # The model will naturally reference characters/locations if they're in recent context
        context_hints = []
        
        # Skip hint injection for now - it confuses GPT-2
        # if relevant_chars and len(relevant_chars) <= 3:
        #     char_list = ", ".join(relevant_chars[:3])
        #     context_hints.append(f"Key people involved: {char_list}.")
        
        # Just return clean context without meta-markers
        return context
    
    def _extract_story_elements(self, text: str):
        """Extract characters and locations (same as original)"""
        # Simple extraction
        words = text.split()
        capitalized = [w for w in words if w and w[0].isupper() and len(w) > 2]
        
        for word in capitalized:
            clean = word.strip('.,!?";:')
            if clean and clean not in ['The', 'A', 'An', 'But', 'And', 'Or']:
                if clean not in self.characters:
                    self.characters[clean] = {
                        'first_mention': len(self.story_history),
                        'mentions': 1
                    }
                else:
                    self.characters[clean]['mentions'] += 1
    
    def _update_story_beat(self):
        """Progress narrative structure"""
        self.beat_counter += 1
        
        if self.beat_counter >= 2 and self.current_beat == StoryBeat.EXPOSITION:
            self.current_beat = StoryBeat.INCITING_INCIDENT
        elif self.beat_counter >= 5 and self.current_beat == StoryBeat.INCITING_INCIDENT:
            self.current_beat = StoryBeat.RISING_ACTION
        elif self.beat_counter >= 10 and self.current_beat == StoryBeat.RISING_ACTION:
            self.current_beat = StoryBeat.CLIMAX
        elif self.beat_counter >= 13 and self.current_beat == StoryBeat.CLIMAX:
            self.current_beat = StoryBeat.FALLING_ACTION
        elif self.beat_counter >= 15 and self.current_beat == StoryBeat.FALLING_ACTION:
            self.current_beat = StoryBeat.RESOLUTION
    
    def get_player_profile(self) -> Dict:
        """Get player personality profile data"""
        return {
            "traits": self.player_profile.traits,
            "archetype": self.player_profile.get_archetype(),
            "total_decisions": self.player_profile.decision_count,
            "personality_summary": self.player_profile.get_narrative_guidance()
        }
    
    def get_story_summary(self) -> str:
        """Get comprehensive story summary WITH PLAYER PROFILE"""
        summary = f"📖 STORY STATE\n{'=' * 50}\n\n"
        summary += f"Current Beat: {self.current_beat.value.upper()}\n"
        summary += f"Actions Taken: {len(self.user_actions)}\n"
        summary += f"Story Segments: {len(self.story_history)}\n\n"
        
        # Add player personality summary
        archetype = self.player_profile.get_archetype()
        summary += f"🧠 Player Archetype: {archetype}\n"
        summary += f"Decisions Analyzed: {self.player_profile.decision_count}\n\n"
        
        if self.characters:
            summary += f"Characters ({len(self.characters)}):\n"
            for name, data in list(self.characters.items())[:10]:
                summary += f"  - {name} (mentioned {data['mentions']}x)\n"
        
        summary += f"\n📝 Recent Story:\n{'-' * 50}\n"
        recent = self.story_history[-2:] if len(self.story_history) >= 2 else self.story_history
        summary += "\n\n".join(recent)
        
        return summary
    
    def _validate_genre_consistency(self, text: str) -> bool:
        """
        Validate that generated text stays within genre constraints
        
        Args:
            text: Generated story text
            
        Returns:
            True if text is genre-appropriate, False otherwise
        """
        if not self.genre_config:
            return True
        
        text_lower = text.lower()
        
        # Check for forbidden keywords
        violations = []
        for forbidden in self.genre_config.get("forbidden_keywords", []):
            if forbidden.lower() in text_lower:
                violations.append(f"forbidden keyword: {forbidden}")
                self.genre_violations.append(forbidden)
        
        # Check for genre-appropriate keywords (at least some should appear)
        genre_keyword_found = False
        for keyword in self.genre_config.get("tone_keywords", []):
            if keyword.lower() in text_lower:
                genre_keyword_found = True
                break
        
        if violations:
            print(f"⚠️  Genre drift detected: {', '.join(violations)}")
            return False
        
        return True
    
    def _regenerate_with_stronger_constraints(self, prompt: str, beat: str) -> str:
        """
        Regenerate text with stronger genre constraints
        
        Args:
            prompt: Original prompt
            beat: Current narrative beat
            
        Returns:
            Regenerated text with stronger constraints
        """
        print("🔄 Regenerating with stricter genre constraints...")
        
        if not self.genre_config:
            return self._generate_text(prompt)
        
        # Add explicit genre constraints to prompt
        strict_prompt = f"{prompt}\n\n"
        strict_prompt += f"CRITICAL: This is a {self.current_genre.upper()} story. "
        strict_prompt += f"Focus on: {', '.join(self.genre_config.get('tone_keywords', [])[:5])}. "
        strict_prompt += f"FORBIDDEN: {', '.join(self.genre_config.get('forbidden_keywords', [])[:5])}. "
        strict_prompt += f"Current story beat: {beat}."
        
        return self._generate_text(strict_prompt, max_length=200, temperature=0.7)
    
    def _generate_genre_template(self, beat: str) -> str:
        """
        Generate template-based text as fallback
        
        Args:
            beat: Current narrative beat
            
        Returns:
            Template-based story text
        """
        if not self.genre_config or self.current_genre not in ['mystery', 'horror', 'adventure']:
            return "The story continues in an unexpected direction..."
        
        templates = {
            'mystery': {
                'crime_discovered': "A perplexing mystery presents itself, demanding investigation.",
                'investigation_begins': "Clues begin to emerge as you investigate further.",
                'clue_found': "An important clue comes to light.",
                'suspect_identified': "A potential suspect emerges from the shadows.",
                'false_lead': "The trail leads somewhere unexpected.",
                'revelation': "A crucial revelation changes everything.",
                'confrontation': "The truth must be confronted.",
                'resolution': "The mystery finally unravels."
            },
            'horror': {
                'normal_world': "An unsettling atmosphere pervades the scene.",
                'first_sign': "Something isn't quite right...",
                'escalation': "The horror intensifies.",
                'revelation': "The true nature of the terror reveals itself.",
                'climax': "Terror reaches its peak.",
                'resolution': "The nightmare's grip begins to loosen."
            },
            'adventure': {
                'call_to_adventure': "A new adventure beckons.",
                'journey_begins': "The journey takes an exciting turn.",
                'challenge': "A formidable obstacle appears.",
                'discovery': "An amazing discovery awaits.",
                'climax': "The ultimate challenge presents itself.",
                'return': "The adventure nears its conclusion."
            }
        }
        
        genre_templates = templates.get(self.current_genre, {})
        return genre_templates.get(beat, "The story continues...")
    
    def _extract_genre_elements(self, text: str):
        """
        Extract and track genre-specific elements
        
        Args:
            text: Story text to analyze
        """
        if not self.genre_config or not self.current_genre:
            return
        
        text_lower = text.lower()
        
        # Extract based on genre
        if self.current_genre == 'mystery':
            # Look for clues, suspects, evidence
            if 'clue' in text_lower or 'evidence' in text_lower:
                if 'clues' not in self.genre_elements:
                    self.genre_elements['clues'] = []
                self.genre_elements['clues'].append(text[:100])
            
            if 'suspect' in text_lower or 'accused' in text_lower:
                if 'suspects' not in self.genre_elements:
                    self.genre_elements['suspects'] = []
                self.genre_elements['suspects'].append(text[:100])
        
        elif self.current_genre == 'horror':
            # Track scares, threats
            if any(word in text_lower for word in ['terror', 'fear', 'scream', 'horror']):
                if 'scares' not in self.genre_elements:
                    self.genre_elements['scares'] = []
                self.genre_elements['scares'].append(text[:100])
        
        elif self.current_genre == 'adventure':
            # Track discoveries, challenges
            if 'discover' in text_lower or 'found' in text_lower:
                if 'discoveries' not in self.genre_elements:
                    self.genre_elements['discoveries'] = []
                self.genre_elements['discoveries'].append(text[:100])
    
    def get_genre_status(self) -> dict:
        """
        Get current genre tracking status
        
        Returns:
            Dictionary with genre information
        """
        return {
            'genre': self.current_genre,
            'current_beat': self.genre_config.get('beats', [])[self.genre_beat_index] if self.genre_config else None,
            'beat_progress': f"{self.genre_beat_index + 1}/{len(self.genre_config.get('beats', []))}" if self.genre_config else "N/A",
            'violations': self.genre_violations,
            'elements': self.genre_elements
        }


# CLI interface for testing
if __name__ == "__main__":
    print("=" * 70)
    print("  ENHANCED ADAPTIVE STORY GENERATOR")
    print("  Advanced Storytelling with Quality Models")
    print("=" * 70)
    print()
    
    print("Select model quality:")
    print("  1. Fast (gpt2) - Quick, basic quality")
    print("  2. Balanced (gpt2-medium) - Good speed and quality")
    print("  3. Quality (gpt2-large) - RECOMMENDED for best results")
    print("  4. Maximum (gpt2-xl) - Excellent but slow")
    print("  5. Amazing (gpt-neo-1.3B) - Highest quality")
    
    choice = input("\nChoose (1-5, default=3): ").strip() or "3"
    
    models = {
        "1": "gpt2",
        "2": "gpt2-medium",
        "3": "gpt2-large",
        "4": "gpt2-xl",
        "5": "EleutherAI/gpt-neo-1.3B"
    }
    
    model = models.get(choice, "gpt2-large")
    
    print("\nSelect genre:")
    print("  1. Mystery")
    print("  2. Horror")
    print("  3. Adventure")
    print("  4. Thriller")
    print("  5. Drama")
    
    genre_choice = input("\nChoose (1-5, default=1): ").strip() or "1"
    genres = {"1": "mystery", "2": "horror", "3": "adventure", "4": "thriller", "5": "drama"}
    genre = genres.get(genre_choice, "mystery")
    
    # Initialize enhanced engine
    engine = AdaptiveStoryEngine(model_name=model, use_enhanced_prompts=True)
    
    print(f"\n🎬 Starting {genre} story with enhanced quality...\n")
    initial_story = engine.start_story(genre=genre)
    
    print("📖 STORY:")
    print("─" * 70)
    print(initial_story)
    print("─" * 70)
    print()
    
    # Main loop
    while True:
        print("❓ What happens next?")
        user_input = input("→ ").strip()
        
        if not user_input:
            continue
        
        if user_input.lower() == 'quit':
            print("\n👋 Story concluded. Thank you!")
            break
        
        if user_input.lower() == 'summary':
            print(engine.get_story_summary())
            continue
        
        print("\n🤔 Crafting narrative response...\n")
        status, continuation = engine.process_user_action(user_input)
        
        if status == "rejected":
            print(continuation)
            continue
        
        print("📖 STORY CONTINUES:")
        print("─" * 70)
        print(f"[You: {user_input}]\n")
        print(continuation)
        print("─" * 70)
        print()
