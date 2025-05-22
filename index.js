require('dotenv').config();

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const admin = require('./firebase')

const db = admin.firestore();

// Mantiene el estado de cada conversacion en memoria
const sessions = new Map();

// Numero del usuario, se configura en .env -> OWNER_NUMBER=+569XXXXXXXX
const OWNER_NUMBER = ProcessingInstruction.env.OWNER_NUMBER;

// Pasos del flujo conversacional
const steps = ['askName', 'askOrder', 'askCopies', 'askDate', 'confirm'];

function init() {
    const client = new Client({
        authStrategy: new LocalAuth(), // Guarda la sesion para no escanear el QR cada vez
    });

    // Generemos el QR por consola
    client.on('qr', (qr) => {
        qrcode.generate(qr, { small:true });
    });

    client.on('ready', () => {
        console.log('Bot de impresion listo y conectado a WhatsApp');
    });

    client.on('message', async (msg) => {
        // Ignorar mensajes propios
        if (msg.fromMe) return;

        const chatId = msg.from;
        const text = msg.body.trim();

        // Si no hay sesion para este usuario
    })
}