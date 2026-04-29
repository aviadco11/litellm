import requests

LITELLM_URL = "http://localhost:4000/v1/chat/completions"
MASTER_KEY = "sk-1234"

response = requests.post(
    LITELLM_URL,
    headers={
        "Authorization": f"Bearer {MASTER_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "mistral/mistral-large-latest",
        "messages": [
            {"role": "user", "content": "Explain what LiteLLM is in 3 sentences."}
        ],
    },
    verify=False,
)

data = response.json()
print(data["choices"][0]["message"]["content"])
