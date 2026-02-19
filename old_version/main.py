"""
Example usage of the Data Processing Chatbot
Interactive natural language interface for data processing using LLM-generated code
"""

import os
from chatbot import DataProcessingChatbot

def main():
    # Initialize the chatbot with LLM
    print("Initializing Data Processing Chatbot with LLM...")
    
    # Get API key from environment variable
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")

    model = "gpt-4o-mini-2024-07-18"   # Alternative models: "gpt-3.5-turbo", "gpt-4o-mini"
    
    chatbot = DataProcessingChatbot(
        llm_api_key=api_key,
        llm_model=model,
        llm_provider="openai"  # or "anthropic"
    )
    
    print(f"Using model: {model} \n")
    
    # Start interactive chat session
    chatbot.start_chat()

if __name__ == "__main__":
    main()
