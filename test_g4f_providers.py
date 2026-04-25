import g4f

try:
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4o,
        provider=g4f.Provider.Blackbox,
        messages=[{"role": "user", "content": "Hello, are you working?"}],
    )
    print("G4F Blackbox:", response)
except Exception as e:
    print("Blackbox Error:", e)

try:
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_4o,
        provider=g4f.Provider.DuckDuckGo,
        messages=[{"role": "user", "content": "Hello, are you working?"}],
    )
    print("G4F DuckDuckGo:", response)
except Exception as e:
    print("DuckDuckGo Error:", e)
