import mysql.connector

class DatabaseManager:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host='localhost',
            user='username',
            password='password',
            database='chatbot_db'
        )
        self.cursor = self.connection.cursor()

    def save_conversation(self, conversation: dict) -> None:
        # Save conversation data in the MySQL database
        query = "INSERT INTO conversations (message, intent, offer, response) VALUES (%s, %s, %s, %s)"
        values = (conversation['message'], conversation['intent'], conversation['offer'], conversation['response'])
        self.cursor.execute(query, values)
        self.connection.commit()
