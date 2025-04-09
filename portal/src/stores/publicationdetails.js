import { defineStore } from 'pinia'
import axios from 'axios'

export const usePublicationDetailStore = defineStore( 'publicationDetailStore', {
    state: () => ({
        publication: null,
        loading: false,
        error: null,
    }),
    actions: {
        async fetchPublication(id) {
            try {
                this.loading = true
                this.error = null
                const response = await axios.get(`${ import.meta.env.VITE_API_URL }/publications/${id}`)
                this.publication = response.data
                if(response.status === 200) {
                    this.msg = 'Publicacion cargada con éxito'
                }
            } catch (error) {
                
                error.response
                    ? (this.error = error.response.data.message)
                    : (this.error = 'Ocurrió un error')
            } finally {
                this.loading = false
            }
        },
    },
})