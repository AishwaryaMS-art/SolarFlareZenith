import google.generativeai as genai
from google.colab import userdata
import requests
import random
import re

# -------------------------------------------------------
# 1. GOOGLE API KEY
# -------------------------------------------------------
GOOGLE_API_KEY = userdata.get("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Create Gemini model + chat session
model = genai.GenerativeModel("gemini-2.0-flash")
chat = model.start_chat(history=[])

# -------------------------------------------------------
# 2. PERSONALITIES
# -------------------------------------------------------
personalities = {
    "friendly": "Talk in a warm, curious, cheerful tone. Use light emojis.",
    "funny": "Use playful humor, light jokes, and expressive emojis.",
    "creative": "Speak with imagination, artistic style, dreamy emojis.",
    "sarcastic": "Be sarcastic, clever, but not rude. Use subtle emojis.",
    "professional": "Be clear, calm, formal, minimal emojis."
}

current_personality = "friendly"

# -------------------------------------------------------
# 3. JOKE BANK
# -------------------------------------------------------
jokes = [
    "Why did the tomato turn red? Because it saw the salad dressing!",
    "Why don’t scientists trust atoms? Because they make up everything!",
    "I told my computer I needed a break, and it said it will go to sleep!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "Why don’t skeletons fight? They don’t have the guts!"
]

random.shuffle(jokes)
used_jokes = []

# -------------------------------------------------------
# 4. OPENWEATHER API
# -------------------------------------------------------
OPENWEATHER_KEY = "Weather Agent"  # <- REPLACE THIS

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"

    response = requests.get(url)
    if response.status_code != 200:
        return f"Oops… I couldn’t find weather info for {city}. Maybe try another place? 🤔"

    data = response.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    hum = data["main"]["humidity"]

    return (
        f"Oh, you're curious about the weather in {city}? 🌍\n"
        f"It’s around {temp}°C right now, with {desc}. "
        f"Humidity feels like {hum}%. Interesting vibes today!"
    )

# -------------------------------------------------------
# 5. AGENT BRAIN
# -------------------------------------------------------
def solarflare_agent(user_input):
    global current_personality

    text = user_input.lower()

    # Basic greetings
    if any(g in text for g in ["hi", "hello", "hey"]):
        return random.choice([
            "Hey there! 😊",
            "Hi! How’s your day going? 🌟",
            "Hello! What can I do for you? ✨"
        ])

    # Weather detection
    if "weather in" in text or "temperature in" in text or "forecast in" in text:
        match = re.search(r"(?:weather|temperature|forecast) in ([a-zA-Z\s]+)", text)
        if match:
            city = match.group(1).strip()
            return get_weather(city)
        return "Tell me which city you're curious about! 🌎"

    # Joke request
    if any(k in text for k in ["joke", "funny", "laugh"]):
        ava = [j for j in jokes if j not in used_jokes]

        if ava:
            joke = random.choice(ava)
            used_jokes.append(joke)
        else:
            joke = random.choice(jokes)

        prompt = (
            personalities[current_personality] +
            f"\nRetell this joke in a fun, expressive style: {joke}"
        )
    else:
        # Normal conversation
        rules = "Use natural emojis. No markdown. No ** or formatting symbols. Speak clearly and simply."
        prompt = f"{personalities[current_personality]}. {rules}. User said: {user_input}"

    # Generate response
    response = chat.send_message(prompt, generation_config={"temperature": 1.0})
    return response.text

# -------------------------------------------------------
# 6. MAIN LOOP
# -------------------------------------------------------
print("SolarFlare AI activated! 🔥")
print("Type 'exit' to stop.")
print("Change personality:  personality: funny / friendly / sarcastic / creative / professional")
print()

while True:
    user_input = input("You: ")

    if user_input.lower() == "exit":
        print("SolarFlare: Goodbye! 👋")
        break

    # Personality change
    if user_input.lower().startswith("personality:"):
        new_p = user_input.split(":")[1].strip().lower()
        if new_p in personalities:
            current_personality = new_p
            print(f"SolarFlare: Personality changed to {new_p}! ✨")
        else:
            print("SolarFlare: I don’t know that personality 😅")
        continue

    # Normal response
    reply = solarflare_agent(user_input)
    print("SolarFlare:", reply)
    print()
