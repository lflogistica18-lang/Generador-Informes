import axios from 'axios';

// La URL se saca de las variables de entorno para Vite (VITE_API_URL)
const envUrl = import.meta.env.VITE_API_URL;
console.log('DEBUG [api.js] - VITE_API_URL:', envUrl);

// Si no hay envUrl, usamos localhost
const BASE_URL = envUrl || 'http://localhost:8000/api';

// IMPORTANTE: Para que axios combine correctamente las rutas relativas,
// el baseURL debería terminar en slash si vamos a usar rutas sin slash.
const finalBaseURL = BASE_URL.endsWith('/') ? BASE_URL : `${BASE_URL}/`;
console.log('DEBUG [api.js] - Final baseURL:', finalBaseURL);

// Derivamos la URL de estáticos (sacamos el /api del final)
export const STATIC_URL = BASE_URL.replace(/\/api\/?$/, '') + '/static';

const api = axios.create({
    baseURL: finalBaseURL,
});



export default api;

