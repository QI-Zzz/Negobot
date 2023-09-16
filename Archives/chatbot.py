from intent_classifier import IntentClassifier
from database_manager import DatabaseManager

class Chatbot:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.database_manager = DatabaseManager()

    def process_message(self, message: str) -> str:
        user_intent = self.intent_classifier.classify_intent(message)
        user_offer = self.extract_price(message)

        # Generate response based on conversation history, user offer, and user intent
        response = self.generate_response(user_intent, user_offer)

        # Save conversation data in the database
        conversation = {
            'message': message,
            'intent': user_intent,
            'offer': user_offer,
            'response': response
        }
        self.database_manager.save_conversation(conversation)

        return response

    def extract_price(self, message: str) -> float:
        # Extract the price from the user's message
        # Implement your logic here to extract the price
        pass

    def generate_response(self, user_intent: str, user_offer: float) -> str:
        # Generate response based on conversation history, user offer, and user intent
        # Implement your logic here to generate the response
        pass
