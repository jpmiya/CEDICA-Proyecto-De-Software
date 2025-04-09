import { defineStore } from 'pinia'
import axios from 'axios'


export const usePublicationsStore = defineStore( 'publicationsStore', {
    state: () => ({
        publications: [],
        total : 0,
        page: 1,
        per_page: 12,
        loading: false,
        error: null,
    }),
    actions: {
        async fetchPublications({ author = null, published_from = null, published_to = null, page = null, per_page = null } = {}) {
            try {
                let url = `${import.meta.env.VITE_API_URL}/publications/`;

                const params = [];
                if (author) params.push(`author=${author}`);
                if (published_from) params.push(`published_from=${published_from}`);
                if (published_to) params.push(`published_to=${published_to}`);
                if (page) params.push(`page=${page}`);
                if (per_page) params.push(`per_page=${per_page}`);

                if (params.length) {
                    url += `?${params.join('&')}`;
                }
                this.loading = true
                this.error = null
                const response = await axios.get(url)
                this.publications = response.data.data
                this.total = response.data.total
            
                this.page = response.data.page
                this.per_page = response.data.per_page
                if(response.status === 200) {
                    this.msg = 'Publicaciones cargadas con éxito'
                }
            } catch (error) {
                if (error.response) {
                    
                    this.error = error.response.data;
                } else {
                    this.error = 'Ocurrió un error';
                }
            } finally {
                this.loading = false
            }
        },
    },
})