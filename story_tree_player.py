"""
Story Tree Player - Plays pre-generated story trees with instant responses
Hybrid approach: uses tree for main path, AI for creative inputs
"""

import json
from typing import Dict, List, Optional
from difflib import SequenceMatcher
from adaptive_story_engine_enhanced import AdaptiveStoryEngine


class StoryTreePlayer:
    """Plays pre-generated story trees with instant responses"""
    
    def __init__(self, tree: Dict, use_ai_fallback: bool = True):
        """
        Initialize player with a story tree
        
        Args:
            tree: Story tree dictionary
            use_ai_fallback: Use AI for creative/unexpected inputs
        """
        self.tree = tree
        self.current_node_id = tree.get('start_node', 'start')
        self.history = []
        self.use_ai_fallback = use_ai_fallback
        self.ai_engine = None
        
        if use_ai_fallback:
            print("🤖 AI fallback enabled for creative inputs")
            self.ai_engine = AdaptiveStoryEngine(
                model_name='TinyLlama/TinyLlama-1.1B-Chat-v1.0',
                use_enhanced_prompts=True
            )
    
    def start(self) -> Dict:
        """Start the story, return opening node"""
        self.current_node_id = self.tree['start_node']
        node = self.tree['nodes'][self.current_node_id]
        self.history.append(self.current_node_id)
        
        return {
            'text': node['text'],
            'choices': node.get('choices', []),
            'is_ending': node.get('is_ending', False),
            'type': 'tree_node'
        }
    
    def make_choice(self, user_input: str) -> Dict:
        """
        Process user input and return next story segment
        
        Args:
            user_input: User's choice or freeform input
            
        Returns:
            Story response with text and choices
        """
        current_node = self.tree['nodes'][self.current_node_id]
        
        # Check if current node has choices
        if not current_node.get('choices'):
            return {
                'text': "**Story Complete**\n\nWould you like to play again?",
                'choices': [],
                'is_ending': True,
                'type': 'ending'
            }
        
        # Try to match user input to available choices
        best_match = self._match_to_choice(user_input, current_node['choices'])
        
        if best_match:
            # Follow tree path
            next_node_id = best_match['leads_to']
            
            if next_node_id in self.tree['nodes']:
                self.current_node_id = next_node_id
                self.history.append(next_node_id)
                next_node = self.tree['nodes'][next_node_id]
                
                return {
                    'text': next_node['text'],
                    'choices': next_node.get('choices', []),
                    'is_ending': next_node.get('is_ending', False),
                    'matched_choice': best_match['text'],
                    'type': 'tree_node'
                }
            else:
                # Node not generated, create ending
                return {
                    'text': "This path hasn't been fully developed yet.\n\n**Story Complete**",
                    'choices': [],
                    'is_ending': True,
                    'type': 'incomplete_path'
                }
        
        # No match found - use AI fallback for creative input
        if self.use_ai_fallback and self.ai_engine:
            return self._handle_creative_input(user_input, current_node)
        else:
            # No AI fallback, show available choices
            choices_text = "\n".join([f"- {c['text']}" for c in current_node['choices']])
            return {
                'text': f"I didn't understand that. Please choose from:\n\n{choices_text}",
                'choices': current_node['choices'],
                'is_ending': False,
                'type': 'clarification'
            }
    
    def _match_to_choice(self, user_input: str, choices: List[Dict]) -> Optional[Dict]:
        """
        Match user input to closest choice using fuzzy matching
        
        Returns the choice if match confidence > 0.5, otherwise None
        """
        user_lower = user_input.lower().strip()
        
        # Direct match
        for choice in choices:
            if choice['text'].lower() == user_lower:
                return choice
        
        # Fuzzy match
        best_ratio = 0
        best_choice = None
        
        for choice in choices:
            choice_lower = choice['text'].lower()
            
            # Check if user input contains key words from choice
            choice_words = set(choice_lower.split())
            user_words = set(user_lower.split())
            word_overlap = len(choice_words & user_words) / max(len(choice_words), 1)
            
            # Also check sequence similarity
            seq_ratio = SequenceMatcher(None, user_lower, choice_lower).ratio()
            
            # Combined score
            score = max(word_overlap, seq_ratio)
            
            if score > best_ratio:
                best_ratio = score
                best_choice = choice
        
        # Return if confidence is high enough
        if best_ratio > 0.5:
            return best_choice
        
        return None
    
    def _handle_creative_input(self, user_input: str, current_node: Dict) -> Dict:
        """
        Handle creative/unexpected user input with AI
        
        Args:
            user_input: User's freeform input
            current_node: Current story node
            
        Returns:
            AI-generated response
        """
        print(f"🎨 Creative input detected: '{user_input}' - using AI...")
        
        # Build context from history
        context = self._get_story_context()
        
        # Generate AI response
        prompt = f"""Continue this story based on the character's creative action.

Story so far:
{context}

Current situation:
{current_node['text']}

The character's action: {user_input}

Write 2-3 short paragraphs showing what happens. Then present the same choices that were available before."""

        system_prompt = f"""You are continuing a {self.tree['genre']} story.
- Show the result of the character's action
- Keep it brief (2-3 paragraphs)
- Return to the main story path
- Stay consistent with established characters and setting"""

        ai_response = self.ai_engine._generate_text(prompt, system_prompt, max_length=120)
        
        # Return AI response but keep same choices (returns to main path)
        return {
            'text': ai_response + "\n\n*[Story returns to main path]*",
            'choices': current_node['choices'],
            'is_ending': False,
            'type': 'ai_creative',
            'creative_action': user_input
        }
    
    def _get_story_context(self, max_nodes: int = 3) -> str:
        """Get recent story context from history"""
        recent_nodes = self.history[-max_nodes:]
        context_parts = []
        
        for node_id in recent_nodes:
            if node_id in self.tree['nodes']:
                context_parts.append(self.tree['nodes'][node_id]['text'])
        
        return "\n\n".join(context_parts)
    
    def get_current_state(self) -> Dict:
        """Get current story state"""
        current_node = self.tree['nodes'].get(self.current_node_id, {})
        
        return {
            'current_node_id': self.current_node_id,
            'text': current_node.get('text', ''),
            'choices': current_node.get('choices', []),
            'is_ending': current_node.get('is_ending', False),
            'history': self.history.copy(),
            'story_title': self.tree.get('title', 'Untitled'),
            'genre': self.tree.get('genre', 'adventure')
        }
    
    def restart(self) -> Dict:
        """Restart the story from beginning"""
        self.current_node_id = self.tree['start_node']
        self.history = []
        return self.start()
    
    def save_progress(self, filename: str):
        """Save current progress"""
        progress = {
            'tree_title': self.tree.get('title', ''),
            'current_node_id': self.current_node_id,
            'history': self.history
        }
        
        with open(filename, 'w') as f:
            json.dump(progress, f, indent=2)
        
        print(f"💾 Progress saved to {filename}")
    
    def load_progress(self, filename: str):
        """Load saved progress"""
        with open(filename, 'r') as f:
            progress = json.load(f)
        
        self.current_node_id = progress['current_node_id']
        self.history = progress['history']
        
        print(f"📂 Progress loaded from {filename}")
        return self.get_current_state()


if __name__ == "__main__":
    # Test player
    from story_tree_generator import StoryTreeGenerator
    
    # Load or generate tree
    import os
    if os.path.exists('detective_story.json'):
        tree = StoryTreeGenerator.load_tree('detective_story.json')
    else:
        print("Generating new story tree...")
        generator = StoryTreeGenerator()
        tree = generator.generate_story_tree(genre='detective', num_nodes=15, max_depth=4)
        generator.save_tree('detective_story.json')
    
    # Play
    player = StoryTreePlayer(tree, use_ai_fallback=True)
    response = player.start()
    
    print(f"\n📖 {tree['title']}")
    print(f"{'='*60}\n")
    print(response['text'])
    print(f"\n{'='*60}")
    print("Choices:")
    for i, choice in enumerate(response['choices'], 1):
        print(f"  {i}. {choice['text']}")
    
    # Simulate some choices
    print("\n\n--- Testing choice matching ---")
    test_inputs = [
        "examine the body",  # Should match choice 1
        "look at the dead guy",  # Creative input
        "check clues"  # Fuzzy match to choice 2
    ]
    
    for test_input in test_inputs:
        print(f"\nUser: {test_input}")
        response = player.make_choice(test_input)
        print(f"Type: {response['type']}")
        print(f"Text: {response['text'][:100]}...")
