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

# Create Gemini model - this will now be done in setup_chat_session
model = None # Initialize model to None
chat = None

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

# Function to setup/reset the chat session with the current personality
def setup_chat_session():
    global chat
    global model # Model also needs to be global to be reassigned

    base_system_prompt = "You are SolarFlare, an AI assistant."
    personality_description = personalities.get(current_personality, personalities["friendly"])

    # Combine the base system prompt with the chosen personality instructions.
    # All recurring instructions like follow-up questions, no markdown, etc.,
    # are included here so the solarflare_agent just sends user input.
    system_instruction_full = (
        f"{base_system_prompt} {personality_description} "
        "After answering, ask a related follow-up question or invite the user to talk further. "
        "Never end the conversation unless the user says 'exit'. "
        "Use natural emojis. No markdown. No ** or formatting symbols. Speak clearly and simply."
    )

    # Re-create the model with the system_instruction
    model = genai.GenerativeModel("gemini-2.0-flash", system_instruction=system_instruction_full)
    # Start chat with empty history, as system instruction is now set on the model
    chat = model.start_chat(history=[])

# Initial chat setup
setup_chat_session()


# -------------------------------------------------------
# 3. MULTIPLE LINE CREATION
# -------------------------------------------------------

def pretty_print(sender, text):
    print(f"\n{sender} ✨:")
    print("-" * 40)

    # Split text into multiple lines automatically
    lines = text.split(". ")
    for line in lines:
        if line.strip():
            print(line.strip() + ".")
    print("-" * 40 + "\n")


# -------------------------------------------------------
# 4. SUMMARY AGENT
# -------------------------------------------------------

def summary_agent(text):
    # Use the model directly for single-turn requests, not the chat object
    # The system_instruction on the model will apply here as well, if appropriate.
    summary_prompt = f"""
Summarize the following text in clean, readable chunks.

Rules:
- Break into 2–4 separate lines.
- Each line should contain one clear idea.
- No markdown.
- Natural emojis allowed but optional.

Text to summarize:
{text}
"""
    response = model.generate_content(summary_prompt, generation_config={"temperature": 0.4})
    return response.text


# -------------------------------------------------------
# 5. JOKE BANK
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
# 6. OPENWEATHER API
# -------------------------------------------------------

OPENWEATHER_KEY = userdata.get('YOUR_OPENWEATHER_API')

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
        f"Humidity feels like {hum}%. Interesting vibes today!\n"
        f"Wow👀 That's some interesting facts to know👍"
    )

# -------------------------------------------------------
# 7. AGENT BRAIN
# -------------------------------------------------------
def solarflare_agent(user_input):
    text = user_input.lower()

    # Basic greetings - handled directly without model for quick responses
    if any(g in text for g in ["hi", "hello", "hey"]):
        return random.choice([
            "Hey there! 😊",
            "Hi! How’s your day going? 🌟",
            "Hello! What can I do for you? ✨"
        ])

    # Weather detection
    elif "weather in" in text or "temperature in" in text or "forecast in" in text:
        match = re.search(r"(?:weather|temperature|forecast) in ([a-zA-Z\s]+)", text)
        if match:
            city = match.group(1).strip()
            return get_weather(city)
        return "Tell me which city you're curious about! 🌎"

    # Joke request
    elif any(k in text for k in ["joke", "funny", "laugh"]):
        ava = [j for j in jokes if j not in used_jokes]

        if ava:
            joke = random.choice(ava)
            used_jokes.append(joke)
        else:
            joke = random.choice(jokes)

        # Send the joke content to the chat, the model's personality is set via system_instruction
        response = chat.send_message(f"Please retell this joke: {joke}", generation_config={"temperature": 1.0})
        return response.text

    # Language Detection
    elif "detect language of" in text:
        match = re.search(r"detect language of (.*)", text)
        if match:
            text_to_detect = match.group(1).strip()
            return detect_language(text_to_detect)
        return "Please provide text to detect its language."

    # Translation
    elif "translate" in text and "to" in text:
        match = re.search(r"translate \"(.*?)\" to ([a-zA-Z]+)", text)
        if match:
            text_to_translate = match.group(1)
            target_lang = match.group(2).strip()
            return translate_text(text_to_translate, target_lang)
        return "Please specify the text to translate and the target language, e.g., 'translate \"hello\" to Spanish'."

    else:
        # Normal conversation - send user_input directly to the model
        # The system_instruction is already set on the model
        response = chat.send_message(user_input, generation_config={"temperature": 1.0})
        return response.text


# ---------------------------------------------------------
# 8. LANGUAGE DETECTION USING GEMINI
# ---------------------------------------------------------
def detect_language(text):
    prompt = f"Detect the language of this text and answer ONLY the language name:\n{text}"
    result = model.generate_content(prompt)
    return result.text.strip()


# ---------------------------------------------------------
# 9. TRANSLATION USING GEMINI
# ---------------------------------------------------------
def translate_text(text, target_language):
    prompt = (
        f"Translate this text to {target_language}. Use natural tone, emojis allowed.\n"
        f"Text: {text}"
    )
    result = model.generate_content(prompt)
    return result.text


# -------------------------------------------------------
# 10. MAIN LOOP
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
            setup_chat_session() # Re-setup chat with new personality (and model)
            print(f"SolarFlare: Personality changed to {new_p}! ✨")
        else:
            print("SolarFlare: I don’t know that personality 😅")
        continue

    # Normal response
    freply = solarflare_agent(user_input)
    pretty_print("SolarFlare", freply)
    print()
