# Cambios de esta actualización

## Implementado

- Sesiones en PostgreSQL con refresh tokens opacos: solo se guarda su hash SHA-256.
- Rotación del refresh token bajo bloqueo de fila; cada token de renovación se acepta una vez.
- Logout que revoca tanto el refresh como los access tokens de esa sesión.
- Vencimiento absoluto de sesión controlado por `REFRESH_TOKEN_EXPIRE_DAYS`.
- Administración de usuarios: listado y detalle protegidos, cambio de perfil y activación/desactivación.
- Cambiar perfil o estado revoca las sesiones anteriores, incluso tras reactivar la cuenta.
- Retirada de permisos idempotente sin eliminar el catálogo ni otras asociaciones.
- CORS por lista explícita de orígenes, incluidos errores 500.
- Paginación con `items`, `total`, `page`, `page_size` y `pages` en los tres listados.
- Pruebas HTTP y de persistencia; CI con PostgreSQL para migraciones y concurrencia.

## Correcciones

- `GET /users` ya no expone usuarios sin autenticación; exige `users.read`.
- El perfil resumido incluye `code`, necesario para reconocer `superadmin` en el frontend.
- `CurrentUser` queda definido antes de las dependencias que lo utilizan.
- El listado de usuarios tiene orden estable para paginar.
- Se recargan las relaciones cuando se necesitan datos actualizados de perfil/permisos.
- Los nombres de los dos archivos iniciales de migración estaban intercambiados. Se alinearon
  con sus IDs internos, conservando los IDs, el encadenamiento y las operaciones existentes.

## Eliminado y motivo

- `ProfileRepository.create_permission`: el catálogo ahora lo genera la sincronización de modelos.
- `ProfileRepository.replace_permissions`: sustituía toda la lista; el comportamiento elegido es
  añadir y retirar asociaciones de forma independiente.
- Archivos vacíos de `app/worker/`, `app/infraestructure/` y `app/core/logging.py`: no implementaban
  ninguna función y daban la impresión de que Celery, Redis o correo ya estaban conectados.
- Dependencias `redis` y `aiosmtplib`, y configuración `REDIS_URL`: no tenían ningún consumidor.
  Redis queda para una fase posterior, como se pidió.
- Imports sin uso y formato inconsistente, mediante Ruff.

## Compatibilidad

- El superadmin sigue siendo el usuario cuyo perfil tiene `code="superadmin"`. No se añadió
  `is_superuser` ni se requiere crear de nuevo las cuentas existentes.
- Hay una nueva migración: `d72a48f0e196`. Ejecutar `alembic upgrade head`, sin `stamp` ni resets.
- Los JWT anteriores a esta actualización no contienen `sid`: hay que iniciar sesión otra vez.
- Los listados usan `page` y `page_size` en lugar de `offset` y `limit`.
- Login/refresh conservan el formato OAuth que usa Swagger; las demás respuestas mantienen
  el sobre `success`, `message` y `data`.
- Se conservan los `__init__.py` vacíos: definen los paquetes y permiten descubrir los módulos.
