export function getBaseUrl() {
  if (typeof window !== 'undefined') return '';
  const baseUrl = process.env.BASE_URL;
  if (baseUrl) return `https://${baseUrl}`;
  return 'http://localhost:5000'; // Default to localhost
}


