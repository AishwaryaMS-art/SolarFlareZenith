import google.generativeai as genai

genai.configure(api_key="YOUR_API_KEY")

model = genai.GenerativeModel("gemini-2.0-flash")

while True:
    user = input("You: ")
    response = model.generate_content(user)
    print("AI:", response.text)

