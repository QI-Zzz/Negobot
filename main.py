from flask import Flask, render_template, request, jsonify, session, redirect
from flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
# from flask_cors import CORS
from Bot import Bot
from os import path
import os
from sqlalchemy import create_engine, func, insert, select, update
from sqlalchemy.orm import Session
from model import Base, Question, Conversation, User
import openai
import spacy
import tenacity
from sqlalchemy.exc import IntegrityError



# Creat a Flask Instance
app = Flask(__name__, template_folder='website/templates', static_folder='website/static')
app.config['SECRET_KEY'] = 'hfjdshfekotonoot'

# CORS(app)

# Create an instance of the Bot class
# message_history = [{"role": "system", "content": '''You are a NegotiationBot, an automated service to sell second-hand stuff and trading on Euro. \

message_history = [{
    "role": "system",
    "content": "You are a NegotiationBot tasked with selling second-hand items in Euros and English without requesting personal information. \
        Your responses should be friendly, persuasive, and concise, typically within 3 sentences. \
        When responding to user offers, you should also end your response with questions to keep the conversation engaging. \
        Products: \
        [Type: Switch OLED, Price: €200, Description: blue and red, bought one year ago, small scratch on screen, everything included], \
        [Type: Nespresso Lattissima One, Price: €350, Description:  white, bought two years ago, perfect condition, with some capsules], \
        [Type: Roland FP-30, Price: €500, Description: white, bought one and half years ago, perfect condition, with headphone and pedal], \
        [Type: Fujifilm X-T5, Price: €800, Description: silver, bought one and half year ago, perfect condition, without lens and memory card]"}]

bot = Bot()
# Creat a database
# engine = create_engine("sqlite:///database.db",echo=True)
DATABASE_URL = "postgresql://postgres:Aptx4869@localhost:5432/botdb"
# DATABASE_URL = os.environ.get("DATABASE_URL")
# if DATABASE_URL.startswith("postgres://"):
#     DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://",1)
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
        dbsession.execute(message_table)
        dbsession.commit()
        return 
    
def store_user(user_id, counter_attempts, product_mentioned,turn, message_history):
    with Session(engine) as dbsession:
        user_table = insert(User).values(user_id=user_id, counter_attempts=counter_attempts,product_mentioned=product_mentioned, turn=turn, message_history = message_history)
        dbsession.execute(user_table)
        dbsession.commit()
        return
    
def store_answers(user_id,Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10,Q11,Q12,Q13,Q14,Q15,Q16,Q17,Q18,Q19,Q20,Q21,Q22, Q23):
    with Session(engine) as dbsession:
        answers_table = insert(Question).values(user_id=user_id,Q1=Q1,Q2=Q2,Q3=Q3,Q4=Q4,Q5=Q5,Q6=Q6,Q7=Q7,Q8=Q8,Q9=Q9,Q10=Q10,Q11=Q11,Q12=Q12,Q13=Q13,Q14=Q14,Q15=Q15,Q16=Q16,Q17=Q17,Q18=Q18,Q19=Q19,Q20=Q20,Q21=Q21,Q22=Q22, Q23=Q23)
        dbsession.execute(answers_table)
        dbsession.commit()
        return 
    
# def select_user_parameters(user_id):
#     with Session(engine) as dbsession:
#         stmt = select(User).where(User.user_id == user_id)
#         result = dbsession.execute(stmt)
#         for user_obj in result.scalars():
#             return user_obj
        
def select_user_parameters(user_id):
    with Session(engine) as dbsession:
        user_obj = dbsession.query(User).filter(User.user_id == user_id).first()
        return user_obj
        
def update_user_parameters(user_id, counter_attempts, product_mentioned, turn, message_history):
    with Session(engine) as dbsession:
        stmt = update(User).where(User.user_id == user_id).values(counter_attempts =counter_attempts, product_mentioned=product_mentioned, turn=turn, message_history=message_history)
        dbsession.execute(stmt)
        dbsession.commit()
        return
    

# Creat a route of home page
@app.route('/')
def index():
    session['user_id'] = get_user_id()
    store_message(session['user_id'], -1, 'user', ":)")
    store_user(session.get('user_id'), 0, None, 0, message_history)
    return render_template('home.html')

# Creat a route of chatbot
@app.route('/chatbot', methods=['GET', 'POST'])
def index_chatbot():
    if request.method == 'GET':
        return render_template("chatbot.html")
    elif request.method == 'POST':
        userInfo = select_user_parameters(session.get('user_id'))
        print(userInfo.counter_attempts)
        print(userInfo.product_mentioned)
        print(userInfo.turn)
        print(message_history)
        bot.update(userInfo.counter_attempts, userInfo.product_mentioned, userInfo.turn, userInfo.message_history)

        # print(bot.counter_attempts)
        # user_input = request.form['user_input']
        # return bot.response(user_input)
        # # return render_template('chatbot.html', msg=msg, bot_response=response)
        # print("1")
        if session.get('order_turn') != None:
            # print("2")
            # print(session.get('order_turn'))
            # print(type(session.get('order_turn')))
            session['order_turn'] += 1
            # print("3")
        else:
            session['order_turn']=0
            # print("4")
        user_input = request.get_json().get("message")

        # message = {"answer": response}

        try:
            store_message(session['user_id'], session['order_turn'], 'user', user_input)
            try:
                if session['user_id'] % 2 == 0:
                    response = bot.response_align(user_input)         
                else: 
                    response = bot.response_unalign(user_input)
            except openai.error.APIError as e:
                response = "Oops! Something went wrong. 😅 Please give it another moment and try typing your message again. Thanks a bunch!"
                pass
            except openai.error.APIConnectionError as e:
                response = "Uh-oh! 🙈 It seems like there might be a mistake with the internet connection. Could you please give it another try? 🔄 Thanks a bunch!"
                pass
            except openai.error.RateLimitError as e:
                response = "Oh no! 😅  Something went a bit sideways. Could you please refresh the page 🔄 and let's start our chat again? Thank you for your patience!"
                pass
            except openai.error.Timeout as e:
                response = "Oops! Something went wrong. 😅 Please give it another moment and try typing your message again. Thanks a bunch!"
                pass
            except openai.error.InvalidRequestError as e:
                response = "Oh no! 😅  Something went a bit sideways. Could you please refresh the page 🔄 and let's start our chat again? Thank you for your patience!"
                pass
            except openai.error.AuthenticationError as e:
                response = "Oh no! 😅  Something went a bit sideways. Could you please refresh the page 🔄 and let's start our chat again? Thank you for your patience!"
                pass
            except openai.error.ServiceUnavailableError as e:
                response = "Oh no! 😅  Something went a bit sideways. Could you please refresh the page 🔄 and let's start our chat again? Thank you for your patience!"
                pass
            except tenacity.RetryError as e:
                response = "Oh no! 😅  Something went a bit sideways. Could you please refresh the page 🔄 and let's start our chat again? Thank you for your patience!"
                pass
            # except Exception as e:
            #     response = "Exception: Oh no! 😅  Something went a bit sideways. Could you please refresh the page 🔄 and let's start our chat again? Thank you for your patience!"
            #     pass
        except IntegrityError as e:
            # with Session(engine) as dbsession:
            #     dbsession.rollback()
            response = "Oops! Something went wrong. 😅 Please go back to home page and restart the test. Thanks a bunch!"
            
            # message = {"answer": response}
        

        message = {"answer": response}
        session['order_turn'] += 1
        # try:
        store_message(session['user_id'], session['order_turn'], 'bot', response)
        # except IntegrityError as e:
            # with Session(engine) as dbsession:
            #     dbsession.rollback()
            # response = "Oh no! 🙀 Something went a bit sideways. Could you please refresh the page 🔄 and let's start our chat again? Thank you for your patience! 🙌IntegrityError"
        # message = {"answer": response}
        update_user_parameters(session.get('user_id'),bot.counter_attempts, bot.product_mentioned, bot.turn, bot.message_history)
        print(bot.counter_attempts)
        print(bot.product_mentioned)
        print(bot.turn)
        print(bot.message_history)
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
        q7 = request.form.get('q7', type=int)
        q8 = request.form.get('q8', type=int)
        q9 = request.form.get('q9', type=int)
        q10 = request.form.get('q10', type=int)
        q11 = request.form.get('q11', type=int)
        q12 = request.form.get('q12', type=int)
        q13 = request.form.get('q13', type=int)
        q14 = request.form.get('q14', type=int)
        q15 = request.form.get('q15', type=int)
        q16 = request.form.get('q16', type=int)
        q17 = request.form.get('q17', type=int)
        q18 = request.form.get('q18', type=int)
        q19 = request.form.get('q19', type=int)
        q20 = request.form.get('q20', type=int)
        q21 = request.form.get('q21', type=int)
        q22 = request.form.get('q22', type=int)
        q23 = request.form.get('q23', type=str)
        store_answers(session['user_id'],q1,q2,q3,q4,q5,q6,q7,q8,q9,q10,q11,q12,q13,q14,q15,q16,q17,q18,q19,q20,q21,q22, q23)
        return render_template('/thankyou.html')
    



if __name__ == '__main__':
    
    app.run(debug=True)
