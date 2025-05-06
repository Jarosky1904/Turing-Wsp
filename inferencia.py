import json
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import tokenizer_from_json

# Parametros del modelo
with open("privado/model_config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

max_len_input = config["max_len_input"]
max_len_output = config["max_len_output"]

# Cargar tokenizer
with open('privado/tokenizer.json', 'r', encoding='utf-8') as f:
    tokenizer = tokenizer_from_json(f.read())

word_index = tokenizer.word_index
index_word = {i: w for w, i in word_index.items()}
vocab_size = len(word_index) + 1

# Cargar modelos guardados
encoder_model = load_model('privado/encoder_model.keras')
decoder_model = load_model('privado/decoder_model.keras')

# Generar respuesta
def generar_respuesta(texto_usuario):
    seq = tokenizer.texts_to_sequences([texto_usuario])
    seq = pad_sequences(seq, maxlen=max_len_input, padding='post')

    estados = encoder_model.predict(seq)
    target_seq = np.zeros((1, 1))
    target_seq[0, 0] = tokenizer.word_index.get('<sos>', 1)

    respuesta = ''
    for _ in range(max_len_output):
        output_tokens, h, c = decoder_model.predict([target_seq] + estados)
        token_id = np.argmax(output_tokens[0, -1, :])
        palabra = index_word.get(token_id, '')

        if palabra == '<eos>' or palabra == '':
            break

        respuesta += ' ' + palabra
        target_seq[0, 0] = token_id
        estados = [h, c]

    return respuesta.strip()

# Chat interactivo
if __name__ == '__main__':
    print("Chatbot entrenado listo. Escribe un mensaje (o 'salir' para terminar):\n")
    while True:
        entrada = input("Tu: ")
        if entrada.lower() in ['salir', 'exit', 'quit']:
            break
        respuesta = generar_respuesta(entrada)
        print("Bot:", respuesta)