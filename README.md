# Лабораторная работа: CI/CD

К проекту из первой лабы (Docker + FastAPI + PostgreSQL) добавлены тесты, линтер и пайплайн в GitHub Actions, плюс публикация образа на Docker Hub.

---

## Что сделано по заданию (кратко)

| Требование | Где смотреть |
|-------------|----------------|
| Unit / интеграционные тесты | `app/tests/`, pytest |
| Линтер | Ruff, конфиг `app/pyproject.toml` |
| Пайплайн на PR / push | `.github/workflows/ci.yml` |
| Job **build** — приложение «собирается» (зависимости + импорт) | workflow, job `build` |
| Job **lint** | `python -m ruff check src tests` |
| Job **test** + coverage, порог **50%** | pytest `--cov-fail-under=50`, отчёты как артефакты |
| Job **docker_build** | `docker build` из `./app` |
| Job **docker_push** в Docker Hub отдельно, после успешных шагов | job `docker_push`, образ `naxeel/todo-api` |
| Тег образа от коммита | тег `:latest` и `:<7 символов SHA>` |
| Секреты не в коде | GitHub Secrets `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` |
| Пайплайн падает при ошибках | без `continue-on-error`: сборка, линтер, тесты, coverage ниже порога 50% |

## Стек и структура

- Язык: Python 3.12  
- API: FastAPI, БД: PostgreSQL 16  
- Тесты: pytest + httpx (через TestClient), coverage  
- Линтер: ruff  
- CI: GitHub Actions  

Папки: `app/` (код, Dockerfile приложения, тесты), `db/` (Dockerfile БД, `init.sql`), в корне `docker-compose.yml`, `.env.example`.

---

## Запуск через Docker

1. Скопировать `.env.example` в `.env` и при необходимости поправить переменные (пароли в репозиторий не кладём, `.env` в `.gitignore`).

2. В корне репозитория:

```bash
docker compose up --build
```

3. Проверка: Swagger `http://localhost:8000/docs`, здоровье сервиса `http://localhost:8000/health`.

Снаружи открыт только порт приложения (8000). У PostgreSQL в compose **нет** `ports` на хост. Данные БД в volume `db_data`.

---

## Локальный запуск тестов и линтера (без полного compose)

Нужен PostgreSQL на `127.0.0.1:5432` с логином `ci`, паролем `ci`, базой `ci` (так в `app/tests/conftest.py` по умолчанию). Пример:

```bash
docker run -d --rm --name pg-ci-test -p 5432:5432 -e POSTGRES_USER=ci -e POSTGRES_PASSWORD=ci -e POSTGRES_DB=ci postgres:16
```

Дальше из папки `app/`:

```bash
cd app
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m ruff check src tests
python -m pytest tests --cov=src --cov-report=term-missing --cov-report=html:htmlcov --cov-fail-under=50
```

Остановить тестовый Postgres: `docker stop pg-ci-test`.

---

## CI/CD на GitHub

Файл: `.github/workflows/ci.yml`.

Запуск: **pull request**, **push** в ветки `main` / `master`, вручную: **Actions → CI → Run workflow**.

Этапы (jobs):

1. **build** — установка зависимостей из `app/requirements.txt` и dev-зависимостей, проверка что модуль приложения импортируется.  
2. **lint** — Ruff по `app/src` и `app/tests`.  
3. **test** — pytest с покрытием кода в `src`, порог **50%**; в артефакты кладутся HTML-отчёт coverage и `coverage.xml`; в лог печатается строка с процентом из XML.  
4. **docker_build** — сборка образа приложения (`Dockerfile` в `app/`).  
5. **docker_push** — вход в Docker Hub по секретам и push образа **`naxeel/todo-api`** с тегами **`latest`** и **короткий SHA** (первые 7 символов коммита; для PR берётся SHA из головы PR).

Если что-то из шагов 1–4 падает, дальше пайплайн не идёт. Линтер и тесты настроены так, что «зелёный» прогон — реальный, не заглушка.

### Секреты в репозитории GitHub

Settings → Secrets and variables → Actions:

- `DOCKERHUB_USERNAME` — Ваш логин на Docker Hub
- `DOCKERHUB_TOKEN` — Personal Access Token с Docker Hub 

---

## Где лежат конфиги

- Линтер, pytest, порог coverage в конфиге: `app/pyproject.toml`  
- Dev-зависимости: `app/requirements-dev.txt`  
- Пайплайн: `.github/workflows/ci.yml`


