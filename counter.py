import random

# class Bot:
    
#     def __init__(self):
        
#         self.intent_map = {

#             "Offer_price" : self.counter_price,

#             "Vague-price" : self.counter_price
#         }
        


def counter_price(counter_attempts, intent, user_price):
    
    listed_price = 250
    lowest_price = listed_price*0.95

    price_offer= 0
    # counter_attempts = 0
    # counter_attempts += 1

    if counter_attempts == 1:

        if intent in ["Offer_price", "Vagur-price"] and user_price >= listed_price:

            return f"agree; user price:{user_price}, listed_price{listed_price}"
        
        else:

            return f"insist listed price, user price:{user_price}.listed price:{listed_price},"
    
    elif counter_attempts == 2:

        if user_price != None:

            if intent in ["Offer_price", "Vagur-price"] and user_price >= listed_price*0.98:

                return f"Agreed user price:{user_price}"
        
            else:
            
                price_offer = int(random.uniform(lowest_price, user_price))

                return f"counter_price.user price:{user_price}, offer price{price_offer}"
        else: 
            
            if intent in ["Offer_price", "Vagur-price"] and user_price >= listed_price*0.98:

                return f"Agreed user price:{user_price}"
        
            else:
            
                price_offer = int(random.uniform(listed_price*0.98, listed_price))

                return f"counter_price.user price:{user_price}, offer price{price_offer}"

    
    else:

        if user_price >= lowest_price:

            return f"Agreed user price:{user_price}"
        
        else:
        
            return f"reject user price:{user_price}"
        
print(counter_price(1, "Offer_price", 245))
print(counter_price(2, "Offer_price", 245))
print(counter_price(3, "Offer_price", 245))
print(counter_price(1, "Offer_price", 235))
print(counter_price(2, "Offer_price", 240))
print(counter_price(3, "Offer_price", 235))

# print(counter_attempts)