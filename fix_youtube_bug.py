import re
with open('engine/helper.py', 'r', encoding='utf-8') as f:
    text = f.read()

target1 = """def extract_yt_term(command):
    # Define a regular expression pattern to capture the song name
    pattern = r'play\s+(.*?)\s+on\s+youtube'
    # Use re.search to find the match in the command
    match = re.search(pattern, command, re.IGNORECASE)
    # If a match is found, return the extracted song name; otherwise, return None
    return match.group(1) if match else None"""

replacement1 = """def extract_yt_term(command):
    match = re.search(r'play\s+(.*)', command, re.IGNORECASE)
    if match:
        term = match.group(1).strip()
        term = term.replace("on youtube", "").strip()
        if term:
            return term
    return command"""

text = text.replace(target1, replacement1)
with open('engine/helper.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('engine/command.py', 'r', encoding='utf-8') as f:
    text = f.read()

target2 = """        if "open" in query:
            from engine.features import openCommand
            openCommand(query)
        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)"""

replacement2 = """        if ("youtube" in query and "play" in query) or ("on youtube" in query):
            from engine.features import PlayYoutube
            PlayYoutube(query)
        elif "open" in query:
            from engine.features import openCommand
            openCommand(query)"""

text = text.replace(target2, replacement2)
with open('engine/command.py', 'w', encoding='utf-8') as f:
    f.write(text)

print("Done")
