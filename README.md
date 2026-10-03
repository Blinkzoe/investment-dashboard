# Investment Dashboard

Personal investment portfolio dashboard.

## Architecture

- Frontend: React + TypeScript
- Backend: FastAPI + Python
- Database: PostgreSQL
- Migrations: Alembic
- Containers: Docker Compose

## Security

Secrets are provided through environment variables.

Never commit:

- `.env`
- passwords
- API keys
- JWT secrets
- private keys
- database dumps
- personal financial data

Use `.env.example` as the configuration template.

## Development

Copy the environment template:

```bash
cp .env.example .env