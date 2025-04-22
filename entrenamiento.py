import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding

# Cargar los pares
with open('data\entrenamiento_pares.json', 'r', encoding='utf-8') as f:
    pares = json.load(f)

entradas = [p["entrada"] for p in pares]
respuestas = ['<sos> ' + p["respuesta"] + ' <eos>' for p in pares]

# Tokenizacion
tokenizer = Tokenizer(oov_token='<OOV>')
tokenizer.fit_on_texts(entradas + respuestas)
word_index = tokenizer.word_index
vocab_size = len(word_index) + 1

# Secuencias y padding
max_len_input = max(len(s.split()) for s in entradas)
max_len_output = max(len(s.split()) for s in respuestas)

encoder_input_seq = tokenizer.texts_to_sequences(entradas)
decoder_input_seq = tokenizer.texts_to_sequences(respuestas)
decoder_target_seq = [seq[1:] for seq in decoder_input_seq] # remove <sos>

encoder_input_seq = pad_sequences(encoder_input_seq, max_len_input, padding='post')
decoder_input_seq = pad_sequences(decoder_input_seq, max_len_output, padding='post')
decoder_target_seq = pad_sequences(decoder_target_seq, maxlen=max_len_output, padding='post')

# Crear el modelo
embedding_dim = 256
latent_dim = 256

# Encoder
encoder_inputs = Input(shape=(None,))
x = Embedding(vocab_size, embedding_dim)(encoder_inputs)
encoder_outputs, state_h, state_c = LSTM(latent_dim, return_state=True)(x)
encoder_states = [state_h, state_c]

# Decoder
decoder_inputs = Input(shape=(None,))
x = Embedding(vocab_size, embedding_dim)(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True)
decoder_outputs, _, _ = decoder_lstm(x, initial_state=encoder_states)
decoder_dense = Dense(vocab_size, activation='softmax')
decoder_outputs = decoder_dense(decoder_outputs)

# Modelo completo
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Ajustar dimensiones para target (necesita una dimension extra)
decoder_target_seq = np.expand_dims(decoder_target_seq, -1)

# Entrenar
model.fit([encoder_input_seq, decoder_input_seq], decoder_target_seq,
          batch_size=32,
          epochs=50,
          validation_split=0.2)

# Guardar el modelo y el tokenizer
model.save('privado/modelo_chatbot.h5')
with open('privado/tokenizer.json', 'w', encoding='utf-8') as f:
    f.write(tokenizer.to_json())

print("Modelo entrenado y guardado.")