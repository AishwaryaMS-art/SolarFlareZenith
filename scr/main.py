import google.generativeai as genai
from google.colab import userdata

# Configure the API key using a Colab Secret
GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')  # Ensure your key is saved in Colab secrets
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


# ----------- SAFE INFINITE LOOP FOR COLAB -------------
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
    personalities = {
    "funny": "Speak in a humorous, playful, witty tone. Never repeat jokes.",
    "creative": "Respond with imaginative, artistic, and original ideas.",
    "friendly": "Be warm, positive and supportive.",
    "sarcastic": "Be sarcastic but not rude. Use clever remarks.",
    "professional": "Be formal, clear, and concise."
}

current_personality = "friendly"

# 3️⃣ Joke bank for predictable + improv rotation
jokes = [
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "Why don’t scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break, and it said 'No problem, I’ll go to sleep!'",
    "Why did the scarecrow win an award? Because he was outstanding in his field!",
    "Why don’t skeletons fight each other? They don’t have the guts."
]

import random
random.shuffle(jokes)
used_jokes = []

def chatbox_agent(user_input):
    system_instruction = personalities[current_personality]
    user_input_lower = user_input.lower()

    # Optional: simple greetings
    greetings = ["hi", "hello", "hey"]
    if any(greet in user_input_lower for greet in greetings):
        return random.choice(["Hey there!", "Hello! How’s it going?", "Hi! What’s up?"])

    # Check if user wants a joke using multiple keywords
    joke_keywords = ["joke", "funny", "laugh", "random"]

    if any(word in user_input_lower for word in joke_keywords):
        available_jokes = [j for j in jokes if j not in used_jokes]
        if available_jokes:
            joke = random.choice(available_jokes)
            used_jokes.append(joke)
        else:
            joke = random.choice(jokes)  # reuse if all used

        prompt = f"{system_instruction}\nTell a unique, funny version of this joke: {joke}"
    else:
        prompt = f"{system_instruction}\nUser: {user_input}"

    response = chat.send_message(prompt, generation_config={"temperature":1.0})
    return response.text



# 5️⃣ Safe infinite loop for Colab
print("SolarFlare AI ChatBox ready!")
print("Type 'exit' to stop or 'personality: funny' to change tone.\n")

while True:
    user_input = input("You: ")

    # Exit command
    if user_input.lower() == "exit":
        print("SolarFlare: Chat ended.")
        break

    # Change personality dynamically
    if user_input.lower().startswith("personality:"):
        choice = user_input.split(":")[1].strip().lower()
        if choice in personalities:
            current_personality = choice
            print(f"SolarFlare: Personality changed to {current_personality}.")
        else:
            print("SolarFlare: Unknown personality. Try friendly, funny, creative, sarcastic, professional.")
        continue

    # Get AI response
    answer = chatbox_agent(user_input)
    print("SolarFlare:", answer)
    print()
