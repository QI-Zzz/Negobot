
import requests
import json
import openai

openai.api_key = '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'

# def get_intent(text):
#     url = "http://localhost:5005/model/parse"
#     payload = {"text": text}
#     headers = {'content-type': 'application/json'}

#     response = requests.post(url, data=json.dumps(payload), headers=headers)
#     data = response.json()

#     return data['intent']['name']

test_text = ['how are you doing', 
'That is a great offer. I am willing to pay that amount if you can bring it to me.',
'Hey I am instrested in this bunk bed',
'What is the bed made of? And can you possible go lower',
'does that price include delivery and set up?',
'I see, well considering I have to hire someone to help me and rent a truck to transport this item, I think $152 is reasonable ',
'I am coming to get because you said you do not deliver that is why I have to hire help because that is too much for me to do alone',
'no 152',
'Good day to you. I see that you are interested in this wonderful recliner. I believe it comes with an entertainment center so there must be more.',
'I understand sir. Ill tell you what. I can lower the price to 300 and throw in the center for free because I have no idea what Im doing here.',
'Hello, Im interested in your corner desk.  What is it made of?',
'Excellent, and can you tell me what condition its in?',
'Allright, does it have drawers?',
'I will give you $70 for it and come pick it up to get it out of your way!',
'How about $73?',
'Hello! Why are you selling the bike?',
'What are your reasons for selling the bike?',
'good morning']


# for item in test_text:
#     intent = get_intent(item)
#     print(intent)


# def get_intent(text):
#     url = "http://localhost:5005/model/parse"
#     payload = {"text": text}
#     headers = {'content-type': 'application/json'}

#     response = requests.post(url, data=json.dumps(payload), headers=headers)
#     data = response.json()

#     return data['intent']['name']

# intent = get_intent("hello")
# print(intent)
# intent = get_intent("can you lower the price little bit")
# print(intent)


# import pandas as pd

# df = pd.read_csv('C:/Users/ZZ/Desktop/train_data.csv')  # Load your CSV data

# output = ""
# data = {}

# output = ""
# for intent in df['Intent'].unique():
#     output += f"## intent:{intent}\n"
#     for text in df[df['Intent'] == intent]['Text']:
#         output += f"- {text}\n"
#     output += "\n"

# with open('nlu.md', 'w') as f:
#     f.write(output)

def classify_intent(text):

    completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages=[{"role": "system", "content": "The given" f"{text}" "needs to be mapped to precisely one of the intents described below and only give the intent name:\
                        greet: User greets;\
                        inquiry: User asks product information;\
                        counter_price: User offers price for a product\
                        agree:  User agrees and reach to the deal\
                        disagree: User rejects the offer;\
                        goodbye: User says goodbye;"}
                    ],
            temperature=0,
            max_tokens=20,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
    
    )
    user_intent = completion.choices[0].message.content

    return user_intent

for item in test_text:
    intent = classify_intent(item)
    print(intent)