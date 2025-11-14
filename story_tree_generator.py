"""
Story Tree Generator - Creates pre-generated branching narratives with AI
Uses TinyLlama to generate a complete story tree once, then plays instantly
"""

import json
from typing import Dict, List, Optional
from adaptive_story_engine_enhanced import AdaptiveStoryEngine
import time


class StoryNode:
    """A single node in the story tree"""
    def __init__(self, node_id: str, text: str, choices: List[Dict] = None):
        self.node_id = node_id
        self.text = text
        self.choices = choices or []
        self.visited = False
    
    def to_dict(self):
        return {
            'node_id': self.node_id,
            'text': self.text,
            'choices': self.choices
        }


class StoryTreeGenerator:
    """Generates complete branching story trees using AI"""
    
    def __init__(self, model_name='TinyLlama/TinyLlama-1.1B-Chat-v1.0'):
        print("🌳 Initializing Story Tree Generator...")
        self.engine = AdaptiveStoryEngine(model_name=model_name, use_enhanced_prompts=True)
        self.tree = {}
        self.genre = None
        
    def generate_story_tree(self, genre: str, num_nodes: int = 25, max_depth: int = 5) -> Dict:
        """
        Generate a complete story tree for the specified genre
        
        Args:
            genre: Story genre (detective, war, adventure, etc.)
            num_nodes: Target number of story nodes
            max_depth: Maximum depth of branching
        
        Returns:
            Complete story tree dictionary
        """
        self.genre = genre
        self.tree = {
            'genre': genre,
            'title': '',
            'nodes': {},
            'characters': [],
            'locations': [],
            'start_node': 'start'
        }
        
        print(f"\n🎬 Generating {genre.upper()} story tree...")
        print(f"   Target: {num_nodes} nodes, max depth: {max_depth}")
        print(f"   This will take 3-5 minutes...\n")
        
        # Generate opening
        print("📝 Generating story opening...")
        opening = self._generate_opening(genre)
        
        # Extract metadata
        self.tree['title'] = self._extract_title(opening)
        self.tree['characters'] = self._extract_characters(opening)
        self.tree['locations'] = self._extract_locations(opening)
        
        # Create start node with initial choices
        start_choices = self._generate_initial_choices(opening, genre)
        self.tree['nodes']['start'] = {
            'node_id': 'start',
            'text': opening,
            'choices': start_choices,
            'depth': 0
        }
        
        # Generate branching paths
        nodes_to_generate = [choice['leads_to'] for choice in start_choices]
        generated_count = 1  # Start node counts
        
        while nodes_to_generate and generated_count < num_nodes:
            current_node_id = nodes_to_generate.pop(0)
            
            # Get parent context
            parent_context = self._get_path_to_node(current_node_id)
            depth = len(parent_context.split(' → '))
            
            if depth > max_depth:
                # Create ending node
                self._create_ending_node(current_node_id, parent_context)
                generated_count += 1
                continue
            
            # Generate node content
            print(f"📝 Generating node {generated_count}/{num_nodes}: {current_node_id} (depth {depth})")
            node_text = self._generate_node_content(current_node_id, parent_context, genre)
            
            # Check if this should be an ending
            is_ending = (
                depth >= max_depth - 1 or 
                generated_count >= num_nodes - 3 or
                self._is_natural_ending(node_text)
            )
            
            if is_ending:
                # Create ending node
                self.tree['nodes'][current_node_id] = {
                    'node_id': current_node_id,
                    'text': node_text,
                    'choices': [],
                    'is_ending': True,
                    'depth': depth
                }
            else:
                # Generate choices for this node
                choices = self._generate_choices(current_node_id, node_text, genre, depth)
                self.tree['nodes'][current_node_id] = {
                    'node_id': current_node_id,
                    'text': node_text,
                    'choices': choices,
                    'depth': depth
                }
                
                # Add new branches to queue
                for choice in choices:
                    if choice['leads_to'] not in self.tree['nodes']:
                        nodes_to_generate.append(choice['leads_to'])
            
            generated_count += 1
            time.sleep(0.5)  # Brief pause to prevent overwhelming the model
        
        print(f"\n✅ Story tree generated: {generated_count} nodes")
        print(f"   Title: {self.tree['title']}")
        print(f"   Characters: {', '.join(self.tree['characters'][:5])}")
        
        return self.tree
    
    def _generate_opening(self, genre: str) -> str:
        """Generate compelling story opening"""
        # Use existing genre openings from adaptive_story_engine
        openings = {
            "detective": "Detective Sarah Chen stood at the crime scene, rain drumming on her umbrella. The victim—Marcus Thornton, investment banker—lay in his locked study, no signs of forced entry. The only clue: a cryptic note reading 'The past always collects its debts.' Sarah's instincts screamed that this murder was connected to an old case, one she thought she'd buried years ago.",
            
            "war": "Sergeant Jake Morrison crouched in the muddy trench, artillery fire shaking the ground. His squad of eight had been holding this position for three days. Command just radioed: enemy forces massing for a major assault at dawn. With dwindling ammunition and two wounded soldiers, Jake had to make a call—hold the line or fall back to regroup.",
            
            "adventure": "The ancient map led you to this hidden temple deep in the Amazon rainforest. Dr. Elena Rodriguez examined the stone door covered in mysterious glyphs. Your guide, Carlos, nervously clutched his machete. 'The locals say this place is cursed,' he whispered. But the artifact you sought—the Emerald Eye—was supposedly inside. One wrong move could trigger the temple's deadly traps.",
            
            "horror": "The asylum had been abandoned for thirty years, but something was wrong. Emma clutched her flashlight as she stepped into the main hall. The urban exploration vlog had seemed like a good idea yesterday. Now, with her phone dead and her friends missing, she heard footsteps echoing from the floor above. The door behind her slammed shut. Someone—or something—didn't want her to leave.",
            
            "thriller": "The USB drive in your pocket contained evidence that could bring down a senator. Journalist Alex Carter had three hours before the deadline to publish. But the black SUV that had been following you just pulled up. Two men in suits stepped out. Your editor wasn't answering calls. You had to decide: run, hide, or confront them directly."
        }
        
        return openings.get(genre, openings["adventure"])
    
    def _generate_initial_choices(self, opening: str, genre: str) -> List[Dict]:
        """Generate 3-4 initial choices based on opening"""
        # Generate contextual choices using AI
        prompt = f"""Based on this {genre} story opening, generate 3 distinct choices the protagonist could make.

Story opening:
{opening}

List 3 choices in this exact format:
1. [Action-focused choice]
2. [Investigation/Analysis choice]  
3. [Social/Communication choice]

Keep each choice to 4-6 words."""

        system_prompt = "You are generating player choices for an interactive story. Be concise and action-oriented."
        
        response = self.engine._generate_text(prompt, system_prompt, max_length=80)
        
        # Parse choices (fallback to defaults if parsing fails)
        choices = self._parse_choices(response, genre)
        
        # Create choice objects
        choice_objects = []
        for i, choice_text in enumerate(choices[:3], 1):
            choice_objects.append({
                'text': choice_text,
                'leads_to': f'node_{i}',
                'type': ['action', 'investigate', 'social'][i-1]
            })
        
        return choice_objects
    
    def _parse_choices(self, response: str, genre: str) -> List[str]:
        """Parse AI response into choice list"""
        lines = [line.strip() for line in response.split('\n') if line.strip()]
        choices = []
        
        for line in lines:
            # Remove numbering
            cleaned = line.lstrip('0123456789.-) ').strip()
            if cleaned and len(cleaned) < 60:  # Reasonable length
                choices.append(cleaned)
        
        # Fallback defaults by genre
        defaults = {
            'detective': ['Examine the body', 'Search for clues', 'Question witnesses'],
            'war': ['Hold the position', 'Call for backup', 'Scout enemy lines'],
            'adventure': ['Enter the temple', 'Study the glyphs', 'Search the perimeter'],
            'horror': ['Go upstairs', 'Find another exit', 'Hide and wait'],
            'thriller': ['Run away', 'Confront them', 'Call the police']
        }
        
        if len(choices) < 3:
            choices = defaults.get(genre, defaults['adventure'])
        
        return choices[:3]
    
    def _generate_node_content(self, node_id: str, parent_context: str, genre: str) -> str:
        """Generate content for a story node"""
        # Extract the choice that led here
        choice_made = self._extract_choice_from_id(node_id)
        
        prompt = f"""Continue this {genre} story based on the character's action.

Story so far:
{parent_context}

Character's action: {choice_made}

Write 2-3 short paragraphs showing what happens as a direct result of this action. Keep the same characters and setting. Focus on immediate consequences and new developments."""

        system_prompt = f"""You are continuing a {genre} story. 
- Stay with the same characters
- Keep the same setting
- Show direct results of the action
- Create tension or reveal new information
- Write 2-3 paragraphs maximum"""

        return self.engine._generate_text(prompt, system_prompt, max_length=120)
    
    def _generate_choices(self, node_id: str, node_text: str, genre: str, depth: int) -> List[Dict]:
        """Generate 2-3 choices for a node"""
        # Fewer choices at deeper levels
        num_choices = 3 if depth < 3 else 2
        
        prompt = f"""Based on this story segment, generate {num_choices} distinct choices for what to do next.

Current situation:
{node_text[-300:]}  

List {num_choices} choices in format:
1. [Choice 1]
2. [Choice 2]
{"3. [Choice 3]" if num_choices == 3 else ""}

Each choice should be 4-6 words and action-oriented."""

        response = self.engine._generate_text(prompt, "", max_length=60)
        choice_texts = self._parse_choices(response, genre)[:num_choices]
        
        choices = []
        for i, text in enumerate(choice_texts):
            choices.append({
                'text': text,
                'leads_to': f'{node_id}_{i+1}',
                'type': 'action'
            })
        
        return choices
    
    def _get_path_to_node(self, node_id: str) -> str:
        """Get the story path leading to this node"""
        # Simple implementation: return last 2 nodes
        if node_id == 'start':
            return ""
        
        # Build path by traversing tree
        path_nodes = []
        visited = set()
        
        def find_path(current_id, target_id, path):
            if current_id == target_id:
                return path
            if current_id in visited or current_id not in self.tree['nodes']:
                return None
            
            visited.add(current_id)
            node = self.tree['nodes'][current_id]
            
            for choice in node.get('choices', []):
                result = find_path(choice['leads_to'], target_id, path + [current_id])
                if result:
                    return result
            return None
        
        path = find_path('start', node_id, [])
        
        if not path:
            return self.tree['nodes'].get('start', {}).get('text', '')
        
        # Get last 2 nodes for context
        context_parts = []
        for nid in path[-2:]:
            if nid in self.tree['nodes']:
                context_parts.append(self.tree['nodes'][nid]['text'])
        
        return '\n\n'.join(context_parts)
    
    def _extract_choice_from_id(self, node_id: str) -> str:
        """Extract what choice led to this node"""
        # Parse node_id to find parent choice
        parts = node_id.split('_')
        if len(parts) < 2:
            return "continue"
        
        # Find parent node
        parent_id = '_'.join(parts[:-1])
        if parent_id in self.tree['nodes']:
            parent = self.tree['nodes'][parent_id]
            choice_index = int(parts[-1]) - 1
            if 0 <= choice_index < len(parent.get('choices', [])):
                return parent['choices'][choice_index]['text']
        
        return "continue the investigation"
    
    def _is_natural_ending(self, text: str) -> bool:
        """Check if text represents a natural story ending"""
        ending_phrases = [
            'case closed', 'mystery solved', 'the end', 'finally over',
            'mission complete', 'victory', 'defeated', 'escaped',
            'died', 'killed', 'dead', 'game over', 'lost'
        ]
        text_lower = text.lower()
        return any(phrase in text_lower for phrase in ending_phrases)
    
    def _create_ending_node(self, node_id: str, context: str):
        """Create an ending node"""
        self.tree['nodes'][node_id] = {
            'node_id': node_id,
            'text': f"{context}\n\n**THE END**\n\nThank you for playing!",
            'choices': [],
            'is_ending': True
        }
    
    def _extract_title(self, opening: str) -> str:
        """Extract or generate story title"""
        # Simple title based on genre
        titles = {
            'detective': 'The Thornton Case',
            'war': 'Hold the Line',
            'adventure': 'The Emerald Eye',
            'horror': 'The Abandoned Asylum',
            'thriller': 'The USB Drive'
        }
        return titles.get(self.genre, 'Untitled Story')
    
    def _extract_characters(self, opening: str) -> List[str]:
        """Extract character names from opening"""
        # Simple regex extraction
        import re
        names = re.findall(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', opening)
        return list(set(names))[:5]
    
    def _extract_locations(self, opening: str) -> List[str]:
        """Extract locations from opening"""
        locations = []
        location_keywords = ['room', 'study', 'trench', 'temple', 'asylum', 'street', 'building', 'house']
        for keyword in location_keywords:
            if keyword in opening.lower():
                locations.append(keyword)
        return locations[:3]
    
    def save_tree(self, filename: str):
        """Save story tree to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.tree, f, indent=2)
        print(f"💾 Story tree saved to {filename}")
    
    @staticmethod
    def load_tree(filename: str) -> Dict:
        """Load story tree from JSON file"""
        with open(filename, 'r') as f:
            tree = json.load(f)
        print(f"📂 Story tree loaded from {filename}")
        return tree


if __name__ == "__main__":
    # Test generation
    generator = StoryTreeGenerator()
    tree = generator.generate_story_tree(genre='detective', num_nodes=15, max_depth=4)
    generator.save_tree('detective_story.json')
    
    print("\n📊 Story Tree Stats:")
    print(f"   Nodes: {len(tree['nodes'])}")
    print(f"   Characters: {tree['characters']}")
    print(f"   Title: {tree['title']}")
