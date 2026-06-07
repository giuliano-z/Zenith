// Tipos del dominio AUTH. El contrato lo define el backend Django (apps/users).

/** Usuario básico. El backend aún no expone /me, así que en esta fase
 *  solo conocemos el email (lo capturamos del form de login). */
export interface User {
  email: string
}

/** Respuesta de POST /api/auth/login/ — Knox devuelve token + expiry. */
export interface AuthToken {
  token: string
  expiry: string
}

export interface LoginCredentials {
  email: string
  password: string
}
