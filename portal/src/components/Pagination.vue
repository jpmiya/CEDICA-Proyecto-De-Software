<template>
    <nav v-if="totalPages>0" class="pagination">
      <button 
        :disabled="page === 1" 
        @click="$emit('change-page', page - 1)">
        Anterior
      </button>
  
      <span>Página {{ page }} de {{ totalPages }}</span>
  
      <button 
        :disabled="page === totalPages" 
        @click="$emit('change-page', page + 1)">
        Siguiente
      </button>
    </nav>
  </template>
  
  <script>
  export default {
    props: {
      page: {
        type: Number,
        required: true,
      },
      totalPages: {
        type: Number,
        required: true,
      },
    },
  };
  </script>
  
  <style scoped>
  .pagination {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 1rem;
    margin-top: 1rem;
  }
  
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  </style>
  