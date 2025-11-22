// casino.js - Funciones generales del casino

function actualizarSaldo(nuevoSaldo) {
    const saldoElement = document.getElementById('saldo-actual');
    if (saldoElement) {
        // Animación de actualización
        saldoElement.style.transform = 'scale(1.2)';
        saldoElement.style.color = '#10b981';
        
        setTimeout(() => {
            saldoElement.textContent = nuevoSaldo;
            saldoElement.style.transform = 'scale(1)';
        }, 200);
        
        setTimeout(() => {
            saldoElement.style.color = '';
        }, 1000);
    }
}

function mostrarMensajeJuego(mensaje, tipo = 'info') {
    const messageElement = document.getElementById('game-message');
    if (messageElement) {
        messageElement.textContent = mensaje;
        messageElement.className = `game-message ${tipo}`;
        messageElement.style.display = 'block';
        
        // Auto-ocultar después de 5 segundos si no es error
        if (tipo !== 'error') {
            setTimeout(() => {
                messageElement.style.display = 'none';
            }, 5000);
        }
    }
}

function deshabilitarBoton(btnId, segundos = 3) {
    const btn = document.getElementById(btnId);
    if (btn) {
        btn.disabled = true;
        const textoOriginal = btn.textContent;
        
        let contador = segundos;
        const intervalo = setInterval(() => {
            btn.textContent = `Espera ${contador}s...`;
            contador--;
            
            if (contador < 0) {
                clearInterval(intervalo);
                btn.disabled = false;
                btn.textContent = textoOriginal;
            }
        }, 1000);
    }
}

function validarApuesta(cantidad, saldoActual) {
    const min = 10;
    const maxPorcentaje = 0.30;
    const max = Math.floor(saldoActual * maxPorcentaje);
    
    if (cantidad < min) {
        return { valido: false, mensaje: `La apuesta mínima es ${min} puntos.` };
    }
    
    if (cantidad > max) {
        return { valido: false, mensaje: `Solo puedes apostar hasta ${max} puntos (30% de tu saldo).` };
    }
    
    if (cantidad > saldoActual) {
        return { valido: false, mensaje: 'No tienes suficientes puntos.' };
    }
    
    return { valido: true };
}