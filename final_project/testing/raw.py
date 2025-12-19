from openai import OpenAI

client = OpenAI(
    api_key="sk-p-6q9ueChtyIoeHuAZzTzA",
    base_url="https://api.artemox.com/v1"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": "Hello world"}]
    # ,stream=True
    # ,timeout=600
)
print(response.choices[0].message.content)
