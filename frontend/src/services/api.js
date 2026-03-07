import axios from 'axios';

// La URL se saca de las variables de entorno para Vite (VITE_API_URL)
const envUrl = import.meta.env.VITE_API_URL;
console.log('API URL detectada:', envUrl);

const BASE_URL = envUrl || 'http://localhost:8000/api';

// Derivamos la URL de estáticos (sacamos el /api del final)
export const STATIC_URL = BASE_URL.replace(/\/api$/, '') + '/static';

const api = axios.create({
    baseURL: BASE_URL,
});


export default api;

