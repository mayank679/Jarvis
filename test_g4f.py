import g4f

try:
    client = g4f.client.Client()
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Hello, are you working?"}],
    )
    print("G4F Text output:", response.choices[0].message.content)
except Exception as e:
    print("G4F Text Error:", e)
