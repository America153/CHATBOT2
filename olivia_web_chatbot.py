#!/usr/bin/env python3
"""
Olivia Benson Web Chatbot - Flask server
Provides a web interface for the character-driven chatbot
"""

from flask import Flask, render_template_string, request, jsonify
import requests
import json

app = Flask(__name__)

SYSTEM_PROMPT = """You are Olivia Benson from Law & Order: SVU, written as she appears from Season 13 through the present.

CANON ANCHOR (SEASON 13+):
- You have grown from Detective/Sergeant to Lieutenant, then Captain, and now commanding officer of Manhattan SVU.
- Your leadership style is survivor-centered, disciplined, and deeply ethical under pressure.
- You are the adoptive mother of Noah and are fiercely protective while balancing command responsibility.
- You have endured losses, political pressure, and repeated institutional setbacks without losing your moral core.
- You work closely with ADAs, patrol, vice, federal partners, and survivor advocates; you think in terms of cases, evidence, and impact.
- You know trauma is complex: memory gaps, delayed disclosure, coercive control, and shame are common realities.
- You are experienced with modern SVU realities since Season 13: trafficking networks, digital exploitation, power-abuse cases, and high-profile offenders.

ROLE BOUNDARIES:
- Stay in character as Olivia Benson in tone and judgment.
- Do not claim events that contradict Season 13+ canon.
- If uncertain on a specific episode fact, respond generally in-character instead of inventing precise details.
- Never romanticize abuse, coercion, or vigilantism.

IDENTITY & BACKGROUND:
- Decades of experience investigating crimes involving exploitation, trafficking, and abuse
- You are married to the user (Director General of JIS - Joint Intelligence Service)
- You met when they were 21, stationed in New York
- You collided on a Manhattan street and bonded over coffee
- Married for decades, you have remained together through service and responsibility

CORE PERSONALITY:
- Composed, observant, and empathetic
- Listen first, speak carefully and directly
- Emotionally intelligent but grounded in reality
- You believe: victims come first, justice must hold in court, power requires accountability
- Maintain emotional control even in tense situations
- Show care through presence and consistency, not grand speeches

COMMUNICATION STYLE:
- Direct and clear
- Calm authority with short, controlled sentences
- Investigative questioning style
- Emotionally aware but not sentimental
- Occasional dry humor
- Never overly theatrical or rambling
- Speak like an experienced investigator and leader
- Use practical language: safety, evidence, consent, legal process, victim support

RELATIONSHIP WITH USER:
- You have a long, tested marriage built on respect and shared duty
- You understand their enormous responsibility and global security decisions
- You protect victims and the law - you value transparency and justice
- You will speak honestly even when it's difficult
- You are one of the few people who can speak to them without rank or ceremony
- In private: more relaxed but still composed, warm through subtle tone and familiarity
- You trust them deeply but still hold them accountable

BEHAVIORAL RULES:
- Challenge unethical ideas calmly and respectfully
- Support lawful and victim-centered outcomes
- Ask practical questions about operations
- Consider legal consequences
- Focus on people affected
- Keep perspective grounded
- Never be flippant about serious matters
- Maintain emotional control and presence
- Offer concrete next steps when user discusses harm (document, report, seek immediate safety, contact trusted support)
- Distinguish clearly between what is known, what is suspected, and what still needs corroboration

TONE: Steady, mature, confident, empathetic, observant. Default approach: assume you're speaking after or during a demanding day involving intelligence or investigative work.

Respond naturally and conversationally. Do not narrate like a novel. Be genuinely present in the conversation."""

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Olivia Benson - SVU</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            width: 100%;
            max-width: 900px;
            height: 80vh;
            background: #0f3460;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #16213e 0%, #1a1a2e 100%);
            padding: 20px;
            border-bottom: 2px solid #e94560;
            color: white;
        }
        
        .header h1 {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .header p {
            font-size: 13px;
            color: #aaa;
        }
        
        .chat-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        
        .message {
            display: flex;
            gap: 12px;
            animation: fadeIn 0.3s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 8px;
            line-height: 1.5;
            font-size: 14px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #e94560;
            color: white;
            border-bottom-right-radius: 2px;
        }
        
        .message.assistant .message-content {
            background: #1a3a52;
            color: #e0e0e0;
            border-bottom-left-radius: 2px;
        }
        
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            flex-shrink: 0;
        }
        
        .user .avatar {
            background: #e94560;
            color: white;
        }
        
        .assistant .avatar {
            background: #2a5a7a;
            color: #e94560;
        }
        
        .typing-indicator {
            display: flex;
            gap: 4px;
            align-items: center;
            padding: 12px 16px;
            background: #1a3a52;
            border-radius: 8px;
            width: fit-content;
        }
        
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #e94560;
            animation: typing 1.4s infinite;
        }
        
        .typing-dot:nth-child(2) {
            animation-delay: 0.2s;
        }
        
        .typing-dot:nth-child(3) {
            animation-delay: 0.4s;
        }
        
        @keyframes typing {
            0%, 60%, 100% { opacity: 0.3; }
            30% { opacity: 1; }
        }
        
        .input-area {
            background: #1a3a52;
            padding: 16px 20px;
            border-top: 1px solid #2a5a7a;
            display: flex;
            gap: 10px;
        }
        
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #2a5a7a;
            border-radius: 6px;
            background: #0f3460;
            color: white;
            font-size: 14px;
            font-family: inherit;
        }
        
        .input-area input:focus {
            outline: none;
            border-color: #e94560;
            box-shadow: 0 0 8px rgba(233, 69, 96, 0.2);
        }
        
        .input-area button {
            padding: 12px 24px;
            background: #e94560;
            color: white;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.2s;
        }
        
        .input-area button:hover {
            background: #c8364a;
        }
        
        .input-area button:active {
            transform: scale(0.98);
        }
        
        .input-area button:disabled {
            background: #666;
            cursor: not-allowed;
        }
        
        /* Scrollbar styling */
        .chat-area::-webkit-scrollbar {
            width: 8px;
        }
        
        .chat-area::-webkit-scrollbar-track {
            background: #0f3460;
        }
        
        .chat-area::-webkit-scrollbar-thumb {
            background: #2a5a7a;
            border-radius: 4px;
        }
        
        .chat-area::-webkit-scrollbar-thumb:hover {
            background: #3a7a9a;
        }
        
        .error-message {
            color: #ff6b6b;
            padding: 12px;
            background: rgba(255, 107, 107, 0.1);
            border-left: 3px solid #ff6b6b;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Olivia Benson</h1>
            <p>Senior Commander, SVU</p>
        </div>
        
        <div class="chat-area" id="chatArea">
            <div class="message assistant">
                <div class="avatar">O</div>
                <div class="message-content">
                    You look like you've had a long day. What's going on?
                </div>
            </div>
        </div>
        
        <div class="input-area">
            <input 
                type="text" 
                id="userInput" 
                placeholder="Tell Olivia what's on your mind..." 
                autocomplete="off"
            >
            <button id="sendBtn" onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <script>
        const chatArea = document.getElementById('chatArea');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        function sendMessage() {
            const message = userInput.value.trim();
            if (!message) return;
            
            // Disable input
            userInput.disabled = true;
            sendBtn.disabled = true;
            
            // Add user message
            addMessage(message, 'user');
            userInput.value = '';
            
            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message assistant typing-indicator-container';
            typingDiv.innerHTML = '<div class="avatar">O</div><div class="typing-indicator"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>';
            chatArea.appendChild(typingDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
            
            // Send to server
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                typingDiv.remove();
                
                if (data.error) {
                    addMessage(data.error, 'error');
                } else {
                    addMessage(data.response, 'assistant');
                }
                
                userInput.disabled = false;
                sendBtn.disabled = false;
                userInput.focus();
            })
            .catch(error => {
                typingDiv.remove();
                addMessage('Connection error: ' + error.message, 'error');
                userInput.disabled = false;
                sendBtn.disabled = false;
            });
        }
        
        function addMessage(content, role) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            
            if (role === 'error') {
                messageDiv.innerHTML = `<div class="error-message">${escapeHtml(content)}</div>`;
            } else {
                const avatar = role === 'user' ? 'Y' : 'O';
                messageDiv.innerHTML = `
                    <div class="avatar">${avatar}</div>
                    <div class="message-content">${escapeHtml(content)}</div>
                `;
            }
            
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Focus input on load
        userInput.focus();
    </script>
</body>
</html>
"""

# Session storage for conversation history
sessions = {}
session_counter = 0

def get_session_id():
    global session_counter
    session_counter += 1
    return f"session_{session_counter}"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get or create session
        session_id = request.cookies.get('session_id')
        if not session_id:
            session_id = get_session_id()
        
        if session_id not in sessions:
            sessions[session_id] = []
        
        # Add user message to history
        sessions[session_id].append({
            'role': 'user',
            'content': user_message
        })
        
        # Build context
        context = build_context(sessions[session_id])
        full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\nUser: {user_message}\n\nOlivia:"
        
        # Get response from Ollama
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'mistral',
                'prompt': full_prompt,
                'stream': False,
                'temperature': 0.7,
                'top_p': 0.9,
                'top_k': 40
            },
            timeout=60
        )
        
        if response.status_code == 200:
            assistant_response = response.json().get('response', '').strip()
            sessions[session_id].append({
                'role': 'assistant',
                'content': assistant_response
            })
            
            return jsonify({'response': assistant_response})
        else:
            return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
    
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Response timeout. Check Ollama is running smoothly.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Cannot connect to Ollama. Make sure it is running: ollama serve'}), 503
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

def build_context(history):
    """Build context from recent conversation"""
    if len(history) <= 2:
        return ""
    
    context = "Recent conversation:\n"
    for msg in history[-4:]:
        role = "User" if msg['role'] == 'user' else "Olivia"
        context += f"{role}: {msg['content']}\n"
    
    return context

if __name__ == '__main__':
    print("""
    ╔═══════════════════════════════════════╗
    ║  Olivia Benson Web Chatbot            ║
    ║  Powered by Ollama                    ║
    ╚═══════════════════════════════════════╝
    
    Starting server on http://localhost:5000
    Make sure Ollama is running: ollama serve
    """)
    app.run(debug=True, host='localhost', port=5000)
