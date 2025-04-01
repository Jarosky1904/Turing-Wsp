import json
import re
import emoji

# Cargar mensajes del historial
with open('chats_historicos.json', 'r', encoding='utf-8') as file:
    messages = json.load(file)

# Funcion para filtrar mensajes no utiles
def es_mensaje_util(msg):
    texto = msg['message']

    #Filtrar mensajes vacios, sticker, eliminados
    if not texto.strip() or "Este mensaje fue eliminado" in texto:
        return False
    
    # Filtrar notificaciones de grupo
    if re.search(r"salió del grupo|añadió a|cambió el nombre", texto):
        return False
    
    return True

# Filtrar los mensajes utiles
mensajes_utiles = [msg for msg in messages if es_mensaje_util(msg)]

# Guardar mensajes filtrados
with open('chats_filtrados.json', 'w', encoding='utf-8') as file:
    json.dump(mensajes_utiles, file, indent=4, ensure_ascii=False)

print(f"Mensajes utiles guardados en chats_filtrados.json ({len(mensajes_utiles)} mensajes)")