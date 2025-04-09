<template>
    <div class="container mt-5">
        <h1 class="text-center mb-4">Formulario de Contacto</h1>
        <h6 class="text-center mb-4">*Todos los campos son obligatorios*</h6>
        <div v-if="store.error.length" class="alert alert-danger mt-4" role="alert">
            <ul>
                <li v-for="(err, index) in store.error" :key="index">{{ err }}</li>
            </ul>
        </div>

        <div v-if="store.msg" class="alert alert-success mt-4" role="alert">
            {{ store.msg }}
        </div>
        <form @submit.prevent="handleSubmit">

            <div class="mb-3">
                <label for="title" class="form-label">Titulo del mensaje</label>
                <input type="text" id="title" v-model="form.title" class="form-control" required />
            </div>
            <div class="mb-3">
                <label for="full_name" class="form-label">Nombre completo</label>
                <input type="text" id="full_name" v-model="form.full_name" class="form-control" required />
            </div>
            <div class="mb-3">
                <label for="email" class="form-label">Correo electrónico</label>
                <input type="email" id="email" v-model="form.email" class="form-control" required />
            </div>
            <div class="mb-3">
                <label for="message" class="form-label">Cuerpo del mensaje</label>
                <textarea id="message" v-model="form.message" class="form-control" rows="5" maxlength="500" required></textarea>
                <div class="form-text">Máximo 500 caracteres.</div>
            </div>
            <!-- reCAPTCHA -->
            <div class="mb-3 d-flex justify-content-center">
                <div 
                    class="g-recaptcha" 
                    data-sitekey="6LclWYYqAAAAAIDb-lO_w9f3DYu6EtdAevW2IyZ6"
                    data-callback="onRecaptchaVerified"
                    data-expired-callback="onRecaptchaExpired"
                ></div>
            </div>
            <!-- Botón enviar -->
            <button
                type="submit"
                class="btn btn-primary w-100"
                :disabled="!recaptchaToken || isSubmitting"
            >
                {{ isSubmitting ? 'Enviando...' : 'Enviar' }}
            </button>

        </form>
    </div>
</template>

<script setup>
import { useContactStore } from '../stores/contact';
import { onMounted, reactive, ref } from 'vue';
import { storeToRefs } from 'pinia';

const store = useContactStore();
const { result} = storeToRefs(store);

const recaptchaToken = ref('');
const isSubmitting = ref(false);

const form = reactive({
    title: '',
    full_name: '',
    email: '',
    message: '',
});

// Definimos las funciones del recaptcha en el objeto window para que sean accesibles globalmente
onMounted(() => {
    window.onRecaptchaVerified = (token) => {
        recaptchaToken.value = token;
    };

    window.onRecaptchaExpired = () => {
        recaptchaToken.value = '';
    };
});

const waitForRecaptcha = () => {
    return new Promise((resolve, reject) => {
        const interval = setInterval(() => {
            if (window.grecaptcha) {
                clearInterval(interval); // Detenemos el intervalo cuando grecaptcha está listo
                resolve(window.grecaptcha); // Resolvemos la promesa con el objeto grecaptcha
            }
        }, 100); // Verifica cada 100ms

        // Opción para evitar loops infinitos (timeout después de 10 segundos)
        setTimeout(() => {
            clearInterval(interval);
            reject(new Error('reCAPTCHA client not loaded after timeout'));
        }, 10000);
    });
};

const resetRecaptcha = async () => {
    try {
        const grecaptcha = await waitForRecaptcha(); // Esperamos a que grecaptcha esté disponible
        grecaptcha.reset(); // Reseteamos reCAPTCHA
        console.log('reCAPTCHA reset successfully');
    } catch (error) {
        console.error(error.message);
    }
};

const handleSubmit = async () => {
    try {
        if (!recaptchaToken.value) {
            alert('Por favor, verifica el reCAPTCHA antes de enviar');
            return;
        }

        isSubmitting.value = true;
        await store.fetchMessage({
            ...form,
            recaptchaToken: recaptchaToken.value
        });
        
        // Reset form and recaptcha after successful submission
        if (result.value) {
            form.title = '';
            form.full_name = '';
            form.email = '';
            form.message = '';
            store.error = [];
            resetRecaptcha();
        }
    } catch (error) {
        console.error('Error al enviar el formulario:', error);
        alert('Hubo un error al enviar el formulario. Por favor, intenta nuevamente.');
        resetRecaptcha();
    } finally {
        isSubmitting.value = false;
    }
};

onMounted(() => {
    // Cargar el script de reCAPTCHA dinámicamente
    
    const script = document.createElement('script');
    script.src = 'https://www.google.com/recaptcha/api.js';
    script.async = true;
    script.defer = true;
    document.head.appendChild(script);
});
</script>

<style scoped>
.text-danger {
    font-size: 0.9rem;
}

#message {
    resize: none;
}
</style>