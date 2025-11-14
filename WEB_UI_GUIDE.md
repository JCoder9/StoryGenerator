# Wasteland Stories - Fallout-Style Terminal UI Guide

## Overview

A complete web-based interface for your adaptive story generator with a **Fallout game terminal aesthetic**. Features include:

- ✅ Retro CRT terminal display with scan lines and glow effects
- ✅ Chapter system with AI-determined breaks
- ✅ Story database with character/location/event tracking
- ✅ Search functionality with popup displays
- ✅ Previous chapters sidebar
- ✅ Real-time story progression
- ✅ Fallout-style green monospace terminal

## Quick Start

### 1. Start the Server

```bash
cd /Users/jordanhiggins/Desktop/Story_Generator
/Users/jordanhiggins/Desktop/Story_Generator/bin/python web_story_server.py
```

### 2. Open in Browser

```
http://localhost:5000
```

### 3. Use the Terminal

```
Type: START
(Story begins)

Type: John walks to the door
(AI responds)

Type: DATABASE
(View all story elements)

Type: SEARCH John
(Find details about John)
```

## Features Breakdown

### 🎮 Terminal Interface

**Fallout-Style Elements:**
- CRT screen effects (scan lines, flicker, glow)
- Green monospace font
- Amber highlights for important text
- Terminal boot sequence
- Retro computer aesthetic

**Layout:**
```
┌─────────────────────────────────────────────────────────────┐
│         ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL             │
│     WASTELAND STORIES - INTERACTIVE NARRATIVE SYSTEM        │
├──────────┬─────────────────────────────────────┬────────────┤
│ PREVIOUS │                                     │   STORY    │
│ CHAPTERS │       MAIN STORY AREA               │  DATABASE  │
│          │                                     │            │
│ Chapter 1│   Story text displays here...       │ Characters │
│ Chapter 2│   User actions shown...             │ Locations  │
│ Chapter 3│   AI responses...                   │ Events     │
│          │                                     │            │
│          │                                     │ [SEARCH]   │
├──────────┴─────────────────────────────────────┴────────────┤
│ > [User input here]                                         │
├─────────────────────────────────────────────────────────────┤
│ Status: Ready          Beat: EXPOSITION      Session: ...   │
└─────────────────────────────────────────────────────────────┘
```

### 📖 Chapter System

**Automatic Chapter Breaks:**

The AI automatically creates new chapters when:
- 5+ user actions have occurred
- Natural scene transitions detected ("later", "meanwhile", "the next day")
- Major plot developments happen
- Story beats change

**Chapter Display:**
```
═══════════════════════════════════════════════════════
         CHAPTER 2: UNEXPECTED TURN
                Time passes...
═══════════════════════════════════════════════════════
```

**Chapter Titles:**
- Chapter 1: The Beginning
- Chapter 2-3: Developments
- Chapter 4-6: Complications
- Chapter 7+: The Conclusion

### 🗂️ Story Database

**Tracks Automatically:**

1. **Characters**
   - Name
   - First appearance (chapter)
   - Number of mentions
   - Context/description
   - History through story

2. **Locations**
   - Name
   - Description
   - Number of visits

3. **Events**
   - Major user actions
   - Chapter where occurred
   - Timestamp

**Example Database Entry:**
```
CHARACTERS
───────────────────────────────────
Name: John
First appearance: Chapter 1
Mentions: 15
Description: "John stood near the door, considering his options..."
```

### 🔍 Search Functionality

**How to Search:**

1. **Quick Search (Sidebar)**
   - Type name/term in search box
   - Click "QUERY" button
   - Results popup appears

2. **Command Line Search**
   ```
   > SEARCH John
   > SEARCH mansion
   > SEARCH evidence
   ```

**Search Results Popup:**
```
╔═══════════════════════════════════════════════════╗
║  STORY DATABASE - QUERY RESULTS                   ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  Query: John                                      ║
║                                                   ║
║  ═══ CHARACTERS ═══                               ║
║  ┌───────────────────────────────────────┐        ║
║  │ Name: John                            │        ║
║  │ First appearance: Chapter 1           │        ║
║  │ Mentions: 15                          │        ║
║  │ "John's friend Michael came to..."    │        ║
║  └───────────────────────────────────────┘        ║
║                                                   ║
║  ═══ EVENTS ═══                                   ║
║  - John pushes Michael (Chapter 1)                ║
║  - John tries to escape (Chapter 2)               ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

## Commands Reference

### Story Commands

| Command | Description | Example |
|---------|-------------|---------|
| `START` | Begin new story | `START` |
| `(any text)` | Character action | `John walks away` |
| `DATABASE` | View all story data | `DATABASE` |
| `SEARCH [term]` | Search for element | `SEARCH Michael` |
| `CHAPTERS` | List all chapters | `CHAPTERS` |
| `SUMMARY` | Story summary | `SUMMARY` |
| `CLEAR` | Clear screen | `CLEAR` |
| `HELP` | Show commands | `HELP` |

### Usage Examples

```
# Start a story
> START

# Make decisions
> John investigates the noise
> John finds a hidden door
> John enters the passage

# Query story elements
> DATABASE
  (Shows all characters, locations, events)

> SEARCH door
  (Shows all mentions of "door")

> SEARCH John
  (Shows John's complete history)

# View progress
> CHAPTERS
  (Lists all chapters with timestamps)

> SUMMARY
  (Current story state and beat)
```

## How Chapter Breaks Work

### Example Flow:

```
User: John meets Michael at the park
AI: Michael looked nervous. He pulled out a letter...

User: John asks what's wrong
AI: Michael explained the mysterious threat...

User: John offers to help
AI: They decided to investigate together...

User: John drives to the old mansion
AI: The mansion loomed on the hill...

User: John enters the front door
AI: Inside was dark and dusty...

[5 actions completed, scene transition detected]

═══════════════════════════════════════════════
           CHAPTER 2: DEVELOPMENTS
              Later that evening...
═══════════════════════════════════════════════

AI continues: The investigation took a dark turn...
```

### Breaking Points Criteria:

1. **Minimum Actions:** At least 3 user actions
2. **Scene Transition Words:** 
   - "later", "meanwhile", "the next day"
   - "hours passed", "eventually", "finally"
   - "suddenly", "after that"
3. **Action Count:** Automatically at 8+ actions
4. **Natural Breaks:** Major plot developments

## Example User Session

```
═══════════════════════════════════════════════════════════════
  ROBCO INDUSTRIES (TM) TERMLINK PROTOCOL
  WASTELAND STORIES - INTERACTIVE NARRATIVE SYSTEM v2.1.7
═══════════════════════════════════════════════════════════════

SYSTEM INITIALIZING...
LOADING NARRATIVE ENGINE...
CHECKING QUANTUM STATE DRIVES...
WASTELAND STORIES v2.1.7 READY

Welcome to WASTELAND STORIES
An adaptive narrative experience

Type 'START' to begin your story...
Type 'DATABASE' to view story elements...
Type 'HELP' for commands...

> START

[BOOT SEQUENCE HIDES, STORY BEGINS]

═══════════════════════════════════════════════════════════════
CHAPTER 1: THE BEGINNING
═══════════════════════════════════════════════════════════════

It was a pleasant afternoon when John decided to take a walk 
through the park. The sun filtered through the trees, and birds 
sang in the branches. As he rounded the corner, he saw his old 
friend Michael sitting on a bench, looking troubled.

> John approaches Michael

[USER ACTION: John approaches Michael]

Michael looked up with a start. "John," he said quietly, "I was 
hoping I'd run into you. I need your help with something... 
something dangerous." He glanced around nervously before pulling 
a crumpled envelope from his jacket.

> John asks what's in the envelope

[USER ACTION: John asks what's in the envelope]

Michael hesitated, then handed over the envelope. Inside was a 
photograph of an abandoned warehouse and a cryptic note: "They 
know what you did. Midnight. Come alone." Michael's hands were 
shaking. "I don't know who sent this, but I can't go alone."

> SEARCH Michael

[DATABASE POPUP OPENS]

╔═══════════════════════════════════════════════════════════╗
║  STORY DATABASE - QUERY RESULTS                           ║
╠═══════════════════════════════════════════════════════════╣
║  Query: Michael                                           ║
║                                                           ║
║  ═══ CHARACTERS ═══                                       ║
║  ┌─────────────────────────────────────────────┐          ║
║  │ Name: Michael                               │          ║
║  │ First appearance: Chapter 1                 │          ║
║  │ Mentions: 3                                 │          ║
║  │ "Michael looked troubled... nervously       │          ║
║  │  pulling envelope from jacket"              │          ║
║  └─────────────────────────────────────────────┘          ║
║                                                           ║
║  ═══ EVENTS ═══                                           ║
║  - John approaches Michael (Chapter 1)                    ║
║  - John asks what's in the envelope (Chapter 1)           ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

[CLOSE POPUP]

> John agrees to go with Michael to the warehouse

[USER ACTION: John agrees to go with Michael to the warehouse]

Michael's relief was visible. "Thank you," he said. "We should 
go tonight, before midnight. I have a bad feeling about this, 
but I can't ignore it." As they made plans, John couldn't shake 
the feeling they were being watched...

[MORE ACTIONS CONTINUE...]

═══════════════════════════════════════════════════════════════
           CHAPTER 2: RISING TENSION
              Hours later...
═══════════════════════════════════════════════════════════════

The warehouse loomed before them in the darkness...

```

## Technical Details

### File Structure

```
Story_Generator/
├── web_story_server.py          # Flask backend
├── adaptive_story_engine.py     # Story AI engine
├── templates/
│   └── terminal.html            # Terminal interface
├── static/
│   ├── terminal.css            # Fallout styling
│   └── terminal.js             # Frontend logic
└── story_sessions.json         # Saved stories
```

### API Endpoints

```python
POST /api/start          # Start new story
POST /api/action         # Process user action
GET  /api/chapters       # Get all chapters
POST /api/search         # Search database
GET  /api/database       # Get full database
GET  /api/summary        # Get story summary
```

### Data Persistence

Stories are automatically saved to `story_sessions.json`:

```json
{
  "story_20231113_140532": {
    "chapters": [...],
    "current_chapter": 2,
    "database": {
      "characters": {...},
      "locations": {...},
      "events": [...]
    },
    "created": "2023-11-13T14:05:32"
  }
}
```

## Customization

### Change Terminal Colors

Edit `static/terminal.css`:

```css
:root {
    --terminal-green: #40ff40;     /* Main text */
    --terminal-amber: #ffb000;      /* Highlights */
    --terminal-dark: #001a00;       /* Background */
}
```

### Adjust Chapter Break Sensitivity

Edit `web_story_server.py`:

```python
# In ChapterManager.should_create_chapter()

if user_actions_since_chapter < 3:  # Minimum actions
    return False, None

if user_actions_since_chapter >= 8:  # Auto-break threshold
    return True, "After a series of events..."
```

### Modify Database Extraction

Edit character/location detection in `web_story_server.py`:

```python
# StoryDatabase.extract_from_text()
potential_names = re.findall(r'\b([A-Z][a-z]+)\b', text)
```

## Troubleshooting

### Server won't start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill existing process if needed
kill -9 [PID]

# Or use different port
# Edit web_story_server.py, change:
app.run(debug=True, host='0.0.0.0', port=5001)
```

### Database not updating
- Check browser console for errors
- Verify session_id is set
- Restart server to reload code

### Chapters not breaking
- Increase actions (try 8+)
- Use transition words in story
- Check console for chapter detection logs

### Search not working
- Ensure story has been started
- Check spelling of search terms
- Database extracts capitalized names

## Performance Notes

- **First story generation:** 3-5 seconds (model loading)
- **Subsequent responses:** 2-4 seconds
- **Database queries:** <1 second
- **Chapter breaks:** Instant
- **Search:** <1 second

## Browser Compatibility

✅ **Recommended:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

⚠️ **CRT effects** work best on modern browsers
❌ **IE11** not supported

## Advanced Features

### Custom Story Prompts

The START command accepts custom prompts:

```javascript
// In terminal.js, modify startNewStory():
fetch('/api/start', {
    method: 'POST',
    body: JSON.stringify({
        prompt: "Your custom opening here..."
    })
})
```

### Export Story

Add export button to save complete story:

```javascript
function exportStory() {
    fetch(`/api/chapters?session_id=${sessionId}`)
    .then(response => response.json())
    .then(data => {
        const text = JSON.stringify(data.chapters, null, 2);
        downloadFile('story.json', text);
    });
}
```

## Tips for Best Experience

1. **Full screen browser** - Use F11 for immersive terminal
2. **Dark room** - CRT effects look best in darkness
3. **Speakers on** - Add sound effects for typing (optional)
4. **Save regularly** - Stories auto-save but backup `story_sessions.json`
5. **Descriptive actions** - More detail = better AI responses
6. **Use DATABASE** - Check what AI has tracked
7. **Name things** - Capitalized names are auto-detected

## Next Steps

1. **Start the server:**
   ```bash
   /Users/jordanhiggins/Desktop/Story_Generator/bin/python web_story_server.py
   ```

2. **Open browser:**
   ```
   http://localhost:5000
   ```

3. **Start story:**
   ```
   > START
   ```

4. **Have fun!** Your choices shape the narrative.

---

**Enjoy your Fallout-style story terminal!** 🎮📖✨
