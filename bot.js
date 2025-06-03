const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const path = require('path');

const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', qr => {
    qrcode.generate(qr, { small: true});
});

client.on('ready', () => {
    console.log('Bot is ready!');
});

const clients = {}; // Guardar nombres

client.on('message', async msg => {
    const number = msg.from;

    if (!clients[number]) {
        if (msg.body.toLowerCase() === 'hola' || msg.body.toLowerCase().includes('buenas')) {
            clients[number] = { nombre: null};
            msg.reply('Hola, soy el asistente virtual de impresiones Dany, me puede indicar su nombre para ser mas de ayuda')
        } else {
            msg.reply('Hola, me podrias indicar tu nombre para ser mas de ayuda')
        }
    } else if (!clients[number].nombre) {
        clients[number].nombre = msg.body.trim();
        msg.reply(`Mucho gusto, ${clients[number].nombre} puedes enviarme tu archivo o decirme que necesitas imprimir`);
        // Se podria crear una carpeta
    } else {
        if (msg.hasMedia) {
            const media = await msg.downloadMedia();
            const folderName = `${clients[number].nombre.replace(/ /g, "_")}_${new Date().toISOString().split("T")[0]}`;
            const savePath = path.join(__dirname, 'cliente_data, folderName');
            fs.mkdirSync(savePath, { recursive:true });

            const fileName = `${Date.now()}.${media.mimetype.split("/")[1]}`;
            fs.writeFileSync(path.join(savePath, fileName), media.data, { encoding: 'base64' });

            msg.reply('Archivo recibido. ¿Cuantas copias necesitas?');
            clients[number].estado = 'esperando_copias';
        } else {
            msg.reply('Por favor, enviame tu archivo para impresion o dime que necesitas');
        }
    }
});

client.initialize();