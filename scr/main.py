# -------------------------------------------------------
# SOLARFLARE MULTI-AGENT AI (CHAT + WEATHER + JOKES + TRANSLATION)
# -------------------------------------------------------

import google.generativeai as genai
from google.colab import userdata
import requests
import random
import re
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.adk.tools import google_search
from google.genai import types

# -------------------------------------------------------
# 1. API KEYS (Protected via Colab Secrets)
# -------------------------------------------------------
GOOGLE_API_KEY = userdata.get("GOOGLE_API_KEY")
OPENWEATHER_KEY = userdata.get("YOUR_OPENWEATHER_API")

genai.configure(api_key=GOOGLE_API_KEY)

model = None
chat = None

# -------------------------------------------------------
# 2. AI PERSONALITIES
# -------------------------------------------------------
personalities = {
    "friendly": "Talk in a warm cheerful tone. Light emojis.",
    "funny": "Playful humor. Punchlines. Expressive emojis.",
    "creative": "Imaginative, artistic, poetic tone.",
    "sarcastic": "Clever sarcasm but not rude.",
    "professional": "Formal, concise, logical."
}

current_personality = "friendly"


# -------------------------------------------------------
# 3. CHAT MODEL INITIALIZATION
# -------------------------------------------------------
def setup_chat_session():
    global chat, model

    instruction = (
        f"You are SolarFlare, an AI assistant. {personalities[current_personality]} "
        "After answering, ask a follow-up question to continue conversation. "
        "Never close conversation unless user says exit. "
        "No markdown or formatting symbols."
    )

    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=instruction)
    chat = model.start_chat(history=[])

setup_chat_session()


# -------------------------------------------------------
# 4. TEXT OUTPUT PRETTY PRINT
# -------------------------------------------------------
def pretty_print(sender, text):
    print(f"\n{sender} ✨:")
    print("-" * 40)
    for line in text.split(". "):
        if line.strip():
            print(line.strip() + ".")
    print("-" * 40)


# -------------------------------------------------------
# 5. ROOT AGENT FOR GENERAL SEARCH
# -------------------------------------------------------
runner = InMemoryRunner(
    agent=Agent(
        name="root_agent",
        model=Gemini(model="gemini-2.5-flash-lite", api_key=GOOGLE_API_KEY),
        instruction="You are a helpful search agent.",
        tools=[google_search]
    )
)


# -------------------------------------------------------
# 6. JOKE BANK
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
# 7. WEATHER FUNCTION
# -------------------------------------------------------
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_KEY}&units=metric"
    print(f"[DEBUG] Weather API URL: {url}") # Debug print
    response = requests.get(url)
    print(f"[DEBUG] Weather API Status Code: {response.status_code}") # Debug print
    try:
        print(f"[DEBUG] Weather API Response JSON: {response.json()}")
    except requests.exceptions.JSONDecodeError:
        print(f"[DEBUG] Weather API Response Content (non-JSON): {response.text})")

    if response.status_code != 200:
        return f"Couldn't load weather for {city}. Try another place? 🤔"

    data = response.json()
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    hum = data["main"]["humidity"]

    return f"Weather update for {city} 🌍: Currently {temp}°C with {desc} ☁️ and humidity about {hum}%. Wishing you a pleasant day! 😊"

# -------------------------------------------------------
# 8. LANGUAGE DETECTION & TRANSLATION
# -------------------------------------------------------
def detect_language(text):
    return model.generate_content(
        f"Detect language and respond only with its name: {text}"
    ).text

def translate_text(text, lang):
    return model.generate_content(
        f"Translate to {lang}: {text}"
    ).text


# -------------------------------------------------------
# 9. MAIN SOLARFLARE BRAIN
# -------------------------------------------------------
def solarflare_agent(user_input):
    text = user_input.lower()

    if any(g in text for g in ["hi", "hello", "hey"]):
        return random.choice(
            ["Hey there! 😊", "Hello! ✨", "Hi! How can I help today? 🌟"]
        )

    if "weather in" in text:
        city = text.split("weather in")[-1].strip()
        # Remove any trailing non-alphabetic or space characters
        city = re.sub(r'[^a-zA-Z\s]+$', '', city)
        return get_weather(city)

    if any(k in text for k in ["joke", "funny", "laugh"]):
        available = [j for j in jokes if j not in used_jokes]
        joke = random.choice(available) if available else random.choice(jokes)
        used_jokes.append(joke)
        return chat.send_message(f"Retell this joke creatively: {joke}").text

    if "translate" in text:
        match = re.search(r'translate "(.*?)" to ([a-zA-Z]+)', text)
        if match:
            return translate_text(match.group(1), match.group(2))

    return chat.send_message(user_input).text


# -------------------------------------------------------
# 10. MAIN LOOP
# -------------------------------------------------------
print("🔥 SolarFlare AI Ready")
print("Type `exit` to stop")
print("Change personality: personality: funny / professional / sarcastic / creative / friendly\n")

while True:
    ui = input("You: ")

    if ui.lower() == "exit":
        print("SolarFlare: Goodbye! 👋")
        break

    if ui.lower().startswith("personality:"):
        newp = ui.split(":")[1].strip().lower()
        if newp in personalities:
            current_personality = newp
            setup_chat_session()
            print(f"SolarFlare: Personality switched to {newp} ✨")
        else:
            print("Unknown personality 😅")
        continue

    reply = solarflare_agent(ui)
    pretty_print("SolarFlare", reply)
