import re
import random
import openai
import os
from thefuzz import process
from thefuzz import fuzz
import spacy
from tenacity import *

NER = spacy.load("en_core_web_sm")
class Bot():

    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

    def __init__(self):
        
        self.intent_map = {
            "greet" : self.greet,
            "goodbye" : self.goodbye,
            "ask_list" : self.product_list,
            "inquiry" : self.infor,
            "counter_price" : self.counter_price,
            "disagree" : self.dis_product_list,
            "agree" : self.thanks,
            "open_conversation" : self.open_conversation,
            # "error" : self.error
        }

        self.listed_price = {"switch": 200, "coffee": 350, "camera": 800, "piano": 500} 
        # self.lowest_price = {product: price*0.85 for product, price in self.listed_price.items()}
        self.price_offer = 0
        # self.counter_attempts = 0
        # self.product_mentioned = ''
        # self.turn = 0
        self.NER = NER
    
    def update(self, counter_attempts, product_mentioned, turn, message_history):
        self.counter_attempts = counter_attempts
        self.product_mentioned = product_mentioned
        self.turn = turn
        self.message_history = message_history


    def get_intent(self, text):

        user_intent = self.classify_intent(text)
        
        return self.intent_map.get(user_intent,self.error)
    
    def error(self):
        return "There is an error, please reinput."


    # def classify_intent(self, text):
    #     url = "http://localhost:5005/model/parse"
    #     payload = {"text": text}
    #     headers = {'content-type': 'application/json'}

    #     response = requests.post(url, data=json.dumps(payload), headers=headers)
    #     data = response.json()

    #     return data['intent']['name']
    

    @retry(wait=wait_random(min=1, max=3), stop=stop_after_delay(6))
    def classify_intent(self, text):
        # try:
            completion = openai.ChatCompletion.create(
                    model="gpt-4", 
                    messages=[{"role": "system", "content": "The given text needs to be mapped to precisely one of the intents described below and only give the intent name:\
                                greet: User only greets;\
                                ask_list : User asks for what is selling;\
                                inquiry:  User asks for specific product information about camera, switch, piano, coffee machine;\
                                counter_price: User offers price for a product;\
                                agree: User agrees to buy the products;\
                                disagree: User rejects the offer;\
                                goodbye: User says goodbye;\
                                open_conversation: User is talking about what they like, their hobby, personal lifestyle, and personal experience.;"},
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
        products = ["switch", "coffee machine", "piano", "camera", "roland", "nintendo", "fujifilm", "nespresso", 'game console']

        product_mapping = {
            "roland": "piano",
            "nintendo": "switch",
            "fujifilm":"camera",
            "nespresso":"coffee",
            "coffee machine":"coffee",
            "game console": "switch",
        }
        # NER = spacy.load("en_core_web_sm")
        
        processed_text = self.NER(text)
        noun_phrases = [chunk.text for chunk in processed_text.noun_chunks]
        joined_text = " ".join(noun_phrases)

        if len(text)>14:
            extracted_products = process.extract(joined_text, products, limit=4, scorer=fuzz.partial_ratio)
            mapped_products = []
        else:
            extracted_products = process.extract(text, products, limit=4, scorer=fuzz.partial_ratio)
            mapped_products = []
        # for product, score in extracted_products:
        for index in extracted_products:
            # if score > 60:  # Adjust the threshold as per your requirement
            #     return mapped_products.append(product_mapping.get(product, product))
            # else:
            #     mapped_products.append('None')
            if index[1] > 80:  # Adjust the threshold as per your requirement
                mapped_products.append(product_mapping.get(index[0], index[0]))
            else:
                return mapped_products
        # return score
        # print( extracted_product, score)
        # print(mapped_products)

    def price_extraction(self, text):

        numbers = re.findall(r'\d+(?:\.\d+)?', text)

        valid_numbers = [float(num) for num in numbers if float(num) > 20]

        if not valid_numbers:
            return None

        user_price = min(valid_numbers)
        return user_price 



    def product_list(self):

        return "List only the product Type and Price, then inquire which one the user wishes to purchase."
    

    def greet(self):

        return "Extend a warm welcome to the user."

    def thanks(self):
        return f"Express gratitude to the user for finalizing the agreement without mentioning the price and hope they have an excellent day."

    def dis_product_list(self):
        self.counter_attempts = 0 
        return f"Politely decline the user's offer and suggest alternative products along with their prices."

    def counter_price(self, user_price, product, is_retry):
            
            if not is_retry:
                self.counter_attempts += 1

            if user_price is None: 
                user_price = 0

            if self.counter_attempts == 1:
                if user_price !=0:
                    if user_price >= self.listed_price[product]:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                    
                    else:

                        # return f"Insisting on the original price of {self.listed_price[product]}."
                        if  self.listed_price[product]*0.95 < user_price < self.listed_price[product]:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]))

                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."
                            # return f"Countering with a price of {self.price_offer}."                            
                        
                        elif user_price <=  self.listed_price[product]*0.95:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.95, self.listed_price[product]))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                      
                else:
                    return f"Prompt the user to suggest a price when they haven't provided one."    
                
            
            elif self.counter_attempts == 2:
                
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.95:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                    else:
                    
                        if  self.listed_price[product]*0.88 < user_price < self.listed_price[product]*0.95:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.95))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                      
                        elif user_price <=  self.listed_price[product]*0.88:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.88, self.listed_price[product]*0.95))
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."
                            # return f"Countering with a price of {self.price_offer}."
                            

                else: 

                    return f"Prompt the user to suggest a price when they haven't provided one."
            
            elif self.counter_attempts == 3:
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.88:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                    else:
                    
                        if  self.listed_price[product]*0.80 < user_price < self.listed_price[product]*0.88:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.88))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                     
                        elif user_price <=  self.listed_price[product]*0.80:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.80, self.listed_price[product]*0.88))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                           

                else: 
                    return f"Prompt the user to suggest a price when they haven't provided one."
                    

            elif self.counter_attempts == 4:
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.80:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                    else:
                    
                        if  self.listed_price[product]*0.75 < user_price < self.listed_price[product]*0.80:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.80))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                    
                        elif user_price <=  self.listed_price[product]*0.75:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.75, self.listed_price[product]*0.80))
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."
                            # return f"Countering with a price of {self.price_offer}."
                            

                else: 
                    return f"Prompt the user to suggest a price when they haven't provided one."
                    

            
            else:

                if user_price >=  self.listed_price[product]*0.75:

                    return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                else:
                    
                    self.counter_attempts = 0
                    return f"Politely decline the user's offer and suggest alternative products along with their prices."
                    

            

    def infor(self):
        return f"When the user asks about a specific product, respond with a product description and then ask a relevant '''wh''' word-based question about their choice. For example:\
                If they ask about the Switch, provide the description and then ask, 'What kind of games do you prefer?'\
                If they ask about the coffee machine, provide the description and then ask, 'What type of coffee do you like?'\
                If they ask about the camera, provide the description and then ask, 'What subjects do you enjoy photographing?'\
                If they ask about the piano, provide the description and then ask, 'When did you start playing the piano?"

    def goodbye(self):
        return f"Bid farewell to the user and wish them a wonderful day."
        
    def open_conversation(self):
        return f"Craft a reply referencing the prior conversation and prompt the user to suggest a price."
    
    def before_retry(retry_state):
        retry_state.args = (True, ) + retry_state.args[1:]   

    @retry(wait=wait_random(min=1, max=10), stop=stop_after_delay(22), before=before_retry)
    def response_align(self, user_input, is_retry=False):

        intent = self.get_intent(user_input)

        user_price = self.price_extraction(user_input)
        twoproduct = False

        # user_conversation = self.user_conversation

        # products = self.product_extraction(user_conversation)
        
        # if len(products) >6:
        #     self.counter_attempts = self.counter_attempts-1
        #     products = [prod.strip() for prod in products.split(',')]
        #     product = products[-1]
        #     return f"Apology for only selling one product at one time and ask the user reinput"

        product_utterance = self.product_extraction(user_input)
       
        if product_utterance:

            if len(product_utterance) > 1:
                # prompt = "Apology for only selling one product at one time and ask the user reinput"
                twoproduct = True
                # return prompt
            
            else :
                # self.products_mentioned.append(product_utterance)
                product = product_utterance[0]
          
                if product != self.product_mentioned:

                    self.product_mentioned = product
                    self.counter_attempts =0
                        
    
        # message_history = [{"role": "system", "content": "Use the alternative words as" f"{user_input}" "in response"}]
        
        if intent == self.counter_price:
        

            if self.product_mentioned != '':

                prompt = intent(user_price, self.product_mentioned, is_retry)

            else:
                prompt = f"Apologize for the oversight regarding the product in question and kindly request the user to specify it again."
        
        # elif intent == self.product_list:
            
        #     prompt = intent(product)
 

        else:
            prompt = intent()

        if twoproduct:
            prompt = f"Express regret for the limitation of selling only one item at a time and kindly ask the user to select a single product."
            self.counter_attempts = 0

        self.message_history.append(
        {
                "role": "user", "content": "Your primary objective is to try to use same word in" f'''{user_input}''' "in your reponses.\
                    For instance, if user uses verb hey, you should use verb hey too; if user use noun switch, you should use noun switch too.\
                    Also in any point, dont ask user personal information.\
                    Do you understand?"

            }
        )

    
        self.message_history.append(
            {
                "role": "assistant", "content": "Yes, I understand and I will try to use the same words as in" f'''{user_input}''' "and would not ask for user any personal information."
            }
        )
        self.message_history.append(
            {"role": "user", "content": f'''{user_input}'''}
        )

        self.message_history.append({"role": "assistant", "content":  f'''{prompt}'''})


        # conversation.append(user[i])

        if intent == self.open_conversation:
            completion = openai.ChatCompletion.create(
                model="gpt-4", 
                messages= self.message_history,
                temperature=1,
                max_tokens=256,
                top_p=0.5,
                frequency_penalty=1,
                presence_penalty=0.5
            )
            reply_content = completion.choices[0].message.content

        else:

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages= self.message_history,
                temperature=1,
                max_tokens=256,
                top_p=0.5,
                frequency_penalty=1,
                presence_penalty=0.5
            )
            reply_content = completion.choices[0].message.content

        index_to_del = [1,2,4]
        for index in sorted(index_to_del, reverse=True):
            del self.message_history[index+2*self.turn]
        self.turn += 1

        self.message_history.append(
            {"role": "assistant", "content": f'''{reply_content}''' }
        )

        # conversation.append(reply_content)
        return reply_content
 
    @retry(wait=wait_random(min=1, max=10), stop=stop_after_delay(22), before=before_retry)
    def response_unalign(self, user_input, is_retry =False):

        intent = self.get_intent(user_input)

        user_price = self.price_extraction(user_input)

        twoproduct = False
        
        product_utterance = self.product_extraction(user_input)
        
        if product_utterance:

            if len(product_utterance) > 1:
                # prompt = "Apology for only selling one product at one time and ask the user reinput"
                twoproduct = True
                # return prompt
            
            else :
                # self.products_mentioned.append(product_utterance)
                product = product_utterance[0]
                
                if product != self.product_mentioned:
                    self.product_mentioned = product
                    self.counter_attempts =0
        
        
        # if intent == self.counter_price:
        #     print(self.product_mentioned)
        #     prompt = intent(user_price, self.product_mentioned)
        if intent == self.counter_price:

            if self.product_mentioned != '':

                prompt = intent(user_price, self.product_mentioned, is_retry)

            else:
                prompt = f"Apologize for the oversight regarding the product in question and kindly request the user to specify it again."
        # elif intent == self.dis_product_list:
        
        #     prompt = intent(user_conversation)
        # elif intent == self.infor:
            
        #     prompt = intent(self.product_mentioned)

        else:
            prompt = intent()

        if twoproduct:
            prompt = f"Express regret for the limitation of selling only one item at a time and kindly ask the user to select a single product."
            
            self.counter_attempts = 0

        self.message_history.append(
        {
                "role": "user", "content": "Your primary objective is to use different words from users in your responses.\
                    Specifically, substitute their prepositions, nouns, tenses, modals, verbs, product names, and hedges.\
                    For instance, if user uses buy, you should use purchase; if user use switch, you should use nintendo.\
                    Also in any point, dont ask user personal information.\
                    Do you understand?"
            }
        )

        self.message_history.append(
            {
                "role": "assistant", "content": "Yes, I understand and I will use different words from f'''{user_input}'''and would not ask for user any personal information. "
            }
        )

        self.message_history.append(
            {"role": "user", "content": f'''{user_input}'''}
        )

        self.message_history.append({"role": "assistant", "content":  f'''{prompt}'''})

        if intent == self.open_conversation:
            completion = openai.ChatCompletion.create(
                model="gpt-4", 
                messages= self.message_history,
                temperature=1,
                max_tokens=256,
                top_p=0.5,
                frequency_penalty=1,
                presence_penalty=0.5
            )
            reply_content = completion.choices[0].message.content

        else:

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages= self.message_history,
                temperature=1,
                max_tokens=256,
                top_p=0.5,
                frequency_penalty=1,
                presence_penalty=0.5
            )
            reply_content = completion.choices[0].message.content

        index_to_del = [1,2,4]
        for index in sorted(index_to_del, reverse=True):
            del self.message_history[index+2*self.turn]
        self.turn += 1

        self.message_history.append(
            {"role": "assistant", "content": f'''{reply_content}''' }
        )

        # conversation.append(reply_content)
        return reply_content
        # print(completion)

# message_history = [{
#     "role": "system",
#     "content": "You are a NegotiationBot tasked with selling second-hand items in Euros and English without requesting personal information. \
#         Your responses should be friendly, persuasive, and concise, typically within 3 sentences. \
#         When responding to user offers, you should also end your response with questions to keep the conversation engaging. \
#         Products: \
#         [Type: Switch OLED, Price: €200, Description: blue and red, bought one year ago, small scratch on screen, everything included], \
#         [Type: Nespresso Lattissima One, Price: €350, Description:  white, bought two years ago, perfect condition, with some capsules], \
#         [Type: Roland FP-30, Price: €500, Description: white, bought one and half years ago, perfect condition, with headphone and pedal], \
#         [Type: Fujifilm X-T5, Price: €800, Description: silver, bought one and half year ago, perfect condition, without lens and memory card]"}]
# # NER = spacy.load("en_core_web_sm")
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
#         print("Bot: ", bot.response_align(user_input, message_history))
#         # print(message_history)
#         # print(bot.user_conversation)
        

    