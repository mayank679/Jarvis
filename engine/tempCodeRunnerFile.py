import google.generativeai as genai

genai.configure(api_key="AIzaSyB_TPBpzulTV1Pi608iyiztuMyeAxYFD-w")

print("Fetching available models for this API key...\n")
for m in genai.list_models():
    print(m.name, "=>", m.supported_generation_methods)