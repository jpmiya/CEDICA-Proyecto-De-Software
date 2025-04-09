<template>
  <div>
    <header>
      <!-- Barra de navegación Bootstrap -->
      <nav class="navbar navbar-expand-lg navbar-light bg-light">
        <div class="container-fluid">
          <RouterLink class="navbar-brand" to="/">
            <img
              alt="Vue logo"
              src="@/assets/logo_cedica.jpg"
              width="150"
              height="40"
              class="d-inline-block align-text-top"
            />
          </RouterLink>
          <button
            class="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarNav"
            aria-controls="navbarNav"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
          <span class="navbar-toggler-icon"></span>
          </button>
          <div class="collapse navbar-collapse" id="navbarNav">
            <ul class="navbar-nav ms-auto">
              <li class="nav-item">
                <RouterLink class="nav-link" to="/">Inicio</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" to="/about">Sobre nosotros</RouterLink>
              </li>
              <li class="nav-item">
                <a href="/contacto" class="nav-link">Contacto</a>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" to="/publications">Noticias</RouterLink>
              </li>
            </ul>
          </div>
        </div>
      </nav>
    </header>
    <main class="content">
      <router-view />
    </main>
  </div>
  <footer>
    <p class="text-center">Calle 44 y 115 (1900) La Plata, La Plata, B 1900, Argentina</p>
    <p class="text-center">Telefono: +5491167630247</p>
    <div class="social-buttons">
      <a href="https://www.instagram.com/cedica.equitacionparatodos/" class="btn btn-social-icon btn-instagram" target="_blank" rel="noopener noreferrer">
        <i class="fab fa-instagram"></i>
      </a>
      <a href="https://www.facebook.com/cedica.equitacionparatodos/" class="btn btn-social-icon btn-facebook" target="_blank" rel="noopener noreferrer">
        <i class="fab fa-facebook-f"></i>
      </a>
      <a href="https://www.youtube.com/@fundacioncedica8972" class="btn btn-social-icon btn-youtube" target="_blank" rel="noopener noreferrer">
        <i class="fab fa-youtube"></i>
      </a>
      <a href="https://twitter.com/CEDICA_" class="btn btn-social-icon btn-twitter" target="_blank" rel="noopener noreferrer">
        <i class="fab fa-twitter"></i>
      </a>
    </div>
    <p class="text-center">© 2024 CEDICA. Todos los derechos reservados.</p>
  </footer>
</template>

<script setup>
</script>

<style scoped>

img.logo {
  height: 50px;
}

/* Contenedor del contenido principal */
.content {
  display: flex;
  flex-direction: column;
  align-items: center; /* Centrar horizontalmente */
  justify-content: flex-start; /* Alinear arriba */
  padding: 2rem;
  margin-top: 1rem;
  min-height: calc(100vh - 200px); /* Altura mínima ajustada */
}

.about {
  padding: 20px;
  background-color: #f9f9f9;
  color: #333;
  font-family: Arial, sans-serif;
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #2c3e50;
}

h2 {
  font-size: 1.5em;
  margin-top: 20px;
  color: #34495e;
}

p {
  line-height: 1.6;
  margin-bottom: 20px;
}

@media (min-width: 1024px) {
  .about {
    min-height: 100vh;
    display: flex;
    align-items: center;
  }
}

.social-buttons {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 10px;
}

.btn-social-icon {
  margin: 0 10px; 
  font-size: 24px;
  color: #fff;
  background-color: #000;
  border-radius: 50%;
  padding: 10px;
  text-align: center;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-instagram {
  background-color: #E4405F;
}

.btn-facebook {
  background-color: #3b5998;
}

.btn-youtube {
  background-color: #FF0000;
}

.btn-twitter {
  background-color: #1DA1F2;
}

footer {
  margin-top: auto; /* Asegura que el footer esté al final del contenido */
  padding: 1rem 0;
  background-color: #f8f9fa;
  text-align: center;
  width: 100%;
}
</style>