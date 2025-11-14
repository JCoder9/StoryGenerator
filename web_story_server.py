"""
Flask Web Server for Adaptive Story Engine
Provides API endpoints for Fallout-style terminal UI
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from adaptive_story_engine import AdaptiveStoryEngine, StoryBeat
import json
import os
from datetime import datetime, timedelta
import re
import threading
import time

app = Flask(__name__)
app.secret_key = 'wasteland_stories_2077'  # Fallout reference
CORS(app)

# Story storage
STORY_DATA_FILE = 'story_sessions.json'
story_engines = {}  # session_id -> engine instance
SESSION_TIMEOUT_HOURS = 2  # Clean up sessions older than 2 hours


def cleanup_old_sessions():
    """Remove story sessions older than SESSION_TIMEOUT_HOURS"""
    cutoff = datetime.now() - timedelta(hours=SESSION_TIMEOUT_HOURS)
    removed = []
    
    for session_id in list(story_engines.keys()):
        try:
            created = datetime.fromisoformat(story_engines[session_id]['created'])
            if created < cutoff:
                del story_engines[session_id]
                removed.append(session_id)
        except (KeyError, ValueError):
            # Invalid session, remove it
            del story_engines[session_id]
            removed.append(session_id)
    
    if removed:
        print(f"🧹 Cleaned up {len(removed)} old session(s)")
    
    return removed


def session_cleanup_worker():
    """Background thread to periodically clean up old sessions"""
    while True:
        time.sleep(3600)  # Run every hour
        cleanup_old_sessions()


# Start cleanup thread
cleanup_thread = threading.Thread(target=session_cleanup_worker, daemon=True)
cleanup_thread.start()


class ChapterManager:
    """Manages story chapters and determines good breaking points"""
    
    @staticmethod
    def should_create_chapter(story_history, user_actions_since_chapter):
        """
        Determine if we should break to a new chapter
        
        Criteria:
        - After major plot points (5+ user actions)
        - At natural scene transitions
        - When story beat changes
        - After significant consequences
        """
        if user_actions_since_chapter < 3:
            return False, None
        
        if user_actions_since_chapter >= 8:
            return True, "After a series of events..."
        
        # Check for scene transition words in recent text
        recent_text = " ".join(story_history[-2:]) if story_history else ""
        transition_markers = [
            "later", "meanwhile", "the next day", "hours passed",
            "after that", "eventually", "finally", "suddenly"
        ]
        
        if any(marker in recent_text.lower() for marker in transition_markers):
            if user_actions_since_chapter >= 5:
                return True, "Time passes..."
        
        return False, None
    
    @staticmethod
    def generate_chapter_title(chapter_num, story_summary):
        """Generate chapter title based on content"""
        titles = [
            f"Chapter {chapter_num}: The Beginning",
            f"Chapter {chapter_num}: Unexpected Turn",
            f"Chapter {chapter_num}: Rising Tension",
            f"Chapter {chapter_num}: The Confrontation",
            f"Chapter {chapter_num}: Consequences",
            f"Chapter {chapter_num}: Resolution"
        ]
        
        # Simple selection based on chapter number
        if chapter_num == 1:
            return "Chapter 1: The Beginning"
        elif chapter_num < 4:
            return f"Chapter {chapter_num}: Developments"
        elif chapter_num < 7:
            return f"Chapter {chapter_num}: Complications"
        else:
            return f"Chapter {chapter_num}: The Conclusion"


class StoryDatabase:
    """Maintains searchable database of story elements"""
    
    def __init__(self):
        self.characters = {}
        self.locations = {}
        self.events = []
        self.items = {}
    
    def add_character(self, name, description, first_appearance):
        """Add or update character"""
        if name not in self.characters:
            self.characters[name] = {
                'name': name,
                'description': description,
                'first_appearance': first_appearance,
                'mentions': 1,
                'history': [description]
            }
        else:
            self.characters[name]['mentions'] += 1
            self.characters[name]['history'].append(description)
    
    def add_location(self, location, description):
        """Add or update location"""
        if location not in self.locations:
            self.locations[location] = {
                'name': location,
                'description': description,
                'visits': 1
            }
        else:
            self.locations[location]['visits'] += 1
    
    def add_event(self, event, chapter):
        """Record major event"""
        self.events.append({
            'description': event,
            'chapter': chapter,
            'timestamp': datetime.now().isoformat()
        })
    
    def search(self, query):
        """Search database for query term"""
        query_lower = query.lower()
        results = {
            'characters': [],
            'locations': [],
            'events': []
        }
        
        # Search characters
        for name, data in self.characters.items():
            if query_lower in name.lower():
                results['characters'].append(data)
        
        # Search locations
        for loc, data in self.locations.items():
            if query_lower in loc.lower():
                results['locations'].append(data)
        
        # Search events
        for event in self.events:
            if query_lower in event['description'].lower():
                results['events'].append(event)
        
        return results
    
    def extract_from_text(self, text, chapter_num):
        """Extract story elements from text"""
        # Extract potential character names (capitalized words)
        potential_names = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', text)
        
        # Common words to exclude
        exclude = {'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'Of', 'And', 
                   'But', 'Or', 'As', 'He', 'She', 'It', 'They', 'This', 'That',
                   'When', 'Where', 'Why', 'How', 'What', 'Which', 'Who'}
        
        for name in potential_names:
            if name not in exclude and len(name) > 2:
                # Get context around name
                name_pos = text.find(name)
                context_start = max(0, name_pos - 50)
                context_end = min(len(text), name_pos + 100)
                context = text[context_start:context_end]
                
                self.add_character(name, context, chapter_num)
        
        # Extract potential locations (after prepositions)
        location_markers = r'(?:in|at|to|from|near)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        locations = re.findall(location_markers, text)
        
        for loc in locations:
            if loc not in exclude:
                self.add_location(loc, f"Location mentioned in chapter {chapter_num}")


def get_or_create_engine(session_id):
    """Get existing engine or create new one"""
    if session_id not in story_engines:
        story_engines[session_id] = {
            'engine': AdaptiveStoryEngine(model_name='distilgpt2'),
            'chapters': [],
            'current_chapter': 1,
            'actions_since_chapter': 0,
            'database': StoryDatabase(),
            'created': datetime.now().isoformat()
        }
    return story_engines[session_id]


def save_story_data():
    """Save story sessions to file"""
    data = {}
    for session_id, session_data in story_engines.items():
        data[session_id] = {
            'chapters': session_data['chapters'],
            'current_chapter': session_data['current_chapter'],
            'database': {
                'characters': session_data['database'].characters,
                'locations': session_data['database'].locations,
                'events': session_data['database'].events
            },
            'created': session_data['created']
        }
    
    with open(STORY_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/')
def index():
    """Serve main terminal interface"""
    return render_template('terminal.html')


@app.route('/api/start', methods=['POST'])
def start_story():
    """Start a new story session"""
    data = request.json
    custom_prompt = data.get('prompt', None)
    
    # Create session ID
    session_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session['story_id'] = session_id
    
    # Create engine
    story_data = get_or_create_engine(session_id)
    engine = story_data['engine']
    
    # Start story
    initial_story = engine.start_story(custom_prompt)
    
    # Create first chapter
    story_data['chapters'].append({
        'number': 1,
        'title': 'Chapter 1: The Beginning',
        'content': [initial_story],
        'started': datetime.now().isoformat()
    })
    
    # Extract story elements
    story_data['database'].extract_from_text(initial_story, 1)
    
    save_story_data()
    
    return jsonify({
        'success': True,
        'session_id': session_id,
        'story': initial_story,
        'chapter': 1,
        'chapter_title': 'Chapter 1: The Beginning',
        'beat': engine.current_beat.value
    })


@app.route('/api/action', methods=['POST'])
def process_action():
    """Process user action"""
    data = request.json
    user_action = data.get('action', '')
    session_id = data.get('session_id') or session.get('story_id')
    
    if not session_id or session_id not in story_engines:
        return jsonify({'success': False, 'error': 'No active story session'})
    
    story_data = get_or_create_engine(session_id)
    engine = story_data['engine']
    
    # Process action
    status, continuation = engine.process_user_action(user_action)
    
    if status == 'rejected':
        return jsonify({
            'success': False,
            'error': continuation
        })
    
    # Add to current chapter
    current_chapter_idx = story_data['current_chapter'] - 1
    story_data['chapters'][current_chapter_idx]['content'].append(f"[USER ACTION: {user_action}]")
    story_data['chapters'][current_chapter_idx]['content'].append(continuation)
    story_data['actions_since_chapter'] += 1
    
    # Extract story elements
    story_data['database'].extract_from_text(continuation, story_data['current_chapter'])
    story_data['database'].add_event(user_action, story_data['current_chapter'])
    
    # Check if should create new chapter
    should_break, transition = ChapterManager.should_create_chapter(
        engine.story_history,
        story_data['actions_since_chapter']
    )
    
    new_chapter = None
    if should_break:
        story_data['current_chapter'] += 1
        story_data['actions_since_chapter'] = 0
        
        chapter_title = ChapterManager.generate_chapter_title(
            story_data['current_chapter'],
            " ".join(engine.story_history[-3:])
        )
        
        story_data['chapters'].append({
            'number': story_data['current_chapter'],
            'title': chapter_title,
            'content': [],
            'started': datetime.now().isoformat()
        })
        
        new_chapter = {
            'number': story_data['current_chapter'],
            'title': chapter_title,
            'transition': transition
        }
    
    save_story_data()
    
    return jsonify({
        'success': True,
        'status': status,
        'story': continuation,
        'chapter': story_data['current_chapter'],
        'beat': engine.current_beat.value,
        'new_chapter': new_chapter
    })


@app.route('/api/chapters', methods=['GET'])
def get_chapters():
    """Get all chapters for current story"""
    session_id = request.args.get('session_id') or session.get('story_id')
    
    if not session_id or session_id not in story_engines:
        return jsonify({'success': False, 'error': 'No active story session'})
    
    story_data = get_or_create_engine(session_id)
    
    return jsonify({
        'success': True,
        'chapters': story_data['chapters'],
        'current_chapter': story_data['current_chapter']
    })


@app.route('/api/search', methods=['POST'])
def search_database():
    """Search story database"""
    data = request.json
    query = data.get('query', '')
    session_id = data.get('session_id') or session.get('story_id')
    
    if not session_id or session_id not in story_engines:
        return jsonify({'success': False, 'error': 'No active story session'})
    
    story_data = get_or_create_engine(session_id)
    results = story_data['database'].search(query)
    
    return jsonify({
        'success': True,
        'query': query,
        'results': results
    })


@app.route('/api/database', methods=['GET'])
def get_full_database():
    """Get complete story database"""
    session_id = request.args.get('session_id') or session.get('story_id')
    
    if not session_id or session_id not in story_engines:
        return jsonify({'success': False, 'error': 'No active story session'})
    
    story_data = get_or_create_engine(session_id)
    db = story_data['database']
    
    return jsonify({
        'success': True,
        'characters': list(db.characters.values()),
        'locations': list(db.locations.values()),
        'events': db.events
    })


@app.route('/api/summary', methods=['GET'])
def get_summary():
    """Get story summary"""
    session_id = request.args.get('session_id') or session.get('story_id')
    
    if not session_id or session_id not in story_engines:
        return jsonify({'success': False, 'error': 'No active story session'})
    
    story_data = get_or_create_engine(session_id)
    engine = story_data['engine']
    
    return jsonify({
        'success': True,
        'summary': engine.get_story_summary(),
        'chapters': len(story_data['chapters']),
        'current_beat': engine.current_beat.value,
        'actions_taken': len(engine.user_actions)
    })


if __name__ == '__main__':
    print("=" * 70)
    print("  WASTELAND STORIES - Terminal Interface Server")
    print("  Fallout-Style Interactive Narrative System")
    print("=" * 70)
    print("\n🚀 Starting server...")
    
    # Get port from environment or use default
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"📡 Access terminal at: http://localhost:{port}")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    print("🎮 Press Ctrl+C to shutdown\n")
    print("=" * 70)
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
