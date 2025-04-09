import { defineStore } from "pinia";
import axios from "axios";

export const useContactStore = defineStore("contactStore", {

    state: () => ({
        result: null,
        msg: null,
        error: [],
    }),
    actions: {
        async fetchMessage({ title, full_name, email, message, recaptchaToken }) {
            try {
                const url = `${import.meta.env.VITE_API_URL}/messages/`;
                const data = { title, full_name, email, message, recaptchaToken };
                
                const response = await axios.post(url, data);
                this.result = response.data;
                if (response.status === 201) {
                    this.msg = 'Mensaje enviado con éxito'
                }
            } catch (error) {
                if (error.response) {
                    // Si la respuesta incluye múltiples errores
                    const errors = error.response.data; 
                    this.error = Array.isArray(errors) ? errors : [errors]; // Aseguramos que sea un array
                } else {
                    this.error = ['Ocurrió un error al enviar el formulario'];
                }
            }
        }
    },
});