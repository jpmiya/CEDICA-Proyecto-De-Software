<template>
    <div v-if="publication" class="publication-details">
      <h1>{{ publication.title }}</h1>
      <p>{{ publication.summary }}</p>
      <h5>Publicado por: {{ publication.author }}</h5>
      <h6>Fecha de publicación: {{ new Date(publication.publication_date).toLocaleDateString('es-ES') }}</h6>
      <p v-html="publication.content"></p>
      <button @click="goBack" class="back-button">Volver</button>
    </div>
    <div v-else-if="loading && !publication">
      <p>Cargando publicacion</p>
    </div>
    <div v-else>
      <p>Publicacion no encontrada</p>
    </div>
</template>

<script setup>
import { useRoute } from 'vue-router';
import { usePublicationDetailStore } from '../stores/publicationdetails';
import { onMounted } from 'vue';
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';

// Accede al parámetro `id` de la ruta
const route = useRoute();
const publicationId = route.params.id;
const store = usePublicationDetailStore();
const { publication, loading, error } = storeToRefs(store);
// Usa el store para obtener la publicación

const fetchPublication = async () => {
  await store.fetchPublication(publicationId);
};

const router = useRouter();

const goBack = () => {
    router.push('/publications');
};

// Si no está en el store, haz una consulta al backend
onMounted(async () => {
  if (!publication.value) {
      fetchPublication(publicationId);
  }
});
</script>

<style scoped>
.publication-details {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.publication-details h1 {
  font-size: 2em;
  margin-bottom: 10px;
  color: #333;
}

.publication-details h5, .publication-details h6 {
  color: #666;
}

.publication-details p {
  line-height: 1.6;
  color: #444;
}

.publication-details p:nth-of-type(1) {
  color: #011f3d; /* Dark blue color for the summary */
}

.back-button {
  display: inline-block;
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  text-align: center;
  text-decoration: none;
  font-size: 1em;
  transition: background-color 0.3s ease;
}

.back-button:hover {
  background-color: #0056b3;
}
</style>
