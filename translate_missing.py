import os
import time
from ruamel.yaml import YAML
from deep_translator import GoogleTranslator
import sys

lang_names = {
    'gu': '🇮🇳 ગુજરાતી',
    'hi': '🇮🇳 हिन्दी',
    'id': '🇮🇩 Indonesia',
    'si': '🇱🇰 සිංහල',
    'ja': '🇯🇵 日本語',
    'ru': '🇷🇺 Русский'
}

gt_langs = {
    'gu': 'gu',
    'hi': 'hi',
    'id': 'id',
    'si': 'si',
    'ja': 'ja',
    'ru': 'ru'
}

def translate_yaml(source_file, target_file, target_lang, gt_lang):
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.allow_duplicate_keys = True
    
    with open(source_file, 'r', encoding='utf-8') as f:
        data = yaml.load(f)
        
    translator = GoogleTranslator(source='en', target=gt_lang)
    
    for key, value in data.items():
        if key == 'name':
            data[key] = lang_names[target_lang]
            continue
            
        if isinstance(value, str) and value.strip():
            try:
                translated = translator.translate(value)
                data[key] = translated
            except Exception as e:
                print(f"Error translating key {key} for {target_lang}: {e}")
                
    with open(target_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f)
        
    print(f"Translated to {target_lang} -> {target_file}", flush=True)

src = r"c:\Users\itsme\Documents\AG\val12\strings\langs\en.yml"
base_dir = r"c:\Users\itsme\Documents\AG\val12\strings\langs"

for lang, gt_lang in gt_langs.items():
    print(f"Processing {lang}...", flush=True)
    target_path = os.path.join(base_dir, f"{lang}.yml")
    translate_yaml(src, target_path, lang, gt_lang)
    time.sleep(1)

print("All translations completed successfully!", flush=True)
