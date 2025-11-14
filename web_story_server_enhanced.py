"""
ENHANCED Flask Web Server for Adaptive Story Engine
Now with improved story quality through advanced prompt engineering and better models
"""

# Prevent TensorFlow import issues and speed up transformers loading
import os
os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['USE_TF'] = 'NO'  # Don't load TensorFlow
os.environ['USE_TORCH'] = 'YES'  # Only use PyTorch
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'  # Fix OpenMP conflict

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS

# Import ENHANCED story engine
from adaptive_story_engine_enhanced import AdaptiveStoryEngine, StoryBeat

# Import intelligent model selector
from model_selector import ModelSelector

# Import simple story generator (fast, on-demand generation)
from simple_story_generator import SimpleStoryGenerator

import json
import os
from datetime import datetime, timedelta
import re
import threading
import time

app = Flask(__name__)
app.secret_key = 'ai_story_generator_2077_enhanced'
CORS(app)

# Story storage
STORY_DATA_FILE = 'story_sessions.json'
story_engines = {}
story_generators = {}  # Simple story generators
SESSION_TIMEOUT_HOURS = 2

# INTELLIGENT MODEL SELECTION
# Automatically detects your hardware and selects the best model that will work
print("\n" + "="*70)
print("🤖 INTELLIGENT MODEL SELECTION")
print("="*70)

# BEST MODEL SELECTION - TinyLlama 1.1B Chat
# Best ungated model: No authentication needed, LLaMA-based, excellent storytelling
print("\n" + "="*70)
print("🤖 MODEL SELECTION")
print("="*70)

# Use best ungated storytelling model: TinyLlama 1.1B Chat
DEFAULT_MODEL = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
print(f"\n✅ USING: TinyLlama 1.1B Chat")
print(f"   📚 LLaMA-based architecture, excellent storytelling")
print(f"   🔓 No authentication required - works for all users")
print(f"   💾 Memory: ~2.2GB download, ~2GB RAM usage")
print(f"   ⚡ Fast generation, optimized for chat/narrative")

# Disable auto-fallback - stick with chosen model
ENABLE_AUTO_FALLBACK = False
FALLBACK_MODELS = []

print(f"\n📌 Model: {DEFAULT_MODEL}")
print(f"🔄 Fallback: DISABLED")

print("="*70 + "\n")

USE_ENHANCED_PROMPTS = True   # True = better quality, False = faster
DEFAULT_GENRE = 'mystery'      # Options: mystery, horror, adventure, thriller, drama


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
            del story_engines[session_id]
            removed.append(session_id)
    
    if removed:
        print(f"🧹 Cleaned up {len(removed)} old session(s)")
    
    return removed


def session_cleanup_worker():
    """Background thread to periodically clean up old sessions"""
    while True:
        time.sleep(3600)
        cleanup_old_sessions()


# Start cleanup thread
cleanup_thread = threading.Thread(target=session_cleanup_worker, daemon=True)
cleanup_thread.start()


class ChapterManager:
    """Manages story chapters and determines good breaking points"""
    
    @staticmethod
    def should_create_chapter(story_history, user_actions_since_chapter):
        """Determine if we should break to a new chapter"""
        if user_actions_since_chapter < 3:
            return False, None
        
        if user_actions_since_chapter >= 8:
            return True, "After a series of events..."
        
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
        
        for name, data in self.characters.items():
            if query_lower in name.lower():
                results['characters'].append(data)
        
        for loc, data in self.locations.items():
            if query_lower in loc.lower():
                results['locations'].append(data)
        
        for event in self.events:
            if query_lower in event['description'].lower():
                results['events'].append(event)
        
        return results
    
    def extract_from_text(self, text, chapter_num):
        """Extract story elements from text"""
        potential_names = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', text)
        
        exclude = {'The', 'A', 'An', 'In', 'On', 'At', 'To', 'For', 'Of', 'And', 
                   'But', 'Or', 'As', 'He', 'She', 'It', 'They', 'This', 'That',
                   'When', 'Where', 'Why', 'How', 'What', 'Which', 'Who'}
        
        for name in potential_names:
            if name not in exclude and len(name) > 2:
                name_pos = text.find(name)
                context_start = max(0, name_pos - 50)
                context_end = min(len(text), name_pos + 100)
                context = text[context_start:context_end]
                
                self.add_character(name, context, chapter_num)
        
        location_markers = r'(?:in|at|to|from|near)\s+(?:the\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)'
        locations = re.findall(location_markers, text)
        
        for loc in locations:
            if loc not in exclude:
                self.add_location(loc, f"Location mentioned in chapter {chapter_num}")


def get_or_create_engine(session_id, model_name=None, genre=None):
    """Get existing engine or create new one - QWEN ONLY (no auto-fallback)"""
    if session_id not in story_engines:
        # Use custom model if specified, otherwise use default
        model = model_name or DEFAULT_MODEL
        story_genre = genre or DEFAULT_GENRE
        
        print(f"\n🔄 Loading story engine: {model}")
        print("   ⏳ First run will download model (~3GB)")
        print("   ⏳ This may take 2-5 minutes depending on your connection")
        print("   💡 Subsequent loads will be instant\n")
        
        engine = None
        
        # Try primary model (Qwen) with better error handling
        try:
            print(f"📥 Attempting to load {model}...")
            engine = AdaptiveStoryEngine(
                model_name=model,
                use_enhanced_prompts=USE_ENHANCED_PROMPTS
            )
            print(f"✅ Successfully loaded: {model}\n")
                
        except Exception as e:
            error_msg = str(e)
            print(f"\n❌ FAILED to load {model}")
            print(f"   Error: {error_msg}\n")
            
            # Only fallback if explicitly enabled
            if ENABLE_AUTO_FALLBACK and FALLBACK_MODELS:
                print(f"🔄 Trying fallback models: {FALLBACK_MODELS}")
                
                for fallback_model in FALLBACK_MODELS:
                    try:
                        print(f"\n📥 Attempting fallback: {fallback_model}...")
                        engine = AdaptiveStoryEngine(
                            model_name=fallback_model,
                            use_enhanced_prompts=USE_ENHANCED_PROMPTS
                        )
                        print(f"✅ Successfully loaded fallback: {fallback_model}\n")
                        model = fallback_model  # Update model name
                        break
                    except Exception as fallback_error:
                        print(f"❌ Fallback {fallback_model} also failed: {str(fallback_error)[:100]}")
                        continue
            else:
                # No fallback - raise the error
                print(f"\n💡 TIP: If download failed, check your internet connection")
                print(f"💡 TIP: To enable GPT-2 fallback, set ENABLE_AUTO_FALLBACK = True")
                raise RuntimeError(f"Failed to load {model}. No fallback enabled.") from e
        
        if engine is None:
            raise RuntimeError("All models failed to load!")
        
        story_engines[session_id] = {
            'engine': engine,
            'chapters': [],
            'current_chapter': 1,
            'actions_since_chapter': 0,
            'database': StoryDatabase(),
            'created': datetime.now().isoformat(),
            'model': model,  # Actual model being used
            'genre': story_genre,
            'fallback_used': False,  # Fallback disabled
            'original_model': None
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
            'created': session_data['created'],
            'model': session_data.get('model', DEFAULT_MODEL),
            'genre': session_data.get('genre', DEFAULT_GENRE)
        }
    
    with open(STORY_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/')
def index():
    """Serve main terminal interface"""
    return render_template('terminal.html')


@app.route('/api/start', methods=['POST'])
def start_story():
    """Start a new story session with enhanced quality"""
    data = request.json
    custom_prompt = data.get('prompt', None)
    model_name = data.get('model', DEFAULT_MODEL)
    genre = data.get('genre', DEFAULT_GENRE)
    
    session_id = f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    session['story_id'] = session_id
    
    # Create engine with specified model and genre (with automatic fallback)
    story_data = get_or_create_engine(session_id, model_name=model_name, genre=genre)
    engine = story_data['engine']
    
    # Start story with genre-specific opening
    if custom_prompt:
        initial_story = engine.start_story(initial_prompt=custom_prompt, genre=genre)
    else:
        initial_story = engine.start_story(genre=genre)
    
    # Create first chapter
    story_data['chapters'].append({
        'number': 1,
        'title': 'Chapter 1: The Beginning',
        'content': [initial_story],
        'started': datetime.now().isoformat()
    })
    
    story_data['database'].extract_from_text(initial_story, 1)
    
    save_story_data()
    
    # Prepare response with fallback notification if applicable
    response = {
        'success': True,
        'session_id': session_id,
        'story': initial_story,
        'chapter': 1,
        'chapter_title': 'Chapter 1: The Beginning',
        'beat': engine.current_beat.value,
        'model': story_data['model'],  # Actual model loaded (may be fallback)
        'genre': genre
    }
    
    # Add fallback warning if smaller model was used
    if story_data.get('fallback_used', False):
        response['fallback_warning'] = {
            'occurred': True,
            'requested_model': story_data.get('original_model'),
            'actual_model': story_data['model'],
            'message': f"⚠️ RAM CONSTRAINT DETECTED\n\nYour system couldn't load '{story_data.get('original_model')}' due to insufficient memory.\n\nUsing fallback model '{story_data['model']}' instead.\n\n⚡ Story quality may be reduced, but the adventure continues!"
        }
    
    return jsonify(response)


@app.route('/api/action', methods=['POST'])
def process_action():
    """Process user action with enhanced narrative quality"""
    data = request.json
    user_action = data.get('action', '')
    session_id = data.get('session_id') or session.get('story_id')
    
    if not session_id or session_id not in story_engines:
        return jsonify({'success': False, 'error': 'No active story session'})
    
    story_data = get_or_create_engine(session_id)
    engine = story_data['engine']
    
    # Check if user wants to continue the story narration
    if user_action.lower().strip() == 'continue':
        # Generate more story continuation with enhanced context
        context = engine._build_context_with_story_elements(recent_action="", max_history=2)
        current_beat = engine.genre_config["beats"][engine.genre_beat_index] if engine.genre_config else "story_development"
        player_guidance = engine.player_profile.get_narrative_guidance()
        
        system_instruction = engine._build_continuation_instruction("normal", player_guidance, current_beat)
        
        # Generate next segment with story element awareness
        continuation = engine._generate_until_user_choice(
            context,
            system_instruction=system_instruction,
            current_beat=current_beat,
            recent_action=""
        )
        
        # Add to current chapter
        current_chapter_idx = story_data['current_chapter'] - 1
        story_data['chapters'][current_chapter_idx]['content'].append(continuation)
        
        # Extract story elements from new content
        story_data['database'].extract_from_text(continuation, story_data['current_chapter'])
        engine._extract_story_elements(continuation)
        engine._extract_genre_elements(continuation)
        
        return jsonify({
            'success': True,
            'continuation': continuation,
            'database': story_data['database'].get_all()
        })
    
    # Process action with enhanced engine
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


@app.route('/api/profile', methods=['GET'])
def get_player_profile():
    """Get player personality profile"""
    session_id = request.args.get('session_id') or session.get('story_id')
    
    if not session_id or session_id not in story_engines:
        return jsonify({'success': False, 'error': 'No active story session'})
    
    story_data = get_or_create_engine(session_id)
    engine = story_data['engine']
    profile = engine.get_player_profile()
    
    return jsonify({
        'success': True,
        'profile': profile
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
        'actions_taken': len(engine.user_actions),
        'model': story_data.get('model', DEFAULT_MODEL),
        'genre': story_data.get('genre', DEFAULT_GENRE)
    })


# ============================================================================
# SIMPLE STORY ENDPOINTS - Fast on-demand story generation
# ============================================================================

@app.route('/api/start-simple-story', methods=['POST'])
def start_simple_story():
    """Start a new story with instant opening scene"""
    data = request.get_json()
    genre = data.get('genre', 'adventure').lower()
    
    # Generate session ID
    session_id = f'story_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    session['story_id'] = session_id
    
    # Validate genre
    valid_genres = ['detective', 'war', 'horror', 'adventure', 'scifi']
    if genre not in valid_genres:
        return jsonify({
            'success': False,
            'error': f'Invalid genre. Choose from: {", ".join(valid_genres)}'
        })
    
    try:
        # Create story generator
        print(f"\n📖 Starting {genre} story for session: {session_id}")
        generator = SimpleStoryGenerator(model_name=DEFAULT_MODEL)
        story_generators[session_id] = {
            'generator': generator,
            'created': datetime.now().isoformat(),
            'genre': genre,
            'context': ''
        }
        
        # Get opening scene (instant - no AI generation needed)
        opening = generator.start_story(genre)
        
        # Store opening text as context
        story_generators[session_id]['context'] = opening['text']
        
        print(f"✅ Story started successfully!")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'node': opening
        })
        
    except Exception as e:
        print(f"\n❌ Story start failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


@app.route('/api/continue-story', methods=['POST'])
def continue_story():
    """Continue story based on user's choice"""
    data = request.get_json()
    session_id = data.get('session_id') or session.get('story_id')
    choice = data.get('choice', '').strip()
    
    if not session_id or session_id not in story_generators:
        return jsonify({
            'success': False,
            'error': 'No active story session. Start a new story first.'
        })
    
    if not choice:
        return jsonify({
            'success': False,
            'error': 'No choice provided'
        })
    
    session_data = story_generators[session_id]
    generator = session_data['generator']
    context = session_data['context']
    
    try:
        print(f"\n🎬 Continuing story with choice: {choice}")
        
        # Generate next segment (takes ~10-15 seconds)
        next_segment = generator.continue_story(choice, context)
        
        # Update context
        new_context = context + "\n\n" + choice + "\n\n" + next_segment['text']
        story_generators[session_id]['context'] = new_context
        
        print(f"✅ Story segment generated!")
        
        return jsonify({
            'success': True,
            'node': next_segment,
            'is_ending': next_segment.get('is_ending', False)
        })
        
    except Exception as e:
        print(f"\n❌ Story continuation failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        })


if __name__ == '__main__':
    print("=" * 70)
    print("  AI STORY GENERATOR - Enhanced Edition with Story Trees")
    print("  Hybrid Pre-Generated + Dynamic AI Storytelling")
    print("=" * 70)
    print(f"\n📚 Story Quality: {'ENHANCED' if USE_ENHANCED_PROMPTS else 'STANDARD'}")
    print(f"🤖 Default Model: {DEFAULT_MODEL}")
    print(f"🎭 Default Genre: {DEFAULT_GENRE}")
    print(f"\n🌳 Story Tree System:")
    print(f"   ⚡ Instant responses from pre-generated trees")
    print(f"   🎨 AI fallback for creative user inputs")
    print(f"   💾 Save/Load story trees for reuse")
    print("\n🚀 Starting server...")
    
    # Get port from environment or use default
    import os
    port = int(os.environ.get('PORT', 5000))
    
    # DISABLE debug mode to prevent crashes
    debug_mode = False
    
    print(f"📡 Access terminal at: http://localhost:{port}")
    print(f"🔧 Debug mode: {'ON' if debug_mode else 'OFF'}")
    print("🎮 Press Ctrl+C to shutdown\n")
    print("💡 TIP: Use /api/generate-tree to create branching stories")
    print("   Endpoints: /api/generate-tree, /api/load-tree, /api/play-node")
    print("=" * 70)
    
    # Start Flask server (debug=False prevents auto-reload crashes)
    app.run(host='0.0.0.0', port=port, debug=debug_mode, use_reloader=False)
