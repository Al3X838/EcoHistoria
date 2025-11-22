// ruleta.js - Juego de Ruleta

// Mostrar/ocultar campo de número según tipo de apuesta
document.addEventListener('DOMContentLoaded', function() {
    const tipoApuesta = document.getElementById('tipo-apuesta');
    const numeroGroup = document.getElementById('numero-group');
    
    if (tipoApuesta && numeroGroup) {
        tipoApuesta.addEventListener('change', function() {
            if (this.value === 'numero') {
                numeroGroup.style.display = 'block';
            } else {
                numeroGroup.style.display = 'none';
            }
        });
    }
});

async function girarRuleta() {
    const cantidadInput = document.getElementById('cantidad-apuesta');
    const tipoApuesta = document.getElementById('tipo-apuesta').value;
    const numeroElegido = document.getElementById('numero-elegido').value;
    const saldoActual = parseInt(document.getElementById('saldo-actual').textContent);
    
    const cantidad = parseInt(cantidadInput.value);
    
    // Validar apuesta
    const validacion = validarApuesta(cantidad, saldoActual);
    if (!validacion.valido) {
        mostrarMensajeJuego(validacion.mensaje, 'error');
        return;
    }
    
    // Deshabilitar botón
    deshabilitarBoton('btn-girar', 5);
    
    // Preparar datos
    const data = {
        apuesta: cantidad,
        tipo: tipoApuesta,
        valor: tipoApuesta === 'numero' ? parseInt(numeroElegido) : null
    };
    
    try {
        // Animar ruleta
        const wheel = document.getElementById('ruleta-wheel');
        const resultadoDisplay = document.getElementById('resultado-display');
        resultadoDisplay.style.display = 'none';
        
        // Girar ruleta (3 vueltas completas + ángulo aleatorio)
        const vueltas = 3;
        const anguloAleatorio = Math.random() * 360;
        const rotacionTotal = (vueltas * 360) + anguloAleatorio;
        
        wheel.style.transform = `rotate(${rotacionTotal}deg)`;
        
        // Hacer petición al servidor
        const response = await fetch('/casino/ruleta/jugar', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        
        const resultado = await response.json();
        
        if (!response.ok) {
            throw new Error(resultado.error || 'Error en la apuesta');
        }
        
        // Esperar animación
        setTimeout(() => {
            // Mostrar resultado
            resultadoDisplay.style.display = 'block';
            resultadoDisplay.querySelector('.resultado-numero').textContent = resultado.resultado.numero;
            resultadoDisplay.querySelector('.resultado-color').textContent = 
                resultado.resultado.color.toUpperCase();
            
            // Actualizar saldo
            actualizarSaldo(resultado.puntos_actuales);
            
            // Mostrar mensaje
            if (resultado.resultado.gano) {
                mostrarMensajeJuego(
                    `¡GANASTE! ${resultado.ganancia} puntos (x${resultado.resultado.multiplicador}). Ganancia neta: ${resultado.ganancia_neta > 0 ? '+' : ''}${resultado.ganancia_neta} pts`,
                    'win'
                );
            } else {
                mostrarMensajeJuego(
                    `Perdiste. El número ganador fue ${resultado.resultado.numero}. -${cantidad} pts`,
                    'error'
                );
            }
        }, 3000);
        
    } catch (error) {
        mostrarMensajeJuego(error.message, 'error');
        console.error('Error:', error);
    }
}