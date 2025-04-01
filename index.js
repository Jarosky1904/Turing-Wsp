const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');

// Inicializar el cliente de Whatsapp
const client = new Client({
    authStrategy: new LocalAuth()
});

// Mostrar el QR en la terminal
client.on('qr', qr => {
    console.log("Escanea el QR en Whatsapp para conectarte:");
    qrcode.generate(qr, { small: true});
});

// Confirmar conexion
client.on('ready', async () => {
    console.log('Cliente conectado con exito');

    // Obtener los chats disponibles
    const chats = await client.getChats();
    console.log(`Chats encontrados ${chats.length} chats.`);

    // Elegir el chat de entrenamiento
    const chat = chats[0]; // Cambia el valor si quieres otro chat;

    // Obtener mensajes del chat
    const mensajes = await chat.fetchMessages({ limit: 200 }); // Obtener los ultimos 200 mensajes

    // Guardar los mensajes en un archivo JSON
    const data = mensajes.map(msg => ({
        form: msg.from,
        message: msg.body,
        timestamp: msg.timestamp
    }));

    fs.writeFileSync('chats_historicos.json', JSON.stringify(data, null, 4), 'utf-8');
    console.log("Historial de chat guardado en chats_historicos.json");
});

// Iniciar cliente
client.initialize();