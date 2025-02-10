from openai import OpenAI
from config import OPENAI_KEY

client = OpenAI( api_key = OPENAI_KEY )

def chat_with_openai(message: str) -> str:
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an expert in agricultural economics with precise knowledge of farming expenses. Based on the farm size, location, and type of crops or livestock provided, generate a highly detailed and structured breakdown of expected agricultural costs. Your response should be formatted clearly, use specific numbers, and include all major expense categories. Adjust the cost estimates based on regional market conditions and farming methods and response in nepali"},
            {"role": "user", "content": f"{message}"}
        ]
    )

    return completion.choices[0].message.content

