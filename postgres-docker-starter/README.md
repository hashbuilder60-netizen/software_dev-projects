# Postgres Docker Starter

Production-style local database setup with Docker Compose.

## Run

```powershell
cd postgres-docker-starter
docker compose up -d
```

Services:
- PostgreSQL on `localhost:5432`
- Adminer on `http://localhost:8080`

Default DB credentials:
- DB: `appdb`
- User: `appuser`
- Password: `apppass`