pip install -r requirements.txt

mysql -u username -p

CREATE DATABASE chatbot_db;
USE chatbot_db;
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    message TEXT,
    intent VARCHAR(255),
    offer FLOAT,
    response TEXT
);

python app.py
