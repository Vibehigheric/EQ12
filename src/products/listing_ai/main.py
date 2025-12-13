import os
# import openai

class MockOpenAI:
    class ChatCompletion:
        @staticmethod
        def create(model, messages):
            return {"choices": [{"message": {"content": "Stunning 3-bedroom home with modern amenities..."}}]}

openai = MockOpenAI()

def generate_listing(details):
    prompt = f"Write a real estate listing for: {details}"
    desc = openai.ChatCompletion.create(
        model="gpt-4o", 
        messages=[{"role": "user", "content": prompt}]
    )
    return desc['choices'][0]['message']['content']

if __name__ == "__main__":
    details = "3 bed, 2 bath, downtown, renovated kitchen"
    print(generate_listing(details))
