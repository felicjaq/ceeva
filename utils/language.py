import json

def load_language(lang_code):
    try:
        with open(f'lang/{lang_code}.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise ValueError(f"Language file for '{lang_code}' not found.")
