const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const fs = require('fs');
const readline = require('readline-sync');
const { timeStamp } = require('console');

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

    // Obtener los chats
    const chats = await client.getChats();
    const primerosChats = chats.slice(0, 5);

    console.log("\nChats disponibles: ");
    primerosChats.forEach((chat, index) => {
        const tipo = chat.isGroup ? "grupo" : "chat individual";
        const nombre  = chat.name || chat.id.user;
        console.log(`[${index}] - ${nombre} (${tipo})`); 
    });

    // Elegir el chat de entrenamiento
    const chatIndex = readline.questionInt("\nIngrese el numero que quiere usar: ");
    const chat = primerosChats[chatIndex];

    // Numero de mensajes a extraer
    const cantidad = readline.questionInt('¿Cuantos mensajes quieres extraer?: ');

    // Obtener mensajes
    const mensajes = await chat.fetchMessages({ limit: cantidad});

    let data = [];

    // Si es un chat individual
    if (!chat.isGroup) {
        const contacto = await chat.getContact();
        const nombreOtro = contacto.pushname || contacto.name || contacto.number;

        console.log(`Este es un chat individual con: ${nombreOtro}`);
        const miNombre = readline.question("¿Que nombre quieres usar para ti?: ");

        data = mensajes.map(msg => ({
            from: msg.fromMe ? miNombre : nombreOtro,
            message: msg.body,
            timestamp: msg.timestamp
        }));

    } else {
        // Si es grupo
        console.log("\n Este es un grupo. Detectando participantes...");

        const participantes = chat.participantes || [
            ...new Set(mensajes.map(msg => msg.author || msg.from))
        ];

        // Mostrar particiantes
        const aliasMap = {};
        participantes.forEach((p, index) => {
            const id = p.id ? p.id._serialized : p;
            console.log(`[${index}] - ${id}`);
        });

        // "¿Quien eres tu?"
        const miIndex = readline.questionInt("\n ¿Cual de estos eres tu? Ingresa el numero: ");
        const yoID = participantes[miIndex].id ? participantes[miIndex].id._serialized : participantes[miIndex];
        const miNombre = readline.question("¿Que nombre quieres usar para ti?: ");
        aliasMap[yoID] = miNombre;

        // Asignar alias a los demas
        const asignarResto = readline.question("¿Deseas asignar nombres a los demas particpantes? (s/n): ");
        if (asignarResto.toLowerCase() === "s") {
            participantes.forEach((p, index) => {
                const id = p.id ? p.id._serialized : p;
                if (id !== yoID) {
                    const nombre = readline.question(`Nombre para ${id}: `);
                    aliasMap[id] = nombre;
                }
            });
        }

        // Mapear mensajes con alias
        data = mensajes.map(msg => {
            const id = msg.author || msg.from;
            const nombre = aliasMap[id] || id;
            return {
                from: nombre,
                message : msg.body,
                timestamp: msg.timestamp
            };
        });
    }

    // Guardar historial
    const rutaCarpeta = "./data";
    const nombreArchivo = "historial_chat.json";
    const rutaCompleta = `${rutaCarpeta}/${nombreArchivo}`;

    // Crear carpeta si no existe
    if (!fs.existsSync(rutaCarpeta)) {
        fs.mkdirSync(rutaCarpeta);
    }

    // Guardar archivo
    fs.writeFileSync(rutaCompleta, JSON.stringify(data, null, 4), 'utf-8');
    console.log(`\nHistorial guardado en ${rutaCompleta}`);

    // Cerrar sesion
    client.destroy();
    console.log("Conexion cerrada.");
});

// Iniciar cliente
client.initialize();