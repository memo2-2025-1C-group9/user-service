// authService.js - Servicio para manejo de autenticación
import axios from 'axios';

// URL base de la API (ajusta esto a tu endpoint de API)
const API_URL = 'https://user-auth-service-mtoy.onrender.com/api/v1';

// Crear instancia de axios con configuración personalizada
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Accept': 'application/json, application/problem+json',
  }
});

// Interceptor para transformar respuestas de error
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log('Error original:', error);
    
    // Construir un objeto de error personalizado
    let customError = {
      mensaje: 'Error de conexión al servidor',
      statusCode: 500,
      detalles: null,
      original: error
    };
    
    // Si tenemos una respuesta del servidor
    if (error.response) {
      const { status, data } = error.response;
      
      // Los errores en formato Problem+JSON tendrán un campo 'detail'
      if (data && typeof data === 'object') {
        if (data.detail) {
          customError = {
            mensaje: data.detail,
            statusCode: status,
            detalles: data,
            original: error
          };
        } else if (data.message) {
          // Formato alternativo que algunas APIs usan
          customError = {
            mensaje: data.message,
            statusCode: status,
            detalles: data,
            original: error
          };
        }
      } else if (typeof data === 'string') {
        // Si el servidor devolvió un string directamente
        customError = {
          mensaje: data,
          statusCode: status,
          detalles: { texto: data },
          original: error
        };
      }
      
      // Añadir información categorizada para facilitar manejo en la UI
      customError.esErrorAutenticacion = status === 401 || status === 403;
      customError.esErrorValidacion = status === 400 || status === 422;
      customError.esErrorServidor = status >= 500;
    }
    
    console.log('Error personalizado:', customError);
    return Promise.reject(customError);
  }
);

/**
 * Función para iniciar sesión
 * @param {string} email - Correo electrónico del usuario
 * @param {string} password - Contraseña del usuario
 * @returns {Promise<Object>} - Promesa con el resultado del login
 */
export const login = async (email, password) => {
  try {
    // Preparar los datos en el formato que espera la API
    const formData = new FormData();
    formData.append('username', email);  // OAuth2 usa 'username' en vez de 'email'
    formData.append('password', password);
    
    // Enviar solicitud a la API
    const response = await apiClient.post('/token', formData, {
      headers: {
        // No incluir Content-Type para que el navegador lo configure automáticamente con los límites
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    
    const { access_token, token_type } = response.data;
    
    // Guardar el token en localStorage
    localStorage.setItem('token', access_token);
    localStorage.setItem('tokenType', token_type);
    
    return {
      exitoso: true,
      token: access_token,
      tipo: token_type,
      mensaje: 'Login exitoso'
    };
  } catch (error) {
    // Si el error es el objeto personalizado del interceptor
    return {
      exitoso: false,
      codigo: error.statusCode || 500,
      mensaje: error.mensaje || 'Error de conexión',
      detalles: error.detalles,
      esErrorAutenticacion: error.esErrorAutenticacion || false
    };
  }
};

// Ejemplo de uso del servicio en un componente React:
/*
import React, { useState } from 'react';
import { login } from './authService';

function LoginForm() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const resultado = await login(email, password);
    
    if (resultado.exitoso) {
      // Redireccionar a la página principal
      window.location.href = '/dashboard';
    } else {
      // Mostrar mensaje de error apropiado según el tipo de error
      if (resultado.esErrorAutenticacion) {
        setError('Usuario o contraseña incorrectos');
      } else if (resultado.codigo === 400) {
        setError('Datos de entrada inválidos');
      } else {
        setError(`Error: ${resultado.mensaje}`);
      }
      console.error('Detalles:', resultado.detalles);
    }
    
    setLoading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="error-alert">{error}</div>}
      
      <div className="form-group">
        <label>Email:</label>
        <input 
          type="email" 
          value={email} 
          onChange={(e) => setEmail(e.target.value)} 
          required 
        />
      </div>
      
      <div className="form-group">
        <label>Contraseña:</label>
        <input 
          type="password" 
          value={password} 
          onChange={(e) => setPassword(e.target.value)} 
          required 
        />
      </div>
      
      <button type="submit" disabled={loading}>
        {loading ? 'Cargando...' : 'Iniciar sesión'}
      </button>
    </form>
  );
}
*/ 