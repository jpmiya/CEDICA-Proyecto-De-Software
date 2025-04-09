<template>
  <body>
    <div class="container mt-4">
      <router-view />
      <h2>Listado de noticias y articulos</h2>

      <!-- Inputs para filtros -->
      <form @submit.prevent="applyFilters" class="mb-4">
        <div class="row">
          <div class="col-md-3 mb-2">
            <label for="author" class="form-label">Autor</label>
            <input
              type="text"
              id="author"
              v-model="filters.author"
              class="form-control"
              placeholder="Nombre del autor"
            />
          </div>
          
          <div class="col-md-3 mb-2">
            <label for="published_from" class="form-label">Publicado Desde</label>
            <input
              type="date"
              id="published_from"
              v-model="filters.published_from"
              class="form-control"
            />
          </div>

          <div class="col-md-3 mb-2">
            <label for="published_to" class="form-label">Publicado Hasta</label>
            <input
              type="date"
              id="published_to"
              v-model="filters.published_to"
              class="form-control"
            />
          </div>

          <div class="col-md-2 mb-2">
            <label for="per_page" class="form-label">Ver</label>
            <input
              type="number"
              id="per_page"
              v-model.number="filters.per_page"
              class="form-control"
              min="1"
              @blur="validatePerPage"
            />
            <div v-if="perPageWarning" class="text-warning">
              {{ perPageWarning }}
            </div>
          </div>
        </div>

        <div class="d-flex justify-content-between mt-3">
            <!-- Botón "Limpiar filtros" -->
            <a href="/publications" class="btn btn-secondary">Limpiar filtros</a>

            <!-- Botón "Aplicar filtros" -->
            <button type="submit" class="btn btn-primary">Aplicar filtros</button>
        </div>
      </form>
      
      <!-- Tabla de publicaciones -->
      <p v-if="loading">Cargando...</p>
      <div v-if="error" class="alert alert-danger mt-4" role="alert">
            {{ error }}
        </div>
      <table
        v-if="!loading && publications.length"
        class="table table-striped table-hover table-bordered"
      >
        <thead class="thead-dark">
          <tr>
            <th scope="col">Titulo</th>
            <th scope="col">Fecha de Publicacion</th>
            <th scope="col">Copete</th>
            <th scope="col">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="publication in publications" :key="publication.id">
            <td>{{ publication.title }}</td>
            <td>{{ formatDate(publication.publication_date) }}</td>
            <td>{{ publication.summary }}</td>
            <td>
                <a
                :href="`/publicationdetail/${publication.id}`"
                class="btn btn-primary btn-sm"
                >
                Detalles
                </a>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-if="!loading && !publications.length">No se encontraron publicaciones.</p>

      <Pagination
        :page="filters.page"
        :totalPages="totalPages"
        @change-page="changePage"
      />
    </div>
  </body>
</template>

<script setup>
import { usePublicationsStore } from "../stores/publications";
import { storeToRefs } from "pinia";
import { onMounted, reactive, computed, ref } from "vue";
import Pagination from "@/components/Pagination.vue";
import { useRouter } from 'vue-router';

const store = usePublicationsStore();
const { publications, loading, error, total } = storeToRefs(store);

const filters = reactive({
  author: "",
  published_from: "",
  published_to: "",
  page: 1,
  per_page: 10,
});

const totalPages = computed(() => {
  return Math.ceil(total.value / filters.per_page);
});

const router = useRouter();

const fetchPublications = async () => {
  await store.fetchPublications(filters);
};

const perPageWarning = ref("");

const validatePerPage = () => {
  if (!filters.per_page || filters.per_page < 1) {
    perPageWarning.value = "No se ingresó un número válido.";
    filters.per_page = 10;
  } else {
    perPageWarning.value = "";
  }
};

const applyFilters = () => {
  validatePerPage();
  filters.page = 1;
  fetchPublications();
};

const changePage = (page) => {
  filters.page = page;
  fetchPublications();
};

onMounted(() => {
  if (!publications.value.length) {
    fetchPublications();
  }
});

const formatDate = (dateString) => {
  const date = new Date(`${dateString}T00:00:00`); // Convierte la cadena a un objeto Date
  return date.toLocaleDateString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
};
</script>

<style scoped>
table {
  width: 80%; /* Ajusta el ancho al 80% de la pantalla */
  border-collapse: collapse;
  margin: 0 auto; /* Centra la tabla horizontalmente */
}

th,
td {
  border: 1px solid #ddd;
  padding: 8px;
  text-align: left;
}

h2 {
  text-align: center;
  margin-bottom: 1rem;
}

form .form-label {
  font-weight: bold;
}

form .btn {
  margin-top: 1rem;
}
</style>
