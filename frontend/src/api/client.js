const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

async function request(path, options = {}) {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 30_000)
  try {
    const response = await fetch(`${apiBaseUrl}${path}`, { ...options, credentials: 'include', signal: controller.signal, headers: { 'Content-Type': 'application/json', ...options.headers } })
    const body = await response.json().catch(() => ({}))
    if (!response.ok) {
      if (response.status === 401) window.dispatchEvent(new Event('forgeai:unauthorized'))
      const error = new Error(body?.error?.message || `Request failed with status ${response.status}`)
      error.status = response.status
      throw error
    }
    return body
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The request timed out. Try a smaller repository or run the analysis again.')
    if (error instanceof TypeError) throw new Error('The API is unavailable. Check the backend URL and try again.')
    throw error
  } finally { window.clearTimeout(timeout) }
}

export async function getHealth() {
  return request('/api/v1/health')
}

export function getJson(path) { return request(path) }

export function postJson(path, body) { return request(path, { method: 'POST', body: JSON.stringify(body) }) }

export function getCurrentUser() { return request('/api/auth/me') }

export function registerUser(body) { return request('/api/auth/register', { method: 'POST', body: JSON.stringify(body) }) }

export function loginUser(body) { return request('/api/auth/login', { method: 'POST', body: JSON.stringify(body) }) }

export function logoutUser() { return request('/api/auth/logout', { method: 'POST' }) }
