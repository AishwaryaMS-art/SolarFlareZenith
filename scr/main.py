import google.generativeai as genai
from google.colab import userdata

# Configure the API key using a Secret
GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')  # Ensure your key is safe
genai.configure(api_key=GOOGLE_API_KEY)

# Load the Gemini model
model = genai.GenerativeModel("gemini-2.0-flash")

# Start a chat session to maintain conversational history
chat = model.start_chat(history=[])

def solarflare_brain(user_input):
    # Use the globally defined chat object to send messages
    response = chat.send_message(
        user_input, # Corrected: 'contents=' is not a valid keyword here
        generation_config={
            "temperature": 0.9, # Increase temperature for more varied outputs
        }
    )
    return response.text


# ----------- SAFE INFINITE LOOP -------------
print("SolarFlare AI in Google Colab")
print("Type 'exit' to stop.\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("SolarFlare: Chat ended.")
        break

    answer = solarflare_brain(user_input)
    print("SolarFlare:", answer)
    print()  # spacing

