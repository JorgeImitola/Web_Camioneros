use Gestion_paquetes;

db.camion.insertMany([
    {
        _id: "ABC123",
        modelo: "Freightliner Cascadia",
        tipo: "Tráiler",
        potencia: "500 HP",
        conductores: ["CAMP800101ABC"]
    },
    {
        _id: "XYZ789",
        modelo: "Volvo VNL",
        tipo: "Camión de redilas",
        potencia: "450 HP",
        conductores: ["GOMJ850202XYZ"]
    },
    {
        _id: "DEF456",
        modelo: "Kenworth W900",
        tipo: "Volteo",
        potencia: "600 HP",
        conductores: ["CAMP800101ABC", "GOMJ850202XYZ"]
    }
]);

db.camionero.insertMany([
    {
        _id: "CAMP800101ABC",
        nombre: "Juan Pérez López",
        telefono: "5551234567",
        direccion: "Calle Falsa 123, CDMX",
        salario: 15000,
        poblacion: "Ciudad de México",
        camiones_asignados: ["ABC123", "DEF456"]
    },
    {
        _id: "GOMJ850202XYZ",
        nombre: "María Gómez Jiménez",
        telefono: "5557654321",
        direccion: "Av. Siempre Viva 456, GDL",
        salario: 18000,
        poblacion: "Guadalajara",
        camiones_asignados: ["XYZ789", "DEF456"]
    }
]);

db.ciudad.insertMany([
    {
        _id: "MTY",
        nombre: "Monterrey",
        apartado_postal: "G4000"
    },
    {
        _id: "GDL",
        nombre: "Guadalajara",
        apartado_postal: "44100"
    },
    {
        _id: "CDMX",
        nombre: "Ciudad de México",
        apartado_postal: "01000"
    },
    {
        _id: "BGT",
        nombre: "Bogotá",
        apartado_postal: "60000"
    },
    {
        _id: "STG",
        nombre: "Santiago de Chile",
        apartado_postal: "7000"
    }
]);

db.paquete.insertMany([
    {
        _id: "PKG001",
        descripcion: "Electrónicos",
        destino: "Monterrey",
        dir_destinatario: "Av. Industrial 789",
        camionero_asignado: "CAMP800101ABC",
        ciudad_destino: "MTY"
    },
    {
        _id: "PKG002",
        descripcion: "Ropa",
        destino: "Guadalajara",
        dir_destinatario: "Calle Reforma 101",
        camionero_asignado: "GOMJ850202XYZ",
        ciudad_destino: "GDL"
    },
    {
        _id: "PKG003",
        descripcion: "Muebles",
        destino: "Monterrey",
        dir_destinatario: "Blvd. Constitución 200",
        camionero_asignado: "CAMP800101ABC",
        ciudad_destino: "MTY"
    }
]);