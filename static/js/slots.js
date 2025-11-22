// slots.js - Juego de Slots

const SIMBOLOS = ['🌱', '🌿', '🍃', '♻️', '🌍', '💚', '🌳', '🌲'];

function obtenerSimboloAleatorio() {
    return SIMBOLOS[Math.floor(Math.random() * SIMBOLOS.length)];
}

async function girarSlots() {
    const cantidadInput = document.getElementById('cantidad-apuesta');
    const saldoActual = parseInt(document.getElementById('saldo-actual').textContent);
    const cantidad = parseInt(cantidadInput.value);
    
    // Validar apuesta
    const validacion = validarApuesta(cantidad, saldoActual);
    if (!validacion.valido) {
        mostrarMensajeJuego(validacion.mensaje, 'error');
        return;
    }
    
    // Deshabilitar botón
    deshabilitarBoton('btn-girar', 4);
    
    const reels = [
        document.getElementById('reel-1'),
        document.getElementById('reel-2'),
        document.getElementById('reel-3')
    ];
    
    // Limpiar clases previas
    reels.forEach(reel => {
        reel.classList.remove('win');
    });
    
    try {
        // Hacer petición al servidor
        const response = await fetch('/casino/slots/jugar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ apuesta: cantidad })
        });
        
        const resultado = await response.json();
        
        if (!response.ok) {
            throw new Error(resultado.error || 'Error en la apuesta');
        }
        
        // Animar cada rodillo secuencialmente
        for (let i = 0; i < 3; i++) {
            await animarRodillo(reels[i], resultado.resultado.rodillos[i], i);
        }
        
        // Si ganó, animar rodillos
        if (resultado.resultado.gano) {
            reels.forEach(reel => reel.classList.add('win'));
            
            mostrarMensajeJuego(
                `¡GANASTE! ${resultado.resultado.rodillos.join(' ')} = ${resultado.ganancia} puntos (x${resultado.resultado.multiplicador}). Ganancia neta: ${resultado.ganancia_neta > 0 ? '+' : ''}${resultado.ganancia_neta} pts`,
                'win'
            );
        } else {
            mostrarMensajeJuego(
                `${resultado.resultado.rodillos.join(' ')} - No hubo combinación ganadora. -${cantidad} pts`,
                'error'
            );
        }
        
        // Actualizar saldo
        actualizarSaldo(resultado.puntos_actuales);
        
    } catch (error) {
        mostrarMensajeJuego(error.message, 'error');
        console.error('Error:', error);
    }
}

function animarRodillo(reel, simboloFinal, retraso) {
    return new Promise(resolve => {
        setTimeout(() => {
            reel.classList.add('spinning');
            
            let contador = 0;
            const maxGiros = 20;
            
            const intervalo = setInterval(() => {
                reel.querySelector('.reel-symbol').textContent = obtenerSimboloAleatorio();
                contador++;
                
                if (contador >= maxGiros) {
                    clearInterval(intervalo);
                    reel.classList.remove('spinning');
                    reel.querySelector('.reel-symbol').textContent = simboloFinal;
                    resolve();
                }
            }, 50);
        }, retraso * 500);
    });
}
