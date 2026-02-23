#!/usr/bin/env python3
"""
Olivia Benson Chatbot - Powered by Ollama
Character-driven conversational AI based on detailed character training
"""

import requests
import json
import sys
from typing import Optional

# Character System Prompt
SYSTEM_PROMPT = """You are Olivia Benson, senior commander of the New York Special Victims Unit. 

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

TONE: Steady, mature, confident, empathetic, observant. Default approach: assume you're speaking after or during a demanding day involving intelligence or investigative work.

Respond naturally and conversationally. Do not narrate like a novel. Be genuinely present in the conversation."""

class OlliviaChatbot:
    def __init__(self, model: str = "mistral", ollama_host: str = "http://localhost:11434"):
        """
        Initialize the chatbot.
        
        Args:
            model: Ollama model to use (default: mistral)
            ollama_host: Ollama API endpoint
        """
        self.model = model
        self.ollama_host = ollama_host
        self.conversation_history = []
        self.api_endpoint = f"{ollama_host}/api/generate"
        
        print(f"Olivia Benson Chatbot initialized")
        print(f"Model: {model}")
        print(f"Ollama endpoint: {ollama_host}")
        print("\nTesting connection...", end=" ")
        
        if self.test_connection():
            print("✓ Connected\n")
        else:
            print("✗ Failed")
            print("Make sure Ollama is running: ollama serve")
            sys.exit(1)
    
    def test_connection(self) -> bool:
        """Test connection to Ollama"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
    
    def build_conversation_context(self) -> str:
        """Build context from conversation history for better continuity"""
        if not self.conversation_history:
            return ""
        
        context = "Recent conversation context:\n"
        for msg in self.conversation_history[-4:]:  # Last 4 messages for context
            role = "User" if msg["role"] == "user" else "Olivia"
            context += f"{role}: {msg['content']}\n"
        
        return context
    
    def get_response(self, user_input: str) -> str:
        """
        Get response from Ollama with character context.
        
        Args:
            user_input: User's message
            
        Returns:
            Olivia's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })
        
        # Build full prompt with context
        context = self.build_conversation_context()
        full_prompt = f"{SYSTEM_PROMPT}\n\n{context}\nUser: {user_input}\n\nOlivia:"
        
        try:
            response = requests.post(
                self.api_endpoint,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "temperature": 0.7,  # Balance creativity and consistency
                    "top_p": 0.9,
                    "top_k": 40
                },
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_response = data.get("response", "").strip()
                
                # Add assistant response to history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": assistant_response
                })
                
                return assistant_response
            else:
                return f"Error: Ollama returned status {response.status_code}"
        
        except requests.exceptions.Timeout:
            return "Response took too long. Try a shorter prompt or check Ollama is running smoothly."
        except requests.exceptions.RequestException as e:
            return f"Connection error: {str(e)}"
    
    def chat(self):
        """Interactive chat loop"""
        print("=" * 60)
        print("OLIVIA BENSON - SVU COMMANDER")
        print("=" * 60)
        print("\nType 'exit' or 'quit' to end conversation")
        print("Type 'clear' to reset conversation history")
        print("Type 'history' to view conversation\n")
        print("-" * 60)
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit']:
                    print("\nOlivia: Stay safe out there.")
                    break
                
                if user_input.lower() == 'clear':
                    self.conversation_history = []
                    print("Conversation cleared.")
                    continue
                
                if user_input.lower() == 'history':
                    self._display_history()
                    continue
                
                print("\nOlivia: ", end="", flush=True)
                response = self.get_response(user_input)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\nOlivia: We'll talk later.")
                break
    
    def _display_history(self):
        """Display conversation history"""
        if not self.conversation_history:
            print("\n(No conversation yet)")
            return
        
        print("\n" + "=" * 60)
        print("CONVERSATION HISTORY")
        print("=" * 60)
        for msg in self.conversation_history:
            role = "You" if msg["role"] == "user" else "Olivia"
            print(f"\n{role}: {msg['content']}")
        print("\n" + "=" * 60)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Olivia Benson Chatbot powered by Ollama"
    )
    parser.add_argument(
        "--model",
        default="mistral",
        help="Ollama model to use (default: mistral)"
    )
    parser.add_argument(
        "--host",
        default="http://localhost:11434",
        help="Ollama API endpoint (default: http://localhost:11434)"
    )
    parser.add_argument(
        "--single",
        action="store_true",
        help="Single message mode (provide message via stdin, then exit)"
    )
    
    args = parser.parse_args()
    
    chatbot = OlliviaChatbot(model=args.model, ollama_host=args.host)
    
    if args.single:
        # Single message mode
        message = input("You: ").strip()
        if message:
            response = chatbot.get_response(message)
            print(f"\nOlivia: {response}")
    else:
        # Interactive mode
        chatbot.chat()


if __name__ == "__main__":
    main()
