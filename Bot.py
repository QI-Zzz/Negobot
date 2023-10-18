import re
import random
import openai
import os
from thefuzz import process
from thefuzz import fuzz
import spacy
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)
NER = spacy.load("en_core_web_sm")
class Bot():

    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    # openai.api_key = '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'

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
        self.counter_attempts = 0
        self.user_conversation = []
        self.product_mentioned = ""
        self.turn = 0
        self.NER = NER
        # self.products_mentioned =str
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
    

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def classify_intent(self, text):
        # try:
            completion = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo", 
                    messages=[{"role": "system", "content": "The given text needs to be mapped to precisely one of the intents described below and only give the intent name:\
                                greet: User only greets;\
                                ask_list : User asks for what is selling;\
                                inquiry: User asks specific product information;\
                                counter_price: User offers price for a product;\
                                agree:  User agrees and reaches the deal;\
                                disagree: User rejects the offer;\
                                goodbye: User says goodbye;\
                                open_conversation: chitchat;"},
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
        # except Exception as e:
        #     return "error"
    
    # @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    # def product_extraction(self, text):

    #     completion = openai.ChatCompletion.create(
    #             model="gpt-3.5-turbo", 
    #             messages=[{"role": "system", "content": "Your task is only to choose product from this product list: [Switch, Coffee, Camera, Piano]. If no product mentioned, return [None]. And the returned format like[Switch]"},
    #                     #   {"role": "system", "content": "You need to only choose product name from the list [Switch, Coffee, Camera, Piano] is being referred to in the text and return in List"}
    #                         {"role": "user", "content": f"{text}"}
    #                     ],
    #             temperature=0,
    #             max_tokens=20,
    #             top_p=1,
    #             frequency_penalty=0,
    #             presence_penalty=0
        
    #     )

    #     product = completion.choices[0].message.content.strip()

    #     return product
    
    def product_extraction(self, text):
        products = ["switch", "coffee machine", "piano", "camera", "roland", "nintendo", "fujifilm", "nespresso"]

        product_mapping = {
            "roland": "piano",
            "nintendo": "switch",
            "fujifilm":"camera",
            "nespresso":"coffee",
            "coffee Machine":"coffee"
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

        if not numbers:
            return None

        user_price = min(float(num) for num in numbers)
        return user_price 


    def product_list(self):

        return "List only the product type and price, then inquire which one the user wishes to purchase."
    

    def greet(self):

        return "Extend a warm welcome to the user."

    def thanks(self):
        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."

    def dis_product_list(self):
        self.counter_attempts = 0 
        return f"Politely decline the user's offer and suggest alternative products along with their prices."

    def counter_price(self, user_price, product):
            # print("User price: " + f"{user_price}" + "product: " + product)
            # print( "Listed Price" + self.listed_price[product])
            self.counter_attempts += 1

            if user_price is None: user_price = 0

            # if len(product) >6:
            #     self.counter_attempts = self.counter_attempts-1
            #     products = [prod.strip() for prod in product.split(',')]
            #     return f"Apology for only selling one product at one time and ask the user reinput"

            if self.counter_attempts == 1:
                if user_price !=0:
                    if user_price >= self.listed_price[product]:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                    
                    else:

                        # return f"Insisting on the original price of {self.listed_price[product]}."
                        if  self.listed_price[product]*0.98 < user_price < self.listed_price[product]:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]))

                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."
                            # return f"Countering with a price of {self.price_offer}."                            
                        
                        elif user_price <=  self.listed_price[product]*0.98:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.98, self.listed_price[product]))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                      
                else:
                    return f"Prompt the user to suggest a price when they haven't provided one."    
                
            
            if self.counter_attempts == 2:
                
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.98:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                    else:
                    
                        if  self.listed_price[product]*0.95 < user_price < self.listed_price[product]*0.98:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.98))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                      
                        elif user_price <=  self.listed_price[product]*0.95:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.95, self.listed_price[product]*0.98))
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."
                            # return f"Countering with a price of {self.price_offer}."
                            

                else: 
                    
                    # if user_price >= self.listed_price[product]*0.98:

                    #     return "Agree with user's deal."
                
                    # else:
                    
                    #     self.price_offer = int(random.uniform(self[product]*0.95, self.listed_price[product]*0.98))

                    #     return f"Countering with a price of {self.price_offer}."
                    return f"Prompt the user to suggest a price when they haven't provided one."
            
            elif self.counter_attempts == 3:
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.95:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                    else:
                    
                        if  self.listed_price[product]*0.90 < user_price < self.listed_price[product]*0.95:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.95))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                     
                        elif user_price <=  self.listed_price[product]*0.90:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.90, self.listed_price[product]*0.95))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                           

                else: 
                    return f"Prompt the user to suggest a price when they haven't provided one."
                    
                    # if user_price >= self.listed_price[product]*0.95:

                    #     return "Agree with user's deal."
                
                    # else:
                    
                    #     self.price_offer = int(random.uniform(self[product]*0.90, self.listed_price[product]*0.95))

                    #     return f"Countering with a price of {self.price_offer}."

            elif self.counter_attempts == 4:
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.90:

                        return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                    else:
                    
                        if  self.listed_price[product]*0.85 < user_price < self.listed_price[product]*0.90:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.90))

                            # return f"Countering with a price of {self.price_offer}."
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."                    
                        elif user_price <=  self.listed_price[product]*0.85:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.85, self.listed_price[product]*0.90))
                            return f"Politely decline the user's proposal, ignored the system's listed price, and present a counteroffer at {self.price_offer}."
                            # return f"Countering with a price of {self.price_offer}."
                            

                else: 
                    return f"Prompt the user to suggest a price when they haven't provided one."
                    
                    # if user_price >= self.listed_price[product]*0.90:

                    #     return "Agree with user's deal."
                
                    # else:
                    
                    #     self.price_offer = int(random.uniform(self[product]*0.85, self.listed_price[product]*0.90))

                    #     return f"Countering with a price of {self.price_offer}."

            
            else:

                if user_price >=  self.listed_price[product]*0.85:

                    return f"Express gratitude to the user for finalizing the agreement and hope they have an excellent day."
                
                else:
                    
                    self.counter_attempts = 0
                    return f"Politely decline the user's offer and suggest alternative products along with their prices."
                    

            

    def infor(self):
        return f"When the user asks about a specific product, respond with a product description and then ask a relevant question based on their choice. For example, if they ask about the Switch, provide the description and then ask if they like games. If they ask about the coffee machine, provide the description and then ask if they enjoy coffee. if they ask about the camera, provide the description and then ask if they like photography. If they ask about the piano, provide the description and then ask if they enjoy playing piano.Keep the responses concise."

    def goodbye(self):
        return f"Bid farewell to the user and wish them a wonderful day."
        
    def open_conversation(self):
        return f"Craft a reply referencing the prior conversation and guide the conversation to sell product."

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def response_align(self, user_input, message_history):

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
          
                if product != "None":
                    if product != self.product_mentioned:
                        self.product_mentioned = product
                        self.counter_attempts =0
                        
    
        # message_history = [{"role": "system", "content": "Use the alternative words as" f"{user_input}" "in response"}]
        
        if intent == self.counter_price:
        

            if self.product_mentioned != '':

                prompt = intent(user_price, self.product_mentioned)

            else:
                prompt = f"Apologize for the oversight regarding the product in question and kindly request the user to specify it again."
        
        # elif intent == self.product_list:
            
        #     prompt = intent(product)
 

        else:
            prompt = intent()

        if twoproduct:
            prompt = f"Express regret for the limitation of selling only one item at a time and kindly ask the user to select a single product."
            # self.user_conversation =[]
            self.counter_attempts = 0

        message_history.append(
        {
                "role": "user", "content": "Your primary objective is to closely mimic user's choice of words in your responses.\
                    Specifically, mirror their prepositions, nouns, tenses, modals, verbs, product names, and hedges.\
                    For instance, if user uses verb buy, you should use verb buy too; if user use noun switch, you should use noun switch too.\
                    Also in any point, dont ask user personal information.\
                    Do you understand?"

            }
        )

        message_history.append(
            {
                "role": "assistant", "content": "Yes, I understand and I will try to use the same words as user's and would not ask for user any personal information."
            }
        )
        message_history.append(
            {"role": "user", "content": f'''{user_input}'''}
        )

        message_history.append({"role": "assistant", "content":  f'''{prompt}'''})


        # conversation.append(user[i])

        if intent == self.open_conversation:
            completion = openai.ChatCompletion.create(
                model="gpt-4", 
                messages= message_history,
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
                messages= message_history,
                temperature=1,
                max_tokens=256,
                top_p=0.5,
                frequency_penalty=1,
                presence_penalty=0.5
            )
            reply_content = completion.choices[0].message.content

        index_to_del = [1,2,4]
        for index in sorted(index_to_del, reverse=True):
            del message_history[index+2*self.turn]
        self.turn += 1

        message_history.append(
            {"role": "assistant", "content": f'''{reply_content}''' }
        )

        # conversation.append(reply_content)
        return reply_content
 
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def response_unalign(self, user_input, message_history):

        intent = self.get_intent(user_input)

        user_price = self.price_extraction(user_input)

        twoproduct = False


        # message_history = [{"role": "system", "content": "Use the alternative words as" f"{user_input}" "in response"}]
        
        product_utterance = self.product_extraction(user_input)
        
        if product_utterance:

            if len(product_utterance) > 1:
                # prompt = "Apology for only selling one product at one time and ask the user reinput"
                twoproduct = True
                # return prompt
            
            else :
                # self.products_mentioned.append(product_utterance)
                product = product_utterance[0]
                
                if product != "None":
                    if product != self.product_mentioned:
                        self.product_mentioned = product
                        self.counter_attempts =0
        
        
        # if intent == self.counter_price:
        #     print(self.product_mentioned)
        #     prompt = intent(user_price, self.product_mentioned)
        if intent == self.counter_price:

            if self.product_mentioned != '':

                prompt = intent(user_price, self.product_mentioned)

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
            self.user_conversation =[]
            self.counter_attempts = 0

        message_history.append(
        {
                "role": "user", "content": "Your primary objective is to use different words from users in your responses.\
                    Specifically, substitute their prepositions, nouns, tenses, modals, verbs, product names, and hedges.\
                    For instance, if user uses buy, you should use purchase; if user use switch, you should use nintendo.\
                    Also in any point, dont ask user personal information.\
                    Do you understand?"
            }
        )

        message_history.append(
            {
                "role": "assistant", "content": "Yes, I understand and I will use different words from user's and would not ask for user any personal information. "
            }
        )

        message_history.append(
            {"role": "user", "content": f'''{user_input}'''}
        )

        message_history.append({"role": "assistant", "content":  f'''{prompt}'''})

        if intent == self.open_conversation:
            completion = openai.ChatCompletion.create(
                model="gpt-4", 
                messages= message_history,
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
                messages= message_history,
                temperature=1,
                max_tokens=256,
                top_p=0.5,
                frequency_penalty=1,
                presence_penalty=0.5
            )
            reply_content = completion.choices[0].message.content

        index_to_del = [1,2,4]
        for index in sorted(index_to_del, reverse=True):
            del message_history[index+2*self.turn]
        self.turn += 1

        message_history.append(
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
        

    