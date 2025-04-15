import json
import os
import re

CONFIG_ARCHIVO = "data\config.json"
HISTORIAL_ARCHIVO = "data\historial_chat.json"

def cargar_config():
    if not os.path.exists(CONFIG_ARCHIVO):
        raise FileNotFoundError("No se encontro el archivo config.json")
    
    with open(CONFIG_ARCHIVO, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config.get("usuario", "")

def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^\w\sáéíóúüñ]', '', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def cargar_mensajes():
    if not os.path.exists(HISTORIAL_ARCHIVO):
        print("No se encontro el archivo del historial.")
        return []
    
    with open(HISTORIAL_ARCHIVO, 'r', encoding='utf-8') as f:
        mensajes = json.load(f)
    return mensajes

def agrupar_por_emisor(mensajes):
    bloques = []
    if not mensajes:
        return bloques
    
    actual = mensajes[0]["from"]
    contenido = [mensajes[0]["message"]]

    for mensaje in mensajes[1:]:
        if mensaje["from"] == actual:
            contenido.append(mensaje["message"])
        else:
            bloques.append({
                "from": actual,
                "message": ", ".join(contenido)
            })
            actual = mensaje["from"]
            contenido = [mensaje["message"]]
    
    bloques.append({
        "from": actual,
        "message": ", ".join(contenido)
    })

    return bloques

def generar_pares(bloques, usuario):
    pares = []
    for i in range(len(bloques) - 1):
        actual = bloques[i]
        siguiente = bloques[i + 1]

        if actual["from"] != usuario and siguiente["from"] == usuario:
            entrada = limpiar_texto(actual["message"])
            salida = limpiar_texto(siguiente["message"])
            if entrada and salida:
                pares.append((entrada, salida))
    return pares

def guardar_pares(pares, archivo_salida="data/entrenamiento_pares.json"):
    datos = [{"entrada": inp, "respuesta": out} for inp, out in pares]
    with open(archivo_salida, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=4)
    print(f"Guardados {len(pares)} pares en {archivo_salida}")

if __name__ == "__main__":
    usuario = cargar_config()
    mensajes = cargar_mensajes()
    bloques = agrupar_por_emisor(mensajes)
    pares = generar_pares(bloques, usuario)
    guardar_pares(pares)