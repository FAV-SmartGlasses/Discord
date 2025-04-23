import requests
import dotenv
import os

dotenv.load_dotenv(os.path.abspath(".env"))

LLM_URL = os.getenv("LLM_SERVER")

def send_to_llm(model, messages, temperature):
    global ai_messages

    ai_messages = messages

    payload = {
        "model": model,
        "messages": ai_messages.get(model),
        "temperature": temperature
    }

    response = requests.post(LLM_URL, json=payload)
    if response.status_code == 200:
        text = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip()

        ai_messages.get(model).append({"role": "assistant", "content": text})

        return text, 200
    else:
        return f"Error: {response.status_code} - {response.text}", response.status_code
    
def get_models():
    url = os.getenv("MODELS")
    response = requests.get(url)

    if response.ok:
        return response.json().get("data"), 200
    else:
        return f"Error: {response.status_code} - {response.text}", response.status_code
    
print(send_to_llm("dolphin-2.8-mistral-7b-v02", {"dolphin-2.8-mistral-7b-v02": [{"role": "user", "content": "hello"}]}, .7))
print(get_models())