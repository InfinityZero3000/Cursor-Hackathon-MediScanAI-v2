// API configuration
const getApiUrl = () => {
  // Check if using Firebase Hosting
  const isFirebase = typeof window !== 'undefined' && (
    window.location.hostname.includes('firebaseapp.com') || 
    window.location.hostname.includes('web.app')
  );
  
  if (isFirebase) {
    // When using Firebase Hosting, use Vercel API or external API
    // TODO: Replace with your Vercel app URL or external API
    const vercelApiUrl = import.meta.env.VITE_API_URL || 'https://your-vercel-app.vercel.app/api';
    return vercelApiUrl;
  }
  
  // In production (Vercel), use relative path
  if (import.meta.env.PROD) {
    return '/api';
  }
  
  // In development, use localhost
  return 'http://localhost:5002/api';
};

export const API_URL = getApiUrl();

// Helper function to get full API endpoint URL
export const getApiEndpoint = (endpoint) => {
  const baseUrl = API_URL;
  // Remove leading slash from endpoint if present
  const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
  
  if (baseUrl.includes('cloudfunctions.net')) {
    // Firebase Functions - endpoint is the function name
    return `${baseUrl}/${cleanEndpoint}`;
  } else {
    // Vercel or localhost
    return `${baseUrl}/${cleanEndpoint}`;
  }
};

