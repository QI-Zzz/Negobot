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

class Bot:

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
        self.NER = spacy.load("en_core_web_sm")
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
                                inquiry: User asks specific product information or interested in one product;\
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
        products = ["switch", "coffee Machine", "piano", "camera", "roland", "nintendo", "fujifilm", "nespresso"]

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
        extracted_products = process.extract(joined_text, products, limit=4, scorer=fuzz.partial_ratio)
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

        return "Only provide selling product type and price and ask users which one want to buy."
    

    def greet(self):

        return "Greet the user."

    def thanks(self):
        return "Only thanks to user for reaching the deal"

    def dis_product_list(self):
        self.counter_attempts = 0 
        return "Reject user offer and provide product name and price again."

    def counter_price(self, user_price, product):
  
            self.counter_attempts += 1

            if user_price is None: user_price = 0

            # if len(product) >6:
            #     self.counter_attempts = self.counter_attempts-1
            #     products = [prod.strip() for prod in product.split(',')]
            #     return f"Apology for only selling one product at one time and ask the user reinput"

            if self.counter_attempts == 1:

                if user_price >= self.listed_price[product]:

                    return f"Agree with user's deal"
                
                else:

                    return f"Insisting on the original price of {self.listed_price[product]}."
                
            
            elif self.counter_attempts == 2:

                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.98:

                        return "Agree with user's deal"
                
                    else:
                    
                        if  self.listed_price[product]*0.95 < user_price < self.listed_price[product]*0.98:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.98))

                            return f"Countering with a price of {self.price_offer}."
                        
                        elif user_price <=  self.listed_price[product]*0.95:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.95, self.listed_price[product]*0.98))

                            return f"Countering with a price of {self.price_offer}."
                            

                else: 
                    
                    # if user_price >= self.listed_price[product]*0.98:

                    #     return "Agree with user's deal."
                
                    # else:
                    
                    #     self.price_offer = int(random.uniform(self[product]*0.95, self.listed_price[product]*0.98))

                    #     return f"Countering with a price of {self.price_offer}."
                    return f"Ask the user offer a price."
            
            elif self.counter_attempts == 3:
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.95:

                        return "Agree with user's deal"
                
                    else:
                    
                        if  self.listed_price[product]*0.90 < user_price < self.listed_price[product]*0.95:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.95))

                            return f"Countering with a price of {self.price_offer}."
                        
                        elif user_price <=  self.listed_price[product]*0.90:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.90, self.listed_price[product]*0.95))

                            return f"Countering with a price of {self.price_offer}."
                            

                else: 
                    return f"Ask the user offer a price."
                    
                    # if user_price >= self.listed_price[product]*0.95:

                    #     return "Agree with user's deal."
                
                    # else:
                    
                    #     self.price_offer = int(random.uniform(self[product]*0.90, self.listed_price[product]*0.95))

                    #     return f"Countering with a price of {self.price_offer}."

            elif self.counter_attempts == 4:
                if user_price != 0:

                    if user_price >= self.listed_price[product]*0.90:

                        return "Agree with user's deal"
                
                    else:
                    
                        if  self.listed_price[product]*0.85 < user_price < self.listed_price[product]*0.90:
                        
                            self.price_offer = int(random.uniform(user_price, self.listed_price[product]*0.90))

                            return f"Countering with a price of {self.price_offer}."
                        
                        elif user_price <=  self.listed_price[product]*0.85:
                            
                            self.price_offer = int(random.uniform(self.listed_price[product]*0.85, self.listed_price[product]*0.90))

                            return f"Countering with a price of {self.price_offer}."
                            

                else: 
                    return f"Ask the user offer a price."
                    
                    # if user_price >= self.listed_price[product]*0.90:

                    #     return "Agree with user's deal."
                
                    # else:
                    
                    #     self.price_offer = int(random.uniform(self[product]*0.85, self.listed_price[product]*0.90))

                    #     return f"Countering with a price of {self.price_offer}."

            
            else:

                if user_price >=  self.listed_price[product]*0.85:

                    return "Agree with user's deal"
                
                else:
                    
                    self.counter_attempts = 0
                    return "Reject user offer and provide product name and price again."
                    

            

    def infor(self):
        return "Provide product description that user asked about and ask the user whether like game, coffee, photography, music based on the product"

    def goodbye(self):
        return "Goodbye the user"
        
    def open_conversation(self):
        return "Generate a response based on previous conversation"

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(4))
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
                    self.product_mentioned = product
                    self.counter_attempts = 0
    
        # message_history = [{"role": "system", "content": "Use the alternative words as" f"{user_input}" "in response"}]

        if intent == self.counter_price:

            prompt = intent(user_price, self.product_mentioned)
        
        # elif intent == self.product_list:
            
        #     prompt = intent(product)
        else:
            prompt = intent()

        if twoproduct:
            prompt = "Apology for only selling one product at one time and ask the user reinput"
            # self.user_conversation =[]
            self.counter_attempts = 0

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

        message_history.append({"role": "assistant", "content":  f'''{prompt}'''})


        # conversation.append(user[i])

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages= message_history,
            temperature=1,
            max_tokens=256,
            top_p=0.5,
            frequency_penalty=0,
            presence_penalty=0.5
        )
        reply_content = completion.choices[0].message.content

        message_history.append(
            {"role": "assistant", "content": f'''{reply_content}''' }
        )

        # conversation.append(reply_content)
        return reply_content
 
    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(4))
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
                    self.product_mentioned = product

        if intent == self.counter_price:

            prompt = intent(user_price, self.product_mentioned)
        
        # elif intent == self.dis_product_list:
        
        #     prompt = intent(user_conversation)

        else:
            prompt = intent()

        if twoproduct:
            prompt = "Apology for only selling one product at one time and ask the user reinput"
            self.user_conversation =[]
            self.counter_attempts = 0

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

        message_history.append({"role": "assistant", "content":  f'''{prompt}'''})


        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages= message_history,
            temperature=1,
            max_tokens=256,
            top_p=0.5,
            frequency_penalty=0,
            presence_penalty=0.5
        )
        reply_content = completion.choices[0].message.content

        message_history.append(
            {"role": "assistant", "content": f'''{reply_content}''' }
        )

        # conversation.append(reply_content)
        return reply_content
        # print(completion)

# message_history = [{"role": "system", "content": '''You are a NegotiationBot, an automated service to sell second-hand stuff and trading on Euro. \
#                     You do not ask for user any personal information such as payment and delivery information at any point.\
#                     Your responses should be friendly, persuasive, and always be within 3 sentences.\
#                     Try not to start reponses with "let me know".\
#                     The second-hand products include: \
#                     </product><Type>: Video game console ; <Price>: €200; <Description>: Switch OLED version, blue and red, bought one year ago, small scratch on screen, everying included </product>
#                     </product><Type>: Coffee machine; <Price>: €350; <Description>: Nespresso Lattissima One, white, bought two years ago, perfect condition, with some capcules </product>
#                     </product><Type>: Digital piano; <Price>: €500; <Description>: Roland FP-30, white, bought one and half years ago, perfect condition, with headphone and pedal </product>
#                     </product><Type>: Camera; <Price>: €800; <Description>: Fujifilm X-T5, silver, bought one and half year ago, perfect condition, without lense and memory card </product>
#                     '''}]
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
        

    