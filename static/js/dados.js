// dados.js - Juego de Dados

// Mostrar/ocultar campo de suma según tipo de apuesta
document.addEventListener('DOMContentLoaded', function() {
    const tipoApuesta = document.getElementById('tipo-apuesta');
    const sumaGroup = document.getElementById('suma-group');
    
    if (tipoApuesta && sumaGroup) {
        tipoApuesta.addEventListener('change', function() {
            if (this.value === 'suma') {
                sumaGroup.style.display = 'block';
            } else {
                sumaGroup.style.display = 'none';
            }
        });
    }
});

async function lanzarDados() {
    const cantidadInput = document.getElementById('cantidad-apuesta');
    const tipoApuesta = document.getElementById('tipo-apuesta').value;
    const sumaElegida = document.getElementById('suma-elegida').value;
    const saldoActual = parseInt(document.getElementById('saldo-actual').textContent);
    
    const cantidad = parseInt(cantidadInput.value);
    
    // Validar apuesta
    const validacion = validarApuesta(cantidad, saldoActual);
    if (!validacion.valido) {
        mostrarMensajeJuego(validacion.mensaje, 'error');
        return;
    }
    
    // Deshabilitar botón
    deshabilitarBoton('btn-lanzar', 4);
    
    // Preparar datos
    const data = {
        apuesta: cantidad,
        tipo: tipoApuesta,
        valor: tipoApuesta === 'suma' ? parseInt(sumaElegida) : null
    };
    
    const dado1 = document.getElementById('dado-1');
    const dado2 = document.getElementById('dado-2');
    const sumaDisplay = document.getElementById('suma-display');
    
    sumaDisplay.style.display = 'none';
    
    try {
        // Animar dados girando
        dado1.classList.add('rolling');
        dado2.classList.add('rolling');
        
        // Cambiar valores rápidamente
        const intervalo = setInterval(() => {
            dado1.querySelector('.dado-face').textContent = Math.floor(Math.random() * 6) + 1;
            dado2.querySelector('.dado-face').textContent = Math.floor(Math.random() * 6) + 1;
        }, 100);
        
        // Hacer petición al servidor
        const response = await fetch('/casino/dados/jugar', {
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
        
        // Esperar 2 segundos
        setTimeout(() => {
            clearInterval(intervalo);
            
            // Mostrar resultado final
            dado1.classList.remove('rolling');
            dado2.classList.remove('rolling');
            
            dado1.querySelector('.dado-face').textContent = resultado.resultado.dado1;
            dado2.querySelector('.dado-face').textContent = resultado.resultado.dado2;
            
            // Mostrar suma
            sumaDisplay.style.display = 'block';
            document.getElementById('suma-valor').textContent = resultado.resultado.suma;
            
            // Actualizar saldo
            actualizarSaldo(resultado.puntos_actuales);
            
            // Mostrar mensaje
            if (resultado.resultado.gano) {
                mostrarMensajeJuego(
                    `¡GANASTE! Dados: ${resultado.resultado.dado1} + ${resultado.resultado.dado2} = ${resultado.resultado.suma}. ${resultado.ganancia} puntos (x${resultado.resultado.multiplicador}). Ganancia neta: ${resultado.ganancia_neta > 0 ? '+' : ''}${resultado.ganancia_neta} pts`,
                    'win'
                );
            } else {
                mostrarMensajeJuego(
                    `Perdiste. Dados: ${resultado.resultado.dado1} + ${resultado.resultado.dado2} = ${resultado.resultado.suma}. -${cantidad} pts`,
                    'error'
                );
            }
        }, 2000);
        
    } catch (error) {
        clearInterval(intervalo);
        dado1.classList.remove('rolling');
        dado2.classList.remove('rolling');
        mostrarMensajeJuego(error.message, 'error');
        console.error('Error:', error);
    }
}