import json
import random
import os
import openai
from dotenv import load_dotenv

load_dotenv()

class ChatbotEngine:
    def __init__(self):
        self.intents = self.load_intents()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def load_intents(self):
        intents_path = os.path.join(os.path.dirname(__file__), '../../data/intents.json')
        with open(intents_path, 'r') as file:
            return json.load(file)

    def get_response(self, message):
        try:
            # First try to find a matching intent for common queries
            for intent in self.intents['intents']:
                if any(pattern.lower() in message.lower() for pattern in intent['patterns']):
                    return random.choice(intent['responses'])

            # If no matching intent found, use OpenAI API
            openai_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful and friendly AI assistant."},
                    {"role": "user", "content": message}
                ]
            )
            return openai_response.choices[0].message.content

        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return "I'm sorry, I'm having trouble processing your request. Please try again later."
