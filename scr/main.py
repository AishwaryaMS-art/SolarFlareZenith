import google.generativeai as genai
from google.colab import userdata
import requests # Moved import requests to the top
import random # Ensure random is imported
import re # Import regex for city extraction

# Configure the API key using a Colab Secret
GOOGLE_API_KEY = userdata.get('GOOGLE_API_KEY')  # Ensure your key is saved in Colab secrets
# Assuming GOOGLE_API_KEY is already set in the environment or a previous cell
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

random.shuffle(jokes)
used_jokes = []

# Your OpenWeather API key
api_key = "Weather Agent"  # <--- UPDATED WITH YOUR NEW OPENWEATHER API KEY

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        temperature = data['main']['temp']
        weather_description = data['weather'][0]['description']
        humidity = data['main']['humidity']

        # Curious, friendly response
        reply = (
            f"Oh! You want to know about {city}? 🌤️\n"
            f"Well, it seems like the temperature is around {temperature}°C. "
            f"And guess what? The weather is {weather_description}! "
            f"The humidity is at {humidity}%, which is quite interesting, don't you think?"
        )
        return reply
    else:
        return f"Hmm… I couldn’t find the weather for '{city}'. Are you sure that’s a real place? 🤔"

def chatbox_agent(user_input):
    global current_personality # Declare global to modify in this function

    user_lower = user_input.lower()
    emotion_style = (
        "Always use natural emojis. Never use **, *, or markdown formatting. "
        "Speak in a curious, expressive, friendly tone. "
        "Keep messages simple and human-like."
    )

    # Greeting
    if any(g in user_lower for g in ["hi", "hello", "hey"]):
        return random.choice([
            "Heyy! 😊",
            "Hello! What’s up? 🌟",
            "Hi there! How can I help? 🌈"
        ])

    # Weather check
    if "weather in" in user_lower or "temperature in" in user_lower or "forecast in" in user_lower:
        match = re.search(r'(?:weather|temperature|forecast) in ([a-zA-Z\s]+)', user_lower)
        if match:
            city = match.group(1).strip()
            return get_weather(city)
        else:
            return "Tell me the city name and I’ll fetch the weather for you! 🗺️✨"

    # Joke request
    if any(word in user_lower for word in ["joke", "funny", "laugh"]):
        available = [j for j in jokes if j not in used_jokes]
        if available:
            joke = random.choice(available)
            used_jokes.append(joke)
        else:
            joke = random.choice(jokes)
        prompt = f"{personalities[current_personality]}\nTell this joke in your own creative style: {joke}"
    else:
        prompt = f"{personalities[current_personality]}\n{emotion_style}\nUser: {user_input}"

    # Generate AI response
    response = chat.send_message(prompt, generation_config={"temperature": 1.0})
    return response.text

# -------------------------------------------------------
# 6️⃣ MAIN LOOP
# -------------------------------------------------------
print("SolarFlare AI Activated! 🔥")
print("Type 'exit' to quit.")
print("Change personality using: personality: funny | friendly | sarcastic | creative | professional\n")

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("SolarFlare: Goodbye! 👋")
        break

    # Change personality
    if user_input.lower().startswith("personality:"):
        choice = user_input.split(":")[1].strip().lower()
        if choice in personalities:
            current_personality = choice
            print(f"SolarFlare: Personality updated to {choice}! ✨")
        else:
            print("SolarFlare: Unknown personality 😅")
        continue

    # Normal chat
    reply = chatbox_agent(user_input)
    print("SolarFlare:", reply)
    print()
