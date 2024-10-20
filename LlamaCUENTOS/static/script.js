// Obtenemos el modal y los elementos que necesitamos
const modal = document.getElementById("imageModal");
const modalContent = document.querySelector(".modal-content");
const modalImg1 = document.getElementById("modalImage1");
const modalImg2 = document.getElementById("modalImage2");
const closeBtn = document.querySelector(".close");

const images = document.querySelectorAll(".grid-item");

// Asignamos las imágenes correspondientes a cada elemento del grid
const modalImages = {
  0: {
    img1: document.getElementById("image1A").src,
    img2: document.getElementById("image1B").src,
    description1: "La contaminación del aire\n Los contaminantes atmosféricos no siempre se ven y vienen de fuentes muy diversas.",
    description2: "Un grupo de científicos alerta contra el “exceso de confianza” en la captura del CO₂ para revertir el calentamiento",
    url1: document.getElementById("image1A").getAttribute("aire1"), // URL para scraping
    url2: document.getElementById("image1B").getAttribute("aire2")  // URL para scraping
  },
  1: {
    img1: document.getElementById("image2A").src,
    img2: document.getElementById("image2B").src,
    description1: "Descripción detallada para la imagen 2A",
    description2: "Descripción detallada para la imagen 2B",
    url1: document.getElementById("image2A").getAttribute("aire1"),
    url2: document.getElementById("image2B").getAttribute("aire2")
  },
  2: {
    img1: document.getElementById("image3A").src,
    img2: document.getElementById("image3B").src,
    description1: "Lucha contra la deforestación",
    description2: "la pérdida de 10 millones de árboles",
    url1: document.getElementById("image3A").getAttribute("aire1"),
    url2: document.getElementById("image3B").getAttribute("aire2")
  },
  3: {
    img1: document.getElementById("image4A").src,
    img2: document.getElementById("image4B").src,
    description1: "Descripción detallada para la imagen 4A",
    description2: "Descripción detallada para la imagen 4B",
    url1: document.getElementById("image4A").getAttribute("aire1"),
    url2: document.getElementById("image4B").getAttribute("aire2")
  },
  4: {
    img1: document.getElementById("image5A").src,
    img2: document.getElementById("image5B").src,
    description1: "El Misisipi, el río más largo y caudaloso de Norteamérica, se está secando y millones de personas dependen de él",
    description2: "El huracán Katrina fue una de las peores tormentas de la historia de Estados Unidos",
    url1: document.getElementById("image5A").getAttribute("aire1"),
    url2: document.getElementById("image5B").getAttribute("aire2")
  },
  5: {
    img1: document.getElementById("image6A").src,
    img2: document.getElementById("image6B").src,
    description1: "Descripción detallada para la imagen 6A",
    description2: "Descripción detallada para la imagen 6B",
    url1: document.getElementById("image6A").getAttribute("aire1"),
    url2: document.getElementById("image6B").getAttribute("aire2")
  },
};

// Función para enviar una URL al servidor para generar el archivo .txt
const sendUrlToServer = (url) => {
    fetch('/scrape', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data.message); // Confirmación del servidor de que el archivo .txt fue creado
    })
    .catch(error => console.error('Error:', error));
};

// Función para mostrar las imágenes correspondientes en el modal
const showModal = (index) => {
  // Asignamos las imágenes correspondientes al modal
  modalImg1.src = modalImages[index].img1;
  modalImg2.src = modalImages[index].img2;

  // Asignar las descripciones
  const description1 = document.getElementById("description1");
  const description2 = document.getElementById("description2");
  if (description1 && description2) {
    description1.textContent = modalImages[index].description1;
    description2.textContent = modalImages[index].description2;
  }

  // Agregar eventos de clic a las imágenes del modal
  modalImg1.onclick = () => sendUrlToServer(modalImages[index].url1);
  modalImg2.onclick = () => sendUrlToServer(modalImages[index].url2);

  // Animamos la aparición del modal
  modal.style.display = "flex";
  gsap.fromTo(
    modalContent,
    { opacity: 0, y: 50 },
    { opacity: 1, y: 0, duration: 0.5, ease: "power3.out" }
  );
};

// Función para cerrar el modal
const closeModal = () => {
  gsap.to(modalContent, {
    opacity: 0,
    y: -50,
    duration: 0.3,
    ease: "power3.in",
    onComplete: () => {
      modal.style.display = "none";
    },
  });
};

// Asignamos el evento de clic a cada imagen del grid
images.forEach((img, index) => {
  img.addEventListener("click", () => showModal(index));
});

// Cerrar el modal al hacer clic en el botón de cerrar
closeBtn.addEventListener("click", closeModal);

// Cerrar el modal al hacer clic fuera del modal
window.addEventListener("click", (e) => {
  if (e.target === modal) {
    closeModal();
  }
});
