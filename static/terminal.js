// Wasteland Stories - Terminal JavaScript
// Handles all user interactions and API communications

let sessionId = null;
let currentChapter = 1;
let isProcessing = false;
let lowPowerMode = false;
let loadingOverlay = null;
let storyTreeMode = false;  // New: Track if using story tree
let currentNode = null;      // New: Current tree node

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    const input = document.getElementById('userInput');
    input.addEventListener('keypress', handleInput);
    
    // Create loading overlay element
    createLoadingOverlay();
    
    // Load low power mode preference
    const savedLowPower = localStorage.getItem('lowPowerMode');
    if (savedLowPower === 'true') {
        enableLowPowerMode();
    }
    
    // Simulate boot sequence
    setTimeout(() => {
        // No need to focus input - using genre buttons now
    }, 1000);
    
    // Allow Enter key on quick search
    document.getElementById('quickSearch').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') quickSearch();
    });
});

// NEW: Genre selection
function selectGenre(genre) {
    if (isProcessing) return;
    
    // Hide genre selection
    document.getElementById('genreSelection').style.display = 'none';
    
    // Show loading message
    const bootSeq = document.getElementById('bootSequence');
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'tree-loading';
    loadingDiv.innerHTML = `
        <div>Starting ${genre.toUpperCase()} story...</div>
        <div style="margin-top: 20px; color: var(--terminal-green);">
            Loading opening scene...
        </div>
    `;
    bootSeq.appendChild(loadingDiv);
    
    storyTreeMode = true;
    isProcessing = true;
    updateStatus('Starting story...');
    
    // Start story (instant - uses predefined opening)
    startSimpleStory(genre);
}

// NEW: Start simple story
function startSimpleStory(genre) {
    fetch('/api/start-simple-story', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ genre: genre })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            sessionId = data.session_id;
            
            // Hide boot sequence, show story
            document.getElementById('bootSequence').style.display = 'none';
            document.getElementById('storyContent').style.display = 'block';
            
            // Show choice buttons area instead of text input
            document.getElementById('textInputArea').style.display = 'none';
            document.getElementById('choiceButtonsArea').style.display = 'block';
            
            // Display opening scene
            displayStoryNode(data.node);
            
            updateStatus('Story ready!');
            updateSessionDisplay(sessionId);
            
            isProcessing = false;
        } else {
            displayError(data.error || 'Failed to start story');
            isProcessing = false;
        }
    })
    .catch(error => {
        displayError('Connection error: ' + error);
        isProcessing = false;
    });
}

// NEW: Display story node
function displayStoryNode(node) {
    currentNode = node;
    
    // Display story text
    const storyContent = document.getElementById('storyContent');
    const div = document.createElement('div');
    div.className = 'story-text';
    div.textContent = node.text;
    storyContent.appendChild(div);
    
    // Check if ending
    if (node.is_ending) {
        const endingDiv = document.createElement('div');
        endingDiv.className = 'story-text';
        endingDiv.style.color = 'var(--terminal-amber)';
        endingDiv.style.textAlign = 'center';
        endingDiv.style.marginTop = '20px';
        endingDiv.textContent = '═══ THE END ═══';
        storyContent.appendChild(endingDiv);
        
        // Show restart button
        displayChoiceButtons([{text: '🔄 Start New Story', action: 'restart'}]);
    } else {
        // Display choices as buttons
        displayChoiceButtons(node.choices);
    }
    
    // Scroll to bottom
    storyContent.scrollTop = storyContent.scrollHeight;
}

// NEW: Display choice buttons
function displayChoiceButtons(choices) {
    const buttonsContainer = document.getElementById('choiceButtons');
    buttonsContainer.innerHTML = '';
    
    choices.forEach((choice, index) => {
        const btn = document.createElement('button');
        btn.className = 'choice-btn';
        btn.textContent = choice.text;
        btn.onclick = () => handleChoice(choice, index);
        buttonsContainer.appendChild(btn);
    });
}

// NEW: Handle choice selection
function handleChoice(choice, index) {
    if (isProcessing) return;
    
    // Special handling for restart
    if (choice.action === 'restart') {
        location.reload();
        return;
    }
    
    isProcessing = true;
    updateStatus('Generating next scene...');
    
    // Disable all buttons
    const buttons = document.querySelectorAll('.choice-btn');
    buttons.forEach((btn, i) => {
        btn.disabled = true;
        if (i === index) btn.classList.add('selected');
    });
    
    // Display user's choice
    const storyContent = document.getElementById('storyContent');
    const choiceDiv = document.createElement('div');
    choiceDiv.className = 'story-text';
    choiceDiv.style.color = 'var(--terminal-amber)';
    choiceDiv.textContent = `\n> You chose: ${choice.text}\n`;
    storyContent.appendChild(choiceDiv);
    
    // Show loading indicator
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'story-text';
    loadingDiv.style.color = 'var(--terminal-green)';
    loadingDiv.textContent = '⏳ Generating story continuation...';
    loadingDiv.id = 'loadingIndicator';
    storyContent.appendChild(loadingDiv);
    storyContent.scrollTop = storyContent.scrollHeight;
    
    // Fetch next scene (takes ~10-15 seconds for AI generation)
    fetch('/api/continue-story', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            session_id: sessionId,
            choice: choice.text
        })
    })
    .then(response => response.json())
    .then(data => {
        // Remove loading indicator
        const loading = document.getElementById('loadingIndicator');
        if (loading) loading.remove();
        
        if (data.success) {
            displayStoryNode(data.node);
            updateStatus('Ready');
        } else {
            displayError(data.error || 'Failed to load next scene');
        }
        isProcessing = false;
    })
    .catch(error => {
        // Remove loading indicator
        const loading = document.getElementById('loadingIndicator');
        if (loading) loading.remove();
        
        displayError('Connection error: ' + error);
        isProcessing = false;
    });
}

function focusInput() {
    document.getElementById('userInput').focus();
}

function handleInput(event) {
    if (event.key === 'Enter') {
        const input = document.getElementById('userInput');
        const userText = input.value.trim();
        input.value = '';
        
        if (!userText) return;
        
        processCommand(userText);
    }
}

function processCommand(text) {
    const command = text.toUpperCase();
    
    // Handle commands
    if (command === 'START') {
        startNewStory();
    } else if (command === 'HELP') {
        showHelp();
    } else if (command === 'DATABASE') {
        showDatabase();
    } else if (command.startsWith('SEARCH ')) {
        const query = text.substring(7);
        searchDatabase(query);
    } else if (command === 'CHAPTERS') {
        listChapters();
    } else if (command === 'SUMMARY') {
        showSummary();
    } else if (command === 'CLEAR') {
        clearScreen();
    } else {
        // Treat as story action
        if (!sessionId) {
            displayError('No active story. Type START to begin.');
            return;
        }
        processStoryAction(text);
    }
}

function startNewStory() {
    if (isProcessing) return;
    isProcessing = true;
    
    showLoading();
    updateStatus('Initializing narrative engine...');
    
    // Hide boot sequence, show story
    document.getElementById('bootSequence').style.display = 'none';
    document.getElementById('storyContent').style.display = 'block';
    document.getElementById('chapterIndicator').style.display = 'block';
    
    fetch('/api/start', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            sessionId = data.session_id;
            currentChapter = data.chapter;
            
            // Check for model fallback warning
            if (data.fallback_warning && data.fallback_warning.occurred) {
                displayFallbackWarning(data.fallback_warning);
            }
            
            displayStoryText(data.story, false);
            updateChapterIndicator(data.chapter_title);
            updateStatus('Story initialized - awaiting input');
            updateBeatIndicator(data.beat);
            updateSessionDisplay(sessionId);
            
            // Add first chapter to sidebar
            addChapterToSidebar(data.chapter, data.chapter_title);
            
            // Update database
            updateDatabaseCounts();
        } else {
            displayError(data.error || 'Failed to start story');
        }
        hideLoading();
        isProcessing = false;
    })
    .catch(error => {
        displayError('Connection error: ' + error);
        hideLoading();
        isProcessing = false;
    });
}

function processStoryAction(action) {
    if (isProcessing) return;
    isProcessing = true;
    
    showLoading();
    updateStatus('Processing action...');
    
    // Display user action
    displayUserAction(action);
    
    fetch('/api/action', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            action: action,
            session_id: sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Display story continuation
            displayStoryText(data.story, true);
            updateStatus('Ready for next action');
            updateBeatIndicator(data.beat);
            
            // Check for new chapter
            if (data.new_chapter) {
                displayChapterBreak(data.new_chapter);
                addChapterToSidebar(data.new_chapter.number, data.new_chapter.title);
                updateChapterIndicator(data.new_chapter.title);
                currentChapter = data.new_chapter.number;
            }
            
            // Update database
            updateDatabaseCounts();
        } else {
            displayError(data.error || 'Action rejected');
        }
        isProcessing = false;
        focusInput();
    })
    .catch(error => {
        displayError('Connection error: ' + error);
        isProcessing = false;
    });
}

function displayStoryText(text, animate = true) {
    const storyContent = document.getElementById('storyContent');
    const div = document.createElement('div');
    div.className = 'story-text';
    
    // Check if typing animation should be used
    const shouldAnimate = animate && (window.typingAnimationEnabled !== false) && !lowPowerMode;
    
    if (shouldAnimate) {
        // Typewriter effect
        div.textContent = '';
        storyContent.appendChild(div);
        typeWriter(div, text, 0);
    } else {
        div.textContent = text;
        storyContent.appendChild(div);
    }
    
    // Scroll to bottom
    storyContent.scrollTop = storyContent.scrollHeight;
}

function typeWriter(element, text, index) {
    // Skip animation in low power mode
    if (lowPowerMode || window.typingAnimationEnabled === false) {
        element.textContent = text;
        return;
    }
    
    if (index < text.length) {
        element.textContent += text.charAt(index);
        setTimeout(() => typeWriter(element, text, index + 1), 10);
    }
}

function displayUserAction(action) {
    const storyContent = document.getElementById('storyContent');
    const div = document.createElement('div');
    div.className = 'user-action';
    div.textContent = '> ' + action;
    storyContent.appendChild(div);
    storyContent.scrollTop = storyContent.scrollHeight;
}

function displayChapterBreak(chapterData) {
    const storyContent = document.getElementById('storyContent');
    const div = document.createElement('div');
    div.className = 'chapter-break';
    div.innerHTML = `
        <div class="chapter-break-title">${chapterData.title}</div>
        <div class="chapter-break-subtitle">${chapterData.transition || 'The story continues...'}</div>
    `;
    storyContent.appendChild(div);
    storyContent.scrollTop = storyContent.scrollHeight;
}

function displayError(message) {
    const storyContent = document.getElementById('storyContent');
    const div = document.createElement('div');
    div.className = 'error-message';
    div.textContent = '⚠ ERROR: ' + message;
    storyContent.appendChild(div);
    storyContent.scrollTop = storyContent.scrollHeight;
    updateStatus('Error occurred');
}

function displayFallbackWarning(warningData) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease-in;
    `;
    
    // Create warning box
    const warningBox = document.createElement('div');
    warningBox.style.cssText = `
        background: #1a1a1a;
        border: 3px solid #ff9500;
        border-radius: 8px;
        padding: 30px;
        max-width: 600px;
        box-shadow: 0 0 30px rgba(255, 149, 0, 0.5), inset 0 0 20px rgba(255, 149, 0, 0.1);
        font-family: 'Courier New', monospace;
        color: #ff9500;
        animation: glitch 0.3s ease-in;
    `;
    
    warningBox.innerHTML = `
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 48px; margin-bottom: 10px; animation: pulse 1.5s infinite;">⚠️</div>
            <div style="font-size: 24px; font-weight: bold; text-transform: uppercase; letter-spacing: 2px; 
                        text-shadow: 0 0 10px rgba(255, 149, 0, 0.8);">
                SYSTEM FALLBACK ACTIVATED
            </div>
        </div>
        
        <div style="background: rgba(255, 149, 0, 0.1); padding: 15px; border-left: 4px solid #ff9500; margin: 20px 0; 
                    font-size: 14px; line-height: 1.6;">
            ${warningData.message.replace(/\n/g, '<br>')}
        </div>
        
        <div style="font-size: 12px; color: #cc7a00; margin: 15px 0; padding: 10px; background: rgba(0,0,0,0.3); 
                    border-radius: 4px;">
            <strong>TECHNICAL DETAILS:</strong><br>
            Requested: <code style="color: #ff9500;">${warningData.requested_model}</code><br>
            Using: <code style="color: #00ff00;">${warningData.actual_model}</code>
        </div>
        
        <div style="text-align: center; margin-top: 25px;">
            <button id="acceptFallback" style="
                background: linear-gradient(180deg, #ff9500 0%, #cc7a00 100%);
                border: 2px solid #ffb84d;
                color: #000;
                padding: 12px 40px;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Courier New', monospace;
                cursor: pointer;
                border-radius: 4px;
                text-transform: uppercase;
                letter-spacing: 1px;
                box-shadow: 0 4px 15px rgba(255, 149, 0, 0.4);
                transition: all 0.2s ease;
            " onmouseover="this.style.transform='scale(1.05)'; this.style.boxShadow='0 6px 20px rgba(255, 149, 0, 0.6)';"
               onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='0 4px 15px rgba(255, 149, 0, 0.4)';">
                CONTINUE ADVENTURE →
            </button>
        </div>
    `;
    
    overlay.appendChild(warningBox);
    document.body.appendChild(overlay);
    
    // Close on button click
    document.getElementById('acceptFallback').addEventListener('click', () => {
        overlay.style.animation = 'fadeOut 0.3s ease-out';
        setTimeout(() => overlay.remove(), 300);
    });
    
    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        @keyframes fadeOut {
            from { opacity: 1; }
            to { opacity: 0; }
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        @keyframes glitch {
            0% { transform: translate(0); }
            20% { transform: translate(-2px, 2px); }
            40% { transform: translate(-2px, -2px); }
            60% { transform: translate(2px, 2px); }
            80% { transform: translate(2px, -2px); }
            100% { transform: translate(0); }
        }
    `;
    document.head.appendChild(style);
}

function createLoadingOverlay() {
    loadingOverlay = document.createElement('div');
    loadingOverlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.85);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        backdrop-filter: blur(4px);
    `;
    
    const spinner = document.createElement('div');
    spinner.style.cssText = `
        text-align: center;
        color: #00ff00;
        font-family: 'Courier New', monospace;
    `;
    
    spinner.innerHTML = `
        <div style="font-size: 48px; margin-bottom: 20px; animation: pulse 1.5s infinite;">⚙</div>
        <div style="font-size: 20px; letter-spacing: 2px;">GENERATING STORY</div>
        <div style="font-size: 14px; margin-top: 10px; opacity: 0.7;">Please wait...</div>
    `;
    
    loadingOverlay.appendChild(spinner);
    document.body.appendChild(loadingOverlay);
}

function showLoading() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

function hideLoading() {
    if (loadingOverlay) {
        loadingOverlay.style.display = 'none';
    }
}

function updateChapterIndicator(title) {
    document.getElementById('currentChapterText').textContent = title;
}

function updateStatus(text) {
    document.getElementById('statusText').textContent = text;
}

function updateBeatIndicator(beat) {
    const formatted = beat.replace(/_/g, ' ').toUpperCase();
    document.getElementById('beatIndicator').textContent = 'BEAT: ' + formatted;
}

function updateSessionDisplay(id) {
    document.getElementById('sessionId').textContent = 'SESSION: ' + id;
}

function addChapterToSidebar(number, title, summary = '') {
    const chaptersList = document.getElementById('chaptersList');
    
    // Remove empty message if exists
    const emptyMsg = chaptersList.querySelector('.empty-message');
    if (emptyMsg) emptyMsg.remove();
    
    // Check if chapter already exists
    const existingChapter = document.getElementById(`chapter-${number}`);
    if (existingChapter) {
        // Update existing chapter summary
        const summaryEl = existingChapter.querySelector('.chapter-item-summary');
        if (summaryEl && summary) {
            summaryEl.textContent = summary;
        }
        return;
    }
    
    const div = document.createElement('div');
    div.className = 'chapter-item';
    div.id = `chapter-${number}`;
    div.onclick = () => toggleChapterSummary(div);
    
    // Generate a simple summary if not provided
    if (!summary) {
        summary = `Chapter ${number}: ${title}`;
    }
    
    div.innerHTML = `
        <div class="chapter-item-title">CHAPTER ${number}: ${title}</div>
        <div class="chapter-item-summary">${summary}</div>
    `;
    
    chaptersList.appendChild(div);
}

function viewChapter(number) {
    // This could scroll to chapter or show chapter details
    alert('Chapter view feature - Would display Chapter ' + number + ' details');
}

function updateDatabaseCounts() {
    if (!sessionId) return;
    
    fetch(`/api/database?session_id=${sessionId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update counts
            document.getElementById('characterCount').textContent = data.characters.length + ' Found';
            document.getElementById('locationCount').textContent = data.locations.length + ' Found';
            document.getElementById('eventCount').textContent = data.events.length + ' Logged';
            
            // Update character list
            const charList = document.getElementById('characters-list');
            charList.innerHTML = '';
            data.characters.forEach(char => {
                const item = document.createElement('div');
                item.className = 'db-item';
                item.onclick = () => toggleItemSummary(item);
                item.innerHTML = `
                    <div class="db-item-name">${char.name}</div>
                    <div class="db-item-summary">${char.description || 'No description available'}</div>
                `;
                charList.appendChild(item);
            });
            
            // Update location list
            const locList = document.getElementById('locations-list');
            locList.innerHTML = '';
            data.locations.forEach(loc => {
                const item = document.createElement('div');
                item.className = 'db-item';
                item.onclick = () => toggleItemSummary(item);
                item.innerHTML = `
                    <div class="db-item-name">${loc.name}</div>
                    <div class="db-item-summary">${loc.description || 'No description available'}</div>
                `;
                locList.appendChild(item);
            });
            
            // Update events list
            const eventList = document.getElementById('events-list');
            eventList.innerHTML = '';
            data.events.forEach((event, index) => {
                const item = document.createElement('div');
                item.className = 'db-item';
                item.onclick = () => toggleItemSummary(item);
                item.innerHTML = `
                    <div class="db-item-name">Event ${index + 1}</div>
                    <div class="db-item-summary">${event.description || event}</div>
                `;
                eventList.appendChild(item);
            });
        }
    });
}

function showDatabase() {
    if (!sessionId) {
        displayError('No active story');
        return;
    }
    
    fetch(`/api/database?session_id=${sessionId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayDatabaseResults({
                query: 'ALL',
                results: {
                    characters: data.characters,
                    locations: data.locations,
                    events: data.events
                }
            });
        }
    });
}

function quickSearch() {
    const query = document.getElementById('quickSearch').value.trim();
    if (!query) return;
    
    searchDatabase(query);
    document.getElementById('quickSearch').value = '';
}

function searchDatabase(query) {
    if (!sessionId) {
        displayError('No active story');
        return;
    }
    
    fetch('/api/search', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            query: query,
            session_id: sessionId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            displayDatabaseResults(data);
        }
    });
}

function displayDatabaseResults(data) {
    const modal = document.getElementById('databaseModal');
    const resultsDiv = document.getElementById('databaseResults');
    
    let html = `<div style="margin-bottom: 20px; color: #40ff40;">Query: <span style="color: #ffb000;">${data.query}</span></div>`;
    
    // Characters
    html += '<div class="db-category">';
    html += '<div class="db-category-title">═══ CHARACTERS ═══</div>';
    if (data.results.characters.length > 0) {
        data.results.characters.forEach(char => {
            html += `
                <div class="db-item">
                    <div class="db-item-name">${char.name}</div>
                    <div class="db-item-detail">First appearance: Chapter ${char.first_appearance}</div>
                    <div class="db-item-detail">Mentions: ${char.mentions}</div>
                    <div class="db-item-detail" style="margin-top: 5px;">${char.description}</div>
                </div>
            `;
        });
    } else {
        html += '<div class="db-no-results">No characters found</div>';
    }
    html += '</div>';
    
    // Locations
    html += '<div class="db-category">';
    html += '<div class="db-category-title">═══ LOCATIONS ═══</div>';
    if (data.results.locations.length > 0) {
        data.results.locations.forEach(loc => {
            html += `
                <div class="db-item">
                    <div class="db-item-name">${loc.name}</div>
                    <div class="db-item-detail">Visits: ${loc.visits}</div>
                    <div class="db-item-detail">${loc.description}</div>
                </div>
            `;
        });
    } else {
        html += '<div class="db-no-results">No locations found</div>';
    }
    html += '</div>';
    
    // Events
    html += '<div class="db-category">';
    html += '<div class="db-category-title">═══ EVENTS ═══</div>';
    if (data.results.events.length > 0) {
        data.results.events.forEach(event => {
            html += `
                <div class="db-item">
                    <div class="db-item-name">Chapter ${event.chapter}</div>
                    <div class="db-item-detail">${event.description}</div>
                </div>
            `;
        });
    } else {
        html += '<div class="db-no-results">No events found</div>';
    }
    html += '</div>';
    
    resultsDiv.innerHTML = html;
    modal.style.display = 'block';
}

function closeDatabase() {
    document.getElementById('databaseModal').style.display = 'none';
    focusInput();
}

function showHelp() {
    document.getElementById('helpModal').style.display = 'block';
}

function closeHelp() {
    document.getElementById('helpModal').style.display = 'none';
    focusInput();
}

function listChapters() {
    if (!sessionId) {
        displayError('No active story');
        return;
    }
    
    fetch(`/api/chapters?session_id=${sessionId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const storyContent = document.getElementById('storyContent');
            const div = document.createElement('div');
            div.className = 'story-text';
            
            let text = '═══ CHAPTERS ═══\n\n';
            data.chapters.forEach(chapter => {
                text += `Chapter ${chapter.number}: ${chapter.title}\n`;
                text += `  Started: ${new Date(chapter.started).toLocaleString()}\n`;
                text += `  Segments: ${chapter.content.length}\n\n`;
            });
            
            div.textContent = text;
            div.style.whiteSpace = 'pre-wrap';
            storyContent.appendChild(div);
            storyContent.scrollTop = storyContent.scrollHeight;
        }
    });
}

function showSummary() {
    if (!sessionId) {
        displayError('No active story');
        return;
    }
    
    fetch(`/api/summary?session_id=${sessionId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            const storyContent = document.getElementById('storyContent');
            const div = document.createElement('div');
            div.className = 'story-text';
            
            let text = '═══ STORY SUMMARY ═══\n\n';
            text += `Chapters: ${data.chapters}\n`;
            text += `Current Beat: ${data.current_beat.replace(/_/g, ' ').toUpperCase()}\n`;
            text += `Actions Taken: ${data.actions_taken}\n\n`;
            text += data.summary;
            
            div.textContent = text;
            div.style.whiteSpace = 'pre-wrap';
            storyContent.appendChild(div);
            storyContent.scrollTop = storyContent.scrollHeight;
        }
    });
}

function clearScreen() {
    document.getElementById('storyContent').innerHTML = '';
    updateStatus('Screen cleared');
}

// Low Power Mode Toggle
function toggleLowPowerMode() {
    lowPowerMode = !lowPowerMode;
    
    if (lowPowerMode) {
        enableLowPowerMode();
    } else {
        disableLowPowerMode();
    }
    
    // Save preference
    localStorage.setItem('lowPowerMode', lowPowerMode.toString());
}

function enableLowPowerMode() {
    lowPowerMode = true;
    document.body.classList.add('low-power-mode');
    document.getElementById('lowPowerToggle').classList.add('active');
    document.getElementById('powerModeIcon').textContent = '🔋';
    document.getElementById('powerModeText').textContent = 'NORMAL MODE';
    updateStatus('Low power mode enabled - animations disabled');
    
    // Disable typing animation
    window.typingAnimationEnabled = false;
}

function disableLowPowerMode() {
    lowPowerMode = false;
    document.body.classList.remove('low-power-mode');
    document.getElementById('lowPowerToggle').classList.remove('active');
    document.getElementById('powerModeIcon').textContent = '⚡';
    document.getElementById('powerModeText').textContent = 'LOW POWER';
    updateStatus('Normal mode enabled - animations active');
    
    // Enable typing animation
    window.typingAnimationEnabled = true;
}

// Close modals when clicking outside
window.onclick = function(event) {
    const dbModal = document.getElementById('databaseModal');
    const helpModal = document.getElementById('helpModal');
    
    if (event.target === dbModal) {
        closeDatabase();
    }
    if (event.target === helpModal) {
        closeHelp();
    }
}

// Prevent page from losing focus
document.addEventListener('click', focusInput);

// Toggle expandable sections in sidebar
function toggleSection(sectionId) {
    const list = document.getElementById(`${sectionId}-list`);
    const icon = document.getElementById(`${sectionId}-icon`);
    
    if (list.style.display === 'none') {
        list.style.display = 'block';
        icon.classList.add('expanded');
    } else {
        list.style.display = 'none';
        icon.classList.remove('expanded');
    }
}

// Toggle individual item summary
function toggleItemSummary(element) {
    element.classList.toggle('expanded');
}

// Toggle chapter summary
function toggleChapterSummary(element) {
    element.classList.toggle('expanded');
}
