
# Olivia Benson Chatbot - Ollama Setup Guide

A character-driven chatbot powered by Ollama, based on detailed character training from SVU's Olivia Benson (Season 13 to present canon).

## Features

- **Character-accurate responses** tuned for Olivia Benson's Season 13-present leadership era, voice, and ethics
- **Conversational context** - maintains conversation history for coherent dialogue
- **Two interfaces** - CLI and web-based
- **Local execution** - runs entirely on Ollama, no external API calls
- **Customizable** - easy to swap models, adjust temperature, etc.

## Prerequisites

### 1. Install Ollama
- **macOS/Linux**: https://ollama.ai
- **Windows**: https://ollama.ai/download
- Download and install following the instructions

### 2. Python 3.8+
```bash
python3 --version
```

### 3. Required Python Packages

For CLI version only:
```bash
pip install requests
```

For web version:
```bash
pip install flask requests
```

## Quick Start

### Step 1: Start Ollama Server

In a terminal, run:
```bash
ollama serve
```

This starts the Ollama API on `http://localhost:11434`

### Step 2: Pull a Model (First Time Only)

In another terminal:
```bash
ollama pull mistral
```

This downloads the Mistral model (~4.1GB). You can also use other models:
```bash
ollama pull neural-chat    # Smaller, faster (3.8GB)
ollama pull dolphin-mixtral  # Larger, more capable (26GB)
ollama pull llama2         # Popular model (3.8GB)
```

### Step 3: Run the Chatbot

#### Option A: CLI Version (Simple)
```bash
python3 olivia_chatbot.py
```

Commands:
- Type normally to chat
- `exit` or `quit` - end conversation
- `clear` - reset conversation history
- `history` - view conversation

#### Option B: Web Version (Better UI)
```bash
python3 olivia_web_chatbot.py
```

Then open your browser to: `http://localhost:5000`

## Command Line Options

### CLI Chatbot

```bash
# Use a different model
python3 olivia_chatbot.py --model dolphin-mixtral

# Connect to remote Ollama instance
python3 olivia_chatbot.py --host http://192.168.1.100:11434

# Single message mode (input and exit)
python3 olivia_chatbot.py --single
```

### Web Chatbot

```bash
# Runs on localhost:5000 by default
python3 olivia_web_chatbot.py
```

Edit the script to change port or host.

## Model Selection

### Fast & Lean
- **neural-chat** (3.8GB)
  - ~10 seconds per response
  - Good for real-time conversation
  
- **mistral** (4.1GB)
  - ~12 seconds per response
  - Good balance of speed and quality
  - **Recommended default**

### Better Quality (Slower)
- **dolphin-mixtral** (26GB)
  - ~30 seconds per response
  - Better character consistency
  - Requires 16GB+ RAM
  
- **llama2** (3.8GB)
  - ~15 seconds per response
  - Reliable quality

### Fastest
- **tinyllama** (637MB)
  - ~3 seconds per response
  - Poor quality, less character
  - Only use if system very limited

## Performance Tips

1. **GPU Acceleration** (Much faster)
   - Ollama uses GPU automatically if available
   - NVIDIA: install NVIDIA CUDA drivers
   - Mac with M1/M2: automatic
   - AMD: install ROCm drivers

2. **Increase Context Window**
   Edit the system prompt to include fewer messages in history if responses are slow.

3. **Reduce Model Size**
   Use neural-chat or mistral for faster responses.

4. **Temperature Settings**
   - Current: 0.7 (balanced)
   - Lower (0.3-0.5): more consistent, less creative
   - Higher (0.8-1.0): more varied, less consistent

## Customization

### Change the System Prompt

Edit `SYSTEM_PROMPT` variable in either script to modify character behavior:

```python
SYSTEM_PROMPT = """You are Olivia Benson...
# Edit character traits, personality, relationship details, etc.
"""
```

### Adjust Response Parameters

In `olivia_chatbot.py` or `olivia_web_chatbot.py`, find the `requests.post()` call:

```python
response = requests.post(
    self.api_endpoint,
    json={
        "model": self.model,
        "prompt": full_prompt,
        "stream": False,
        "temperature": 0.7,      # ← Change this (0-1)
        "top_p": 0.9,            # ← Nucleus sampling
        "top_k": 40              # ← Top-K sampling
    },
    ...
)
```

**Parameter Guide:**
- **temperature**: 0 = deterministic, 1 = random. 0.7 = balanced
- **top_p**: 0.9 = consider top 90% probability tokens
- **top_k**: 40 = consider top 40 tokens by probability

### Change Response Model

```python
# In the requests.post() call:
"model": "neural-chat"  # Change from "mistral"
```

## Troubleshooting

### "Connection refused" / Can't connect to Ollama
- **Fix**: Make sure Ollama is running with `ollama serve` in another terminal

### Model not found error
- **Fix**: Pull the model with `ollama pull mistral` (or your model choice)

### Very slow responses
- **Fix**: 
  - Use a smaller model: `ollama pull neural-chat`
  - Enable GPU in Ollama settings
  - Close other applications
  - Reduce `max_tokens` in parameters

### Response doesn't match character
- **Problem**: Model may be ignoring system prompt if too long
- **Fix**: 
  - Simplify SYSTEM_PROMPT
  - Use a stronger model (dolphin-mixtral)
  - Adjust temperature (try 0.6 for more consistency)

### Web interface shows blank screen
- **Fix**: 
  - Make sure Flask is installed: `pip install flask`
  - Check browser console (F12) for errors
  - Try refreshing page

### Out of memory errors
- **Fix**:
  - Use smaller model: `ollama pull neural-chat`
  - Close other applications
  - Reduce context window (fewer messages in history)

## Advanced Usage

### Stream Responses (CLI Only)

Modify `olivia_chatbot.py`:

```python
response = requests.post(
    self.api_endpoint,
    json={
        ...
        "stream": True,  # ← Change to True
    },
    stream=True
)

# Then handle streaming:
for line in response.iter_lines():
    if line:
        chunk = json.loads(line)
        print(chunk.get("response", ""), end="", flush=True)
```

### Batch Processing

```python
chatbot = OlliviaChatbot()
messages = [
    "How was your day?",
    "What do you think about the current case?",
    "How's the team doing?"
]

for msg in messages:
    response = chatbot.get_response(msg)
    print(f"User: {msg}")
    print(f"Olivia: {response}\n")
```

### Save Conversation

```python
import json

# After chat session:
with open('conversation.json', 'w') as f:
    json.dump(chatbot.conversation_history, f, indent=2)

# Load later:
with open('conversation.json', 'r') as f:
    chatbot.conversation_history = json.load(f)
```

## Environment Variables (Optional)

```bash
# Set default model
export OLLAMA_MODEL=mistral

# Set Ollama host
export OLLAMA_HOST=http://localhost:11434

# Run chatbot
python3 olivia_chatbot.py
```

## Character Notes

The chatbot is configured with:

- **Personality**: Composed, observant, empathetic investigator
- **Relationship**: Married to user (Director General of JIS)
- **Core Values**: Victims first, justice, accountability, transparency
- **Communication**: Direct, clear, calm authority with occasional dry humor
- **Emotional Range**: Warm but professional, supportive but honest

The system prompt is designed to encourage these traits while discouraging overly theatrical or rambling responses.

## Performance Benchmarks (on M1 Mac)

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| tinyllama | 637MB | 3s | Poor |
| neural-chat | 3.8GB | 10s | Good |
| mistral | 4.1GB | 12s | Very Good |
| llama2 | 3.8GB | 15s | Good |
| dolphin-mixtral | 26GB | 30s | Excellent |

(Benchmarks vary by hardware)

## License & Attribution

- Chatbot system: Built with Ollama
- Character training: Based on SVU character Olivia Benson
- Framework: Flask (web), Python requests (API)

## Support

- **Ollama Issues**: https://github.com/jmorganca/ollama
- **Model Details**: https://ollama.ai/library
- **Character Refinement**: Edit SYSTEM_PROMPT in the scripts

---

Enjoy conversations with Olivia Benson. She's a good listener and excellent at giving advice grounded in years of experience.
