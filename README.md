# FastAPI Starter

Base reutilizable con usuarios, perfiles, permisos y sesiones. Python 3.12+ y PostgreSQL.
Comandos para **PowerShell**, desde la raíz del proyecto.

## 1. Preparar el entorno — solo la primera vez

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Edita `.env`:

- `DATABASE_URL`: tu usuario, contraseña y nombre de base de PostgreSQL.
- `JWT_SECRET_KEY`: pega la clave que generó el último comando.
- `CORS_ORIGINS`: los orígenes de tu frontend, por ejemplo `["http://localhost:5173"]`.
- Mantén `DEBUG=false`.

## 2. Crear la base de datos

En pgAdmin, crea la base indicada en `DATABASE_URL`. Por ejemplo:

```sql
CREATE DATABASE fastapi_starter;
```

PostgreSQL debe estar encendido. Alembic crea las tablas, no la base de datos.

## 3. Crear las tablas y los permisos

```powershell
python -m alembic upgrade head
```

Este paso va **antes de arrancar la API**. También crea el perfil predeterminado y
sincroniza los permisos. Puedes repetirlo: solo aplica las migraciones pendientes.

## 4. Crear tu superadmin — solo la primera vez

```powershell
python -m scripts.create_superadmin
```

Introduce sus datos y una contraseña de al menos 12 caracteres. El superadmin tiene
acceso completo por su perfil. Si ya existe, no necesitas crearlo nuevamente.

## 5. Arrancar la API

```powershell
python -m uvicorn app.main:app --reload
```

Abre **http://127.0.0.1:8000/docs** y entra desde **Authorize**.
Para detenerla: `Ctrl+C`.

## Para trabajar otro día

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

## Después de actualizar el código

Detén la API y ejecuta, con el entorno activado:

```powershell
python -m pip install -r requirements-dev.txt
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Conserva tu `.env`. Si aparece una tabla nueva, aplica su migración antes de usarla.

## Cuando agregues o cambies modelos

```powershell
python -m alembic revision --autogenerate -m "describe el cambio"
python -m alembic upgrade head
```

Revisa la migración generada antes de aplicarla. Los modelos del módulo deben estar
en `models.py` y su carpeta debe tener `__init__.py`. Los permisos se sincronizan con el upgrade.

## Pruebas

```powershell
python -m pytest -q
```

Las pruebas locales usan una base en memoria. GitHub Actions también prueba con PostgreSQL,
incluidas las migraciones y la renovación concurrente de tokens.

Redis queda para después; las sesiones actuales se guardan en PostgreSQL.
