# FastAPI starter pack

Backend modular con PostgreSQL asíncrono, UUID, usuarios, perfiles de acceso, permisos,
sesiones revocables y respuestas uniformes. Python 3.12 o superior. Redis queda pendiente.

## Instalación

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Configura `DATABASE_URL` y copia la clave generada en `JWT_SECRET_KEY` del `.env`.
PostgreSQL debe estar encendido y la base de datos debe existir.

```powershell
alembic upgrade head
python -m scripts.create_superadmin
uvicorn app.main:app --reload
```

El script solicita la contraseña sin mostrarla y exige al menos 12 caracteres. Si ya tienes
tu superadmin, no vuelvas a crearlo. El acceso completo depende de `profile.code="superadmin"`;
los demás usuarios usan los permisos de su perfil.

Swagger está en `http://127.0.0.1:8000/docs`, con autorización persistente y formularios activos.

## Actualizar una instalación existente

```powershell
python -m pip install -r requirements-dev.txt
alembic upgrade head
```

La migración nueva crea `auth_sessions`. No borres las tablas ni uses `stamp base`.
Debes iniciar sesión nuevamente: los JWT viejos no incluyen el ID de sesión requerido.
Consulta [CHANGELOG.md](CHANGELOG.md) para ver qué se eliminó y por qué.

## Autenticación y sesiones

- `POST /api/v1/auth/register`: JSON con correo, username, nombres y contraseña.
  El perfil `user` se asigna en el servidor. No acepta campos administrativos.
- `POST /api/v1/auth/login`: formulario OAuth con `username` (también admite correo) y `password`.
- `POST /api/v1/auth/refresh`: JSON `{"refresh_token": "..."}`.
- `POST /api/v1/auth/logout`: header `Authorization: Bearer <access_token>`.

Login y refresh devuelven `access_token`, `refresh_token`, `token_type`, `expires_in` y `user`.
Al renovar, reemplaza **ambos tokens** por los nuevos: el refresh anterior deja de funcionar.
Coordina el frontend para que haya una sola renovación en curso por sesión.

El access token dura `ACCESS_TOKEN_EXPIRE_MINUTES`. La sesión vence de forma absoluta después
de `REFRESH_TOKEN_EXPIRE_DAYS`; renovar no extiende esa fecha. Logout invalida todos los access
tokens de esa sesión y su refresh, pero no las otras sesiones del mismo usuario.
Swagger conserva el access token al recargar, pero no renueva automáticamente el refresh.
Su botón Logout local no llama al endpoint: usa `POST /auth/logout` para revocar en el servidor.

Los JWT se comprueban contra la sesión en PostgreSQL en cada solicitud protegida. La tabla guarda
el hash del refresh token, nunca el token original. Los perfiles y permisos se consultan en vivo.

## Usuarios y permisos

| Método | Ruta bajo `/api/v1` | Acceso |
|---|---|---|
| GET/PATCH | `/users/me` | Usuario autenticado; PATCH solo nombres y apellidos |
| GET | `/users` y `/users/{id}` | `users.read` o superadmin |
| PATCH | `/users/{id}` | Superadmin; `profile_id` y/o `is_active` |
| GET | `/profiles` y `/profiles/{id}` | `profiles.read` o superadmin |
| POST | `/profiles` | Superadmin |
| GET | `/permissions` | `permissions.read` o superadmin |
| POST | `/profiles/{id}/permissions` | Superadmin; añade sin duplicar ni reemplazar |
| DELETE | `/profiles/{id}/permissions` | Superadmin; retira solo las asociaciones enviadas |

POST y DELETE de permisos reciben JSON `{"permission_ids": ["UUID", "UUID"]}`.
Repetir una adición o retirada no duplica ni afecta otras asociaciones. Añadir un permiso
inexistente rechaza toda la petición. Retirar uno no asignado no cambia nada.

Cambiar el perfil o estado de un usuario cierra sus sesiones. El perfil `superadmin` no se puede
asignar por la API y sus cuentas no se modifican con el PATCH administrativo: se gestionan por
consola. El script existente crea cuentas nuevas, no promueve cuentas existentes.

El frontend recibe `user.profile.code` y `user.permissions` al iniciar sesión y en `/users/me`:

```javascript
const puede = (codigo) =>
  user.profile.code === "superadmin" || user.permissions.includes(codigo);
```

Esto sirve para mostrar menús y botones. El backend comprueba la autorización por separado.

## Paginación y respuestas

Los listados aceptan `?page=1&page_size=20` (máximo 100) y devuelven:

```json
{
  "success": true,
  "message": "Usuarios obtenidos correctamente.",
  "data": {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20,
    "pages": 0
  }
}
```

Los errores mantienen el status HTTP real y el formato
`{"success": false, "message": "...", "data": null, "errors": []}`.
Mantén `DEBUG=false` para usar el handler JSON de errores inesperados. Los detalles internos
se registran en el servidor. Login/refresh usan el formato OAuth y `/health` sigue siendo un
health check mínimo sin dependencias.

## CORS

```dotenv
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

Añade los orígenes exactos de tu frontend, sin slash final. Se usan tokens Bearer y no cookies,
por lo que `allow_credentials` está desactivado. CORS también se aplica a errores 500.

## Añadir módulos

Cada módulo debe tener `__init__.py`. Los modelos en `app/modules/<modulo>/models.py` se descubren
automáticamente. Los routers se buscan en `router.py`, con una variable `router: APIRouter`.
Como se solicitó, si un router no existe, está vacío o falla, se omite y se registra el motivo.
Revisa los logs y Swagger: omitir un módulo no demuestra que ese módulo funcione.

Los modelos que heredan de `Base` generan `<tabla>.read/create/update/delete` al ejecutar
`alembic upgrade head`. La sincronización inserta los códigos faltantes y conserva IDs y
asignaciones. No asigna permisos a perfiles comunes ni elimina códigos antiguos.

```python
__permission_actions__ = ("read", "create", "update", "delete", "export")
# O bien, para excluir modelos internos:
__permission_actions__ = ()
```

Para cada modelo nuevo crea su migración y aplica `alembic upgrade head`. Protege los endpoints
con `require_permissions("recurso.accion")`; generar el catálogo no protege rutas por sí solo.

## Pruebas

```powershell
pytest -q
ruff check .
ruff format --check .
```

Por defecto usan SQLite en memoria y no tocan `DATABASE_URL`. Adaptan únicamente la lectura
de fechas UTC de sesiones para reproducir el comportamiento de PostgreSQL.

Para ejecutar también la prueba de renovación concurrente, crea una base exclusiva terminada
en `_test` y configura la variable de entorno en la terminal:

```powershell
$env:TEST_DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_starter_test"
pytest -q
```

Cada prueba usa un esquema aleatorio y lo elimina al terminar. No uses una base con datos reales.
GitHub Actions ejecuta las migraciones desde cero, su repetición, `alembic check` y las pruebas
con PostgreSQL 16. Redis, Celery y correo no se instalan ni arrancan en esta etapa.
