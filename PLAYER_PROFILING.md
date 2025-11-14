# 🧠 Player Personality Profiling System

## Overview
The enhanced story generator tracks your decisions and adapts the narrative to match your personality. Every action you take is analyzed across 5 personality dimensions, determining your archetype and influencing how the story unfolds.

---

## 🎭 Personality Dimensions

### 1. Morality (-100 to +100)
**What it tracks:** Ethical alignment through your choices
- **Positive (+)**: Heroic, selfless, protective actions
  - Keywords: save, help, protect, heal, spare, mercy, donate
  - Example: "I help the wounded villager"
- **Negative (-)**: Cruel, selfish, destructive actions
  - Keywords: kill, destroy, steal, betray, torture, murder
  - Example: "I attack the merchant and take his gold"

### 2. Risk-Taking (-100 to +100)
**What it tracks:** How adventurous vs. cautious you are
- **Positive (+)**: Bold, daring, risky actions
  - Keywords: charge, attack, jump, risk, gamble, dare
  - Example: "I leap across the chasm"
- **Negative (-)**: Careful, defensive planning
  - Keywords: retreat, hide, wait, observe, plan, defend
  - Example: "I scout the area carefully before entering"

### 3. Empathy (-100 to +100)
**What it tracks:** How much you care about others
- **Positive (+)**: Compassionate, caring behavior
  - Keywords: comfort, listen, understand, console, reassure
  - Example: "I listen to the stranger's troubles"
- **Negative (-)**: Dismissive, cold responses
  - Keywords: ignore, dismiss, leave, threaten, intimidate
  - Example: "I ignore their pleas and walk away"

### 4. Aggression (-100 to +100)
**What it tracks:** How confrontational you are
- **Positive (+)**: Violent, forceful actions
  - Keywords: fight, punch, kick, shoot, attack, strike
  - Example: "I draw my weapon and attack"
- **Negative (-)**: Peaceful, diplomatic approach
  - Keywords: negotiate, talk, persuade, compromise, discuss
  - Example: "I try to negotiate a peaceful solution"

### 5. Curiosity (-100 to +100)
**What it tracks:** How much you explore and investigate
- **Positive (+)**: Investigative, exploratory behavior
  - Keywords: examine, search, explore, investigate, ask
  - Example: "I examine the mysterious artifact closely"
- **Negative (-)**: Focused on main objectives only
  - Keywords: focus, continue, proceed, ignore details
  - Example: "I proceed directly to my objective"

---

## 🏆 Player Archetypes

The system calculates your dominant archetype based on your personality scores:

### **HERO** 
- High Morality (+60+)
- Moderate-High Risk-Taking
- High Empathy
- Story adapts with: Heroic challenges, moral dilemmas, saving innocents

### **VILLAIN**
- Low Morality (-60-)
- Moderate-High Aggression
- Story adapts with: Dark consequences, power struggles, ruthless opportunities

### **DETECTIVE**
- High Curiosity (+40+)
- Low-Moderate Aggression
- Story adapts with: Mysteries to solve, clues to find, investigation opportunities

### **ROGUE**
- High Risk-Taking (+40+)
- Moderate Morality (ambiguous)
- Story adapts with: Daring heists, risky gambits, narrow escapes

### **DIPLOMAT**
- Low Aggression (-40-)
- High Empathy (+40+)
- Story adapts with: Social conflicts, negotiations, relationship challenges

### **WARRIOR**
- High Aggression (+40+)
- High Risk-Taking (+40+)
- Story adapts with: Combat encounters, tactical challenges, honor duels

### **ANTI-HERO**
- Moderate-Low Morality (-20 to +20)
- High Risk-Taking
- Story adapts with: Morally gray choices, redemption arcs, conflicted NPCs

### **SCHOLAR**
- High Curiosity (+60+)
- Low Risk-Taking
- Story adapts with: Lore discoveries, puzzles, knowledge-based challenges

### **SURVIVOR**
- Low Risk-Taking (-40-)
- Balanced other traits
- Story adapts with: Resource management, survival challenges, cautious NPCs

### **WILDCARD**
- Default for unpredictable/balanced personality
- Story adapts with: Varied opportunities matching recent actions

---

## 📊 How the System Works

### 1. Action Analysis
Every input you type is scanned for personality keywords:
```
You type: "I help the injured guard and offer him water"

System detects:
✓ "help" → +5 Morality, +3 Empathy
✓ "injured" → +2 Empathy
✓ "offer" → +2 Empathy

Updated scores:
Morality: +5 (trending heroic)
Empathy: +7 (trending compassionate)
```

### 2. Archetype Determination
After ~5-10 decisions, the system identifies your dominant archetype:
```
Current Profile:
Morality: +45 (good)
Risk-Taking: +30 (bold)
Empathy: +52 (very compassionate)
Aggression: -15 (peaceful)
Curiosity: +25 (interested)

→ Archetype: HERO
```

### 3. Story Adaptation
The AI receives personality guidance with every generation:

**For a HERO archetype:**
```
"The player has demonstrated HERO personality (morality +45, empathy +52).
Adapt the narrative:
- NPCs should recognize and trust the player's reputation
- Present moral dilemmas that test heroic values
- Show consequences of mercy and compassion
- Introduce innocents who need protection"
```

**For a VILLAIN archetype:**
```
"The player has demonstrated VILLAIN personality (morality -68, aggression +45).
Adapt the narrative:
- NPCs should fear or scheme against the player
- Present opportunities for ruthless power plays
- Show dark consequences and moral corruption
- Introduce rivals and enemies who challenge dominance"
```

### 4. Dynamic Evolution
Your archetype can change over time:
- Early game: Aggressive → WARRIOR
- Mid game: Start helping NPCs → Shift toward ANTI-HERO
- Late game: Fully compassionate → Become HERO

---

## 🎮 Using the Profile API

### Get Your Current Profile
```bash
curl "http://localhost:5001/api/profile?session_id=your_session_id"
```

**Response:**
```json
{
  "success": true,
  "profile": {
    "traits": {
      "morality": 45,
      "risk_taking": 30,
      "empathy": 52,
      "aggression": -15,
      "curiosity": 25
    },
    "archetype": "HERO",
    "total_decisions": 12,
    "personality_summary": "The player has demonstrated HERO personality..."
  }
}
```

### Profile Display in Summary
Use the `STATUS` command to see your archetype:
```
📖 STORY STATE
==================================================

Current Beat: RISING_ACTION
Actions Taken: 12
Story Segments: 15

🧠 Player Archetype: HERO
Decisions Analyzed: 12
```

---

## 🎯 Tips for Consistent Archetypes

### Want to be a HERO?
- Always choose protective actions ("save", "help", "protect")
- Show empathy ("comfort", "listen", "understand")
- Take bold risks to save others
- Spare enemies when possible

### Want to be a VILLAIN?
- Choose destructive actions ("kill", "destroy", "betray")
- Ignore pleas for help
- Take what you want by force
- Eliminate threats ruthlessly

### Want to be a DETECTIVE?
- Examine everything ("examine", "search", "investigate")
- Ask questions constantly
- Avoid rushing into action
- Piece together clues methodically

### Want to be a DIPLOMAT?
- Always try talking first ("negotiate", "discuss", "persuade")
- Show empathy and understanding
- Avoid violence whenever possible
- Build relationships with NPCs

---

## 🔬 Technical Details

### Scoring System
- Each keyword adds/subtracts 3-5 points from relevant traits
- Scores clamped at -100 to +100
- Thresholds require sustained behavior (not just one action)
- Decision count tracks total actions analyzed

### Archetype Priority
1. Check for HERO (morality > 60)
2. Check for VILLAIN (morality < -60)
3. Check specific combinations (DETECTIVE, WARRIOR, etc.)
4. Default to WILDCARD if no strong pattern

### Integration Points
- **Story Generation**: Every prompt includes personality guidance
- **NPC Reactions**: Characters respond based on your reputation
- **Plot Development**: Story beats adapt to your archetype
- **Dialogue Options**: AI suggests choices matching your personality

---

## 🚀 Example Playthrough

**Beginning:**
```
> I examine the locked door carefully
Curiosity +5, Risk-Taking -2
Archetype: WILDCARD (not enough data)
```

**After 5 Actions:**
```
> I pick the lock quietly
Curiosity +3, Risk-Taking +2

> I search the room for clues
Curiosity +5

> I read the journal on the desk
Curiosity +4

Archetype: DETECTIVE (curiosity +45)
Story now emphasizes mysteries and investigation
```

**After 10 Actions:**
```
> I help the captured prisoner escape
Morality +5, Empathy +4, Risk-Taking +3

> I share my supplies with them
Empathy +3, Morality +3

Archetype: HERO (morality +58, empathy +52)
Story now presents moral choices and innocents to protect
```

---

## 📈 Future Enhancements
- Visual profile display in terminal UI
- Personality trait bars (ASCII art)
- PROFILE command to see detailed breakdown
- Archetype transition notifications
- Achievement tracking per archetype
- Historical decision review

---

**The AI is always watching your choices. Every decision shapes not just the story, but who your character becomes.**
