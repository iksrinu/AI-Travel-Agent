import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    print("Connecting to Groq...")
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": "Say 'hello world'",
            }
        ],
        model="meta-llama/llama-4-scout-17b-16e-instruct",
    )
    print("SUCCESS:", chat_completion.choices[0].message.content)
except Exception as e:
    print("FAILED:", e)

    #Plan the first two weeks of a massive one-year backpacking trip across Africa. I am flying out of Hyderabad and want to start by tackling Mt. Kilimanjaro in Tanzania. I strictly want to use local transport and budget accommodations, so no luxury hotels. Please find my flights, places to stay, and build a rugged itinerary.