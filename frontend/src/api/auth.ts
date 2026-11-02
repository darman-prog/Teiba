import { requestJson } from './client';
import type { SessionResponse } from '../types/api';

// Cliente de sesión: cookie httpOnly, sin guardar token en JS.
export function fetchMe() {
  return requestJson<SessionResponse>('/api/auth/me', { timeoutMs: 8000 });
}

export function postLogin(correo: string, contrasena: string) {
  return requestJson<SessionResponse>('/api/auth/login', {
    method: 'POST',
    body: { correo, contrasena },
    timeoutMs: 15000,
  });
}

export function postLogout() {
  return requestJson<null>('/api/auth/logout', { method: 'POST', timeoutMs: 8000 });
}
