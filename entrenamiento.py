import json
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Embedding
import os

# Crear carpeta 'privado' si no existe
if not os.path.exists('privado'):
    os.makedirs('privado')

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

encoder_input_seq = pad_sequences(encoder_input_seq, maxlen=max_len_input, padding='post')
decoder_input_seq = pad_sequences(decoder_input_seq, maxlen=max_len_output, padding='post')
decoder_target_seq = pad_sequences(decoder_target_seq, maxlen=max_len_output, padding='post')
decoder_target_seq = np.expand_dims(decoder_target_seq, -1)

# Crear el modelo
embedding_dim = 256
latent_dim = 256

# Encoder
encoder_inputs = Input(shape=(None,), name="encoder_inputs")
encoder_embedding = Embedding(vocab_size, embedding_dim, name="encoder_embedding")(encoder_inputs)
encoder_lstm = LSTM(latent_dim, return_state=True, name="encoder_lstm")
encoder_outputs, state_h, state_c = encoder_lstm(encoder_embedding)
encoder_states = [state_h, state_c]

# Decoder
decoder_inputs = Input(shape=(None,), name="decoder_inputs")
decoder_embedding_layer = Embedding(vocab_size, embedding_dim, name="decoder_embedding")
decoder_embedding = decoder_embedding_layer(decoder_inputs)
decoder_lstm = LSTM(latent_dim, return_sequences=True, return_state=True, name="decoder_lstm")
decoder_outputs, _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = Dense(vocab_size, activation='softmax', name="decoder_dense")
decoder_outputs = decoder_dense(decoder_outputs)

# Modelo completo
model = Model([encoder_inputs, decoder_inputs], decoder_outputs)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Entrenar
model.fit([encoder_input_seq, decoder_input_seq], decoder_target_seq,
          batch_size=32,
          epochs=50,
          validation_split=0.2)

# Guardar el modelo completo
model.save('privado/modelo_chatbot.h5')

# Guardar tokenizer
with open('privado/tokenizer.json', 'w', encoding='utf-8') as f:
    f.write(tokenizer.to_json())

# Guardar encoder
encoder_model = Model(encoder_inputs, encoder_states)
encoder_model.save('privado/encoder_model.keras')

# Guardar decoder
decoder_state_input_h = Input(shape=(latent_dim,), name="input_h")
decoder_state_input_c = Input(shape=(latent_dim,), name="input_c")
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]

decoder_inputs_single = Input(shape=(1,), name="decoder_input_single")
decoder_embedding_inf = decoder_embedding_layer(decoder_inputs_single)
decoder_outputs_inf, state_h_inf, state_c_inf = decoder_lstm(
    decoder_embedding_inf, initial_state=decoder_states_inputs)
decoder_outputs_inf = decoder_dense(decoder_outputs_inf)

decoder_model = Model(
    [decoder_inputs_single] + decoder_states_inputs,
    [decoder_outputs_inf, state_h_inf, state_c_inf]
)
decoder_model.save('privado/decoder_model.keras')

print("Modelo, tokenizer, encoder y decoder guardados correctamente")