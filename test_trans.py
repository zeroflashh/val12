from deep_translator import GoogleTranslator

text = "» you don't have permissions to manage video chats.\n\nreload admin cache via /reload {0}"
translator = GoogleTranslator(source='en', target='es')
res = translator.translate(text)
print(res)
