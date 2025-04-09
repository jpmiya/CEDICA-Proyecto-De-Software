<template>
  <div class="home-view">
    <header>
      <h1>Centro de Equitación para Personas con Discapacidad y Carenciadas (CEDICA)</h1>
    </header>
    <div id="carouselExampleIndicators" class="carousel slide" data-bs-ride="carousel">
      <div class="carousel-indicators">
        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="0" class="active" aria-current="true" aria-label="Slide 1"></button>
        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="1" aria-label="Slide 2"></button>
        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="2" aria-label="Slide 3"></button>
        <button type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide-to="3" aria-label="Slide 4"></button>
      </div>
    <div class="container-fluid">
      <h2>¡Bienvenido!</h2>
      <p>Treinta años de crecimiento, de aprendizaje, de brindar lo mejor de nosotrxs para quienes lo necesitan y de ampliar redes con colegas para hacer de las TACAs una actividad cada día más profesional!</p>
    </div>
      <div class="carousel-inner">
        <div class="carousel-item active">
          <img src="@/assets/image_1.jpg" class="d-block w-100 carousel-image" alt="Image 1">
        </div>
        <div class="carousel-item">
          <img src="@/assets/image_2.jpg" class="d-block w-100 carousel-image" alt="Image 2">
        </div>
        <div class="carousel-item">
          <img src="@/assets/image_3.jpg" class="d-block w-100 carousel-image" alt="Image 3">
        </div>
        <div class="carousel-item">
          <img src="@/assets/istockphoto-538856809-612x612.jpg" class="d-block w-100 carousel-image" alt="Image 4">
        </div>
      </div>
      <button class="carousel-control-prev" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="prev" style="background-color: black; width: 30px; height: 30px; position: absolute; top: 50%; transform: translateY(-50%);">
        <span class="carousel-control-prev-icon" aria-hidden="true" style="width: 20px; height: 20px;"></span>
        <span class="visually-hidden">Anterior</span>
      </button>
      <button class="carousel-control-next" type="button" data-bs-target="#carouselExampleIndicators" data-bs-slide="next" style="background-color: black; width: 30px; height: 30px; position: absolute; top: 50%; right: 0; transform: translateY(-50%);">
        <span class="carousel-control-next-icon" aria-hidden="true" style="width: 20px; height: 20px;"></span>
        <span class="visually-hidden">Next</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.carousel-image {
  max-height: 400px;
  width: 100%;
  object-fit: contain;
}
</style>
