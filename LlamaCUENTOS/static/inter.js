document.addEventListener("DOMContentLoaded", () => {
    const botMessageElement = document.getElementById('botMessage');
    const villanoContainer = document.getElementById('villanoContainer');
    const villanoGrid = document.getElementById('villanoGrid');
    const villanoText = document.getElementById('villanoText');
    const historiaModal = document.getElementById('historiaModal');
    const closeModalBtn = document.querySelector(".close");
    const historiaTexto = document.getElementById('historiaTexto');
    const audioPlayer = document.getElementById('audioPlayer');
    const audioSource = document.getElementById('audioSource');

    let resumenGuardado = '';  // Almacena el resumen para usarlo en la generación de héroes
    let villanoSeleccionado = '';  // Almacena el villano seleccionado
    let heroeSeleccionado = '';  // Almacena el héroe seleccionado
    let historiaGenerada = '';  // Almacena la historia generada

    // Función para obtener el resumen y luego mostrar villanos
    async function obtenerResumen() {
        botMessageElement.innerHTML = "Generando resumen...";

        try {
            const resumenResponse = await fetch('/resumen', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const resumenResult = await resumenResponse.json();

            if (resumenResult.resumen) {
                botMessageElement.innerHTML = resumenResult.resumen;
                resumenGuardado = resumenResult.resumen;

                setTimeout(() => {
                    botMessageElement.innerHTML = '';
                    mostrarVillanos(resumenResult.resumen);
                }, 5000);
            } else if (resumenResult.error) {
                botMessageElement.innerHTML = resumenResult.error;
            }
        } catch (error) {
            botMessageElement.innerHTML = "Hubo un error al generar el resumen.";
        }
    }

    // Función para mostrar villanos
    async function mostrarVillanos(resumen) {
        try {
            const villanoResponse = await fetch('/villanos', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ resumen })
            });

            const villanoResult = await villanoResponse.json();

            if (villanoResult.villanos) {
                villanoContainer.style.display = 'block';
                villanoGrid.innerHTML = '';

                const villanos = villanoResult.villanos.split('\n');
                villanos.forEach((villano) => {
                    const div = document.createElement('div');
                    div.classList.add('villano-item');
                    div.innerHTML = villano;
                    villanoGrid.appendChild(div);

                    div.addEventListener('click', () => {
                        villanoSeleccionado = villano;
                        alert(`Has seleccionado: ${villano}`);
                        mostrarHeroes(villano);
                    });
                });
            } else if (villanoResult.error) {
                botMessageElement.innerHTML = villanoResult.error;
            }
        } catch (error) {
            botMessageElement.innerHTML = "Hubo un error al generar los villanos.";
        }
    }

    // Función para mostrar héroes
    async function mostrarHeroes(villano) {
        try {
            const heroeResponse = await fetch('/heroes', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ resumen: resumenGuardado, villano: villanoSeleccionado })
            });

            const heroeResult = await heroeResponse.json();

            if (heroeResult.heroes) {
                villanoText.innerHTML = 'Elige al héroe:';
                villanoGrid.innerHTML = '';

                const heroes = heroeResult.heroes.split('\n');
                heroes.forEach((heroe) => {
                    const div = document.createElement('div');
                    div.classList.add('heroe-item');
                    div.innerHTML = heroe;
                    villanoGrid.appendChild(div);

                    div.addEventListener('click', () => {
                        heroeSeleccionado = heroe;
                        alert(`Has seleccionado al héroe: ${heroe}`);
                        generarHistoria();
                    });
                });
            } else if (heroeResult.error) {
                botMessageElement.innerHTML = heroeResult.error;
            }
        } catch (error) {
            botMessageElement.innerHTML = "Hubo un error al generar los héroes.";
        }
    }

    // Función para generar la historia y mostrar el modal
    async function generarHistoria() {
        try {
            const historiaResponse = await fetch('/historia', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    resumen: resumenGuardado,
                    villano: villanoSeleccionado,
                    heroe: heroeSeleccionado
                })
            });

            const historiaResult = await historiaResponse.json();

            if (historiaResult.historia) {
                historiaGenerada = historiaResult.historia;
                console.log("Historia generada: ", historiaGenerada);

                // Mostrar la historia en el modal
                historiaTexto.innerHTML = historiaGenerada;
                historiaModal.style.display = 'block';

                // Establecer el audio en el reproductor
                audioSource.src = `output (3).wav`;  // Aquí suponemos que hay un archivo de audio relacionado con el héroe
                audioPlayer.load(); // Recargar el audio en el reproductor

            } else if (historiaResult.error) {
                botMessageElement.innerHTML = historiaResult.error;
            }
        } catch (error) {
            botMessageElement.innerHTML = "Hubo un error al generar la historia.";
        }
    }

    // Función para cerrar el modal
    closeModalBtn.addEventListener('click', () => {
        historiaModal.style.display = 'none';
    });

    // Llamar a la función para obtener el resumen
    obtenerResumen();
});
