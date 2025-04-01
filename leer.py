import json

# Leer el archivo de chats
with open ('chats.json', 'r', encoding='utf-8') as file:
    messages = [json.loads(line) for line in file]

# Mostrar los mensajes
for msg in messages:
    print(f"De: {msg['from']} - Mensaje: {msg['message']}")