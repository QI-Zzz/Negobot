import re

def price_extraction(sentence):
    # Find all numbers in the sentence
    numbers = re.findall(r'\d+(?:\.\d+)?', sentence)

    # If no numbers were found, return None
    if not numbers:
        return None

    # Convert the numbers to floats and find the smallest one
    smallest_number = min(float(num) for num in numbers)
    return smallest_number

sentence = "I really like this bike, but there is not enough information in the description for me to pay $160. I have $100 in cash right now and can meet you at your house. "
print(price_extraction(sentence))  # Outputs: 0.5

