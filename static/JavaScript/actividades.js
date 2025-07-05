const checkboxes = document.querySelectorAll('.tarea-checkbox');

checkboxes.forEach(checkbox => {
    checkbox.addEventListener('change', function() {
        // Obtener las tareas completadas
        const tarea_completada = Array.from(checkboxes)
            .filter(cbx => cbx.checked)
            .map(cbx => cbx.getAttribute('data-idx')); // Obtener el índice de las tareas completadas

        // Enviar los datos al backend usando Fetch API
        fetch('/actualizar_tarea', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ tarea_completada: tarea_completada })
        })
        .then(response => response.json())
        .then(data => {
            const rachaElement = document.querySelector('#racha-fuego');
            rachaElement.innerText = `${data.racha} 🔥`;
            rachaElement.style.color = data.color_racha;

            // Cambiar animación dependiendo de la racha
            if (data.racha >= 5) {
                rachaElement.classList.add('gold', 'saludar'); // Agregar clase saludar para animación
            } else {
                rachaElement.classList.remove('gold', 'saludar'); // Quitar clase saludar si la racha es menor
            }
        });
    });
});
