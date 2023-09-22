import re
import random
import openai
import os

class Bot:
    
    # OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    openai.api_key = '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'

    def __init__(self):
        
        self.intent_map = {
            "greet" : self.greet,
            "goodbye" : self.goodbye,
            "ask_list" : self.product_list,
            "inquiry" : self.infor,
            "counter_price" : self.counter_price,
            "disagree" : self.dis_product_list,
            "agree" : self.thanks,
        }

        self.listed_price = {"Switch": 200, "Coffee machine": 350, "Camera": 800, "Vacuum": 300, "None": 0}
        self.lowest_price = {product: price*0.95 for product, price in self.listed_price.items()}
        self.price_offer = 0
        self.counter_attempts = 0
        self.user_conversation = []
        # self.listed_price = 200
        # self.lowest_price = 180
        # self.price_offer = 0
        # self.counter_attempts = 0

    def get_intent(self, text):

        user_intent = self.classify_intent(text)
        
        return self.intent_map.get(user_intent,self.out_of_scope)


    # def classify_intent(self, text):
    #     url = "http://localhost:5005/model/parse"
    #     payload = {"text": text}
    #     headers = {'content-type': 'application/json'}

    #     response = requests.post(url, data=json.dumps(payload), headers=headers)
    #     data = response.json()

    #     return data['intent']['name']
    


    def classify_intent(self, text):

        completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=[{"role": "system", "content": "The given text needs to be mapped to precisely one of the intents described below and only give the intent name:\
                            greet: User only greets;\
                            ask_list : User asks for what is selling;\
                            inquiry: User asks specific product information or interested in one product;\
                            counter_price: User offers price for a product;\
                            agree:  User agrees and reaches the deal;\
                            disagree: User rejects the offer;\
                            goodbye: User says goodbye;"},
                            {
                                "role": "user", "content": f"{text}"
                            }
                        ],
                temperature=0,
                max_tokens=20,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
        
        )
        user_intent = completion.choices[0].message.content

        return user_intent
    
    def product_extraction(self, text):

        completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages=[{"role": "system", "content": "You need to only choose which product from the list [Switch, Coffee machine, Camera, Vacuum] is being referred to in the text and only give the name"},
                            {"role": "user", "content": f"{text}"}
                        ],
                temperature=0,
                max_tokens=20,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
        
        )
        product = completion.choices[0].message.content

        return product       


    def price_extraction(self, text):

        numbers = re.findall(r'\d+(?:\.\d+)?', text)

        if not numbers:
            return None

        user_price = min(float(num) for num in numbers)
        return user_price 


    def product_list(self):

        return "Only provide selling product name and price."
    

    def greet(self):

        return "Greet the user."

    def thanks(self):
        return "Only thanks to user for reaching the deal"

    def dis_product_list(self):
        self.counter_attempts = 0
        self.user_conversation = [] 
        return "Reject user offer and provide product list again."

    def counter_price(self, user_price, product):
  
            self.counter_attempts += 1

            if user_price is None: user_price = 0
            if product is None: product = "none"
        # if user_price is None or product is None:
            
        #     if user_price is None: user_price = 0

        #     
        
        # else:

            if self.counter_attempts == 1:

                if user_price >= self.listed_price[product]:

                    return f"Agree with user's deal"
                
                else:

                    return f"Insisting on the listed price of {self.listed_price[product]}."
                
            
            elif self.counter_attempts == 2:

                # if user_price >= self.listed_price*(1-0.08490643508195561):

                #     return "Agreed"
                
                # else:
                    
                #     self.previous_offer = random.randint(user_price, self.previous_offer)

                #     return f"counter_price, price:{self.previous_offer}."
                if user_price != None:

                    if user_price >= self.listed_price[product]*0.98:

                        return "Agree with user's deal"
                
                    else:
                    
                        # self.price_offer = int(random.uniform(self.lowest_price, user_price))

                        # return f"counter_price, price:{self.price_offer}. {user_price}"

                        if  self.lowest_price[product] < user_price < self.listed_price[product]*0.98:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.98))

                            return f"Countering with a price of {self.price_offer}."
                        
                        elif user_price <=  self.lowest_price[product]:
                            
                            self.price_offer = int(random.uniform(self.lowest_price[product], self.listed_price[product]*0.98))

                            return f"Countering with a price of {self.price_offer}."
                            

                else: 
                    
                    if user_price >= self.listed_price[product]*0.98:

                        return "Agree with user's deal."
                
                    else:
                    
                        self.price_offer = int(random.uniform(self.listed_price[product]*0.98, self.listed_price[product]))

                        return f"Countering with a price of {self.price_offer}."

            
            else:

                if user_price >=  self.lowest_price[product]:

                    return "Agree with user's deal"
                
                else:
                    self.user_conversation =[]
                    self.counter_attempts = 0
                    return "Reject user offer and provide product list again."
                    

            

    def infor(self):
        return "Provide product description that user asked about."

    def goodbye(self):
        return "Goodbye the user"
        
    def out_of_scope(self):
        return "Generate a response as the input of user is out of scope, apology and ask user reinput."


    def response(self, user_input, message_history):

        intent = self.get_intent(user_input)

        user_price = self.price_extraction(user_input)

        user_conversation = self.user_conversation

        product = self.product_extraction(user_conversation)

        # message_history = [{"role": "system", "content": "Use the alternative words as" f"{user_input}" "in response"}]

        if intent == self.counter_price:

            prompt = intent(user_price, product)
        
        # elif intent == self.product_list:
            
        #     prompt = intent(product)
        else:
            prompt = intent()



        message_history.append(
        {
                "role": "user", "content": "Your primary objective is to closely mimic user's choice of words in your responses.\
                    Specifically, mirror their prepositions, nouns, tenses, modals, verbs, product names, and hedges.\
                    For instance, if user uses verb buy, you should use verb buy too; if user use noun switch, you should use noun switch too.\
                    Do you understand?"

            }
        )

        message_history.append(
            {
                "role": "assistant", "content": "Yes, I understand and I will try to use the same words as user's."
            }
        )
        message_history.append(
            {"role": "user", "content": f'''{user_input}'''}
        )

        message_history.append({"role": "assistant", "content": '''You respond in a short, within three sentences based on instruction: ''' f'''{prompt}'''})


        # conversation.append(user[i])

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages= message_history,
            temperature=1.25,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        reply_content = completion.choices[0].message.content

        message_history.append(
            {"role": "assistant", "content": f'''{reply_content}''' }
        )

        # conversation.append(reply_content)
        return reply_content
 
    
    # def response(self, user_input, message_history):

        intent = self.get_intent(user_input)

        user_price = self.price_extraction(user_input)

        user_conversation = self.user_conversation

        product = self.product_extraction(user_conversation)

        # message_history = [{"role": "system", "content": "Use the alternative words as" f"{user_input}" "in response"}]

        if intent == self.counter_price:

            prompt = intent(user_price, product)
        
        # elif intent == self.dis_product_list:
        
        #     prompt = intent(user_conversation)

        else:
            prompt = intent()

        message_history.append(
        {
                "role": "user", "content": "Your primary objective is to use different words from users in your responses.\
                    Specifically, substitute their prepositions, nouns, tenses, modals, verbs, product names, and hedges.\
                    For instance, if user uses buy, you should use purchase; if user use switch, you should use nintendo.\
                    Do you understand?"
            }
        )

        message_history.append(
            {
                "role": "assistant", "content": "Yes, I understand and I will use different words from user's and would not ask for user delivery and payment information. "
            }
        )

        message_history.append(
            {"role": "user", "content": f'''{user_input}'''}
        )

        message_history.append({"role": "assistant", "content": '''You respond in a short, within three sentences based on instruction:  ''' f'''{prompt}'''})


        # conversation.append(user[i])

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages= message_history,
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        reply_content = completion.choices[0].message.content

        message_history.append(
            {"role": "assistant", "content": f'''{reply_content}''' }
        )

        # conversation.append(reply_content)
        return reply_content
        # print(completion)

# message_history = [{"role": "system", "content": '''You are a NegotiationBot, an automated service to sell second-hand stuff and trading on Euro. \
#                     You do not ask for user payment and delivery information.\
#                     The product includes:
#                     Product name: Switch; Product model: OLED version; Product price: €200; Product description: blue and red, bought one year ago, small scratch on screen;
#                     Product name: Coffee machine: Product model: Nespresso Lattissima One; Product price: €350; Product description: white, bought two years ago, perfect condition;
#                     Product name: Vacuum cleaner: Product model: Philips Series 8000 XC8043/01; Product price: €300; Product description: black, bought one and half years ago, perfect condition;
#                     Product name: Camera: Product model: Fujifilm X-T5 Body; Product price: €800; Product description: silver, bought one and half year ago, perfect condition;'''}]

# bot = Bot()


# while True:

    
#     user_input = input("User:") 
#     bot.user_conversation.append(user_input)
#     # product = product_extraction(user_conversation)
#     # conversation.append(user_input)
    
#     if user_input.lower() == "exit":
#         break

#     else:
#         # conversation.append(bot.response(user_input))
#         print("Bot: ", bot.response(user_input, message_history))
#         # print(message_history)
#         # print(bot.user_conversation)

    