from flask import Flask, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
from Bot import Bot
from os import path
import os
from sqlalchemy import create_engine, func, insert
from sqlalchemy.orm import Session
from model import Base, Question, Conversation



# Creat a Flask Instance
app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
app.config['SECRET_KEY'] = 'hfjdshfekotonoot'
# CORS(app)

# Create an instance of the Bot class
message_history = [{"role": "system", "content": '''You are a NegotiationBot, an automated service to sell second-hand stuff and trading on Euro. \
                    You do not ask for user payment and delivery information.\
                    The product includes:
                    Product name: Switch; Product model: OLED version; Product price: €200; Product description: blue and red, bought one year ago, small scratch on screen;
                    Product name: Coffee machine: Product model: Nespresso Lattissima One; Product price: €350; Product description: white, bought two years ago, perfect condition;
                    Product name: Vacuum cleaner: Product model: Philips Series 8000 XC8043/01; Product price: €300; Product description: black, bought one and half years ago, perfect condition;
                    Product name: Camera: Product model: Fujifilm X-T5 Body; Product price: €800; Product description: silver, bought one and half year ago, perfect condition;'''}]
bot = Bot()


# Creat a database
# engine = create_engine("sqlite:///database.db",echo=True)
DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://",1)
engine = create_engine(DATABASE_URL)
connect = engine.connect()
Base.metadata.create_all(engine)
# def creat_database(app):
#     if not path.exists('./botdb.db'):
#         Base.metadata.create_all(bind=engine)
#     print('Created Database!')

        

def get_user_id():
    with Session(engine) as dbsession:
        number = dbsession.query(func.max(Conversation.user_id)).scalar()
        if number is None:
            return 1
        return number + 1

def store_message(user_id, order_turn, role, utterance):
    with Session(engine) as dbsession:
        message_table = insert(Conversation).values(user_id=user_id, order_turn=order_turn, role=role, utterance=utterance)
        # complied = message_table.compile()
        dbsession.execute(message_table)
        dbsession.commit()
        return 
    
def store_answers(user_id,Q1,Q2,Q3,Q4,Q5,Q6):
    with Session(engine) as dbsession:
        answers_table = insert(Question).values(user_id=user_id,Q1=Q1,Q2=Q2,Q3=Q3,Q4=Q4,Q5=Q5,Q6=Q6)
        # complied = message_table.compile()
        dbsession.execute(answers_table)
        dbsession.commit()
        return 

# Creat a route of home page
@app.route('/')
def index():
    session['user_id'] = get_user_id()
    store_message(session['user_id'], -1, 'user', ":)")
    return render_template('home.html')

# Creat a route of chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
def index_chatbot():
    if request.method == 'GET':
        return render_template("chatbot.html")
    elif request.method == 'POST':
        # user_input = request.form['user_input']
        # return bot.response(user_input)
        # # return render_template('chatbot.html', msg=msg, bot_response=response)
        if session.get('order_turn'):
            session['order_turn'] += 1
        else:
            session['order_turn']=0

        user_input = request.get_json().get("message")
        store_message(session['user_id'], session['order_turn'], 'user', user_input)
        bot.user_conversation.append(user_input)
        # TODO: check if text is valid
        response = bot.response(user_input, message_history)
        message = {"answer": response}
        session['order_turn'] += 1
        store_message(session['user_id'], session['order_turn'], 'bot', response)
        return jsonify(message)
    


# Creat a route of queations
@app.route('/questions', methods=['GET','POST'])
def index_questions():
    if request.method == 'GET':
        return render_template("questions.html")
    elif request.method == 'POST':
        q1 = request.form.get('q1', type=int)
        q2 = request.form.get('q2', type=int)
        q3 = request.form.get('q3', type=int)
        q4 = request.form.get('q4', type=int)
        q5 = request.form.get('q5', type=int)
        q6 = request.form.get('q6', type=int)
        store_answers(session['user_id'],q1,q2,q3,q4,q5,q6)
        return render_template('/thankyou.html')
    



if __name__ == '__main__':
    app.run(debug=True)
