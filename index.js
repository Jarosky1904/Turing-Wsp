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
client.on('ready', () => {
    console.log('Cliente conectado con exito');
});

// Escuchar mensajes y guardarlos en un archivo
client.on('message', async msg => {
    console.log(`[${msg.from}] ${msg.body}`);

    // Guardar mensaje en archivo JSON
    const data = { from: msg.from, message:msg.body, timestamp: msg.timestamp };
    fs.appendFileSync('chats.json', JSON.stringify(data) + '\n');
});

// Iniciar cliente
client.initialize();