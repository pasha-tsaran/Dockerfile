# Калькулятор: Flask + фронтенд + Docker Compose

Два сервиса работают в общей сети `app-network`:

- `backend` — Flask API в образе `paveltsaran/python-docker-test:latest`, порт 8000 внутри сети.
- `frontend` — веб-интерфейс и Nginx, доступный на http://localhost:8080.

Браузер отправляет запросы на `/api/` того же сайта. Nginx передаёт их на
`http://backend:8000` внутри сети Compose. Имя `backend` разрешается средствами
Docker. Публиковать порт бэкенда и настраивать CORS не требуется.

## Сборка и запуск

Запустите Docker Desktop в режиме Linux-контейнеров. В папке проекта выполните:

```powershell
docker compose up --build -d
```

Команда пересоберёт имеющийся образ Python с Flask, соберёт фронтенд и запустит
оба сервиса. Фронтенд стартует после успешной проверки здоровья бэкенда.
При первой сборке нужен интернет для загрузки образов и Python-зависимостей.

Откройте http://localhost:8080, введите два числа, выберите сложение или вычитание
и нажмите «Вычислить». На странице появятся результат и JSON-ответ Flask.
Отдельно отображаются доступность бэкенда и имя его хоста.

Если порт 8080 занят, в PowerShell задайте другой порт перед запуском:

```powershell
$env:FRONTEND_PORT = "8081"
docker compose up --build -d
```

Теперь интерфейс доступен на http://localhost:8081.

## Проверка API через фронтенд

```powershell
Invoke-RestMethod http://localhost:8080/api/health

Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/calculate -ContentType "application/json" -Body '{"a":12,"b":5,"operation":"add"}'

Invoke-RestMethod -Method Post -Uri http://localhost:8080/api/calculate -ContentType "application/json" -Body '{"a":12,"b":5,"operation":"subtract"}'
```

Результаты: `17` и `7`. В ответе также есть поля `a`, `b`, `operation`, `hostname`.
API принимает числа, включая отрицательные и дробные; операция — `add` или
`subtract`. Некорректный запрос возвращает HTTP 400 и JSON с полем `error`.
Арифметика использует числа с плавающей точкой: например, для `0.1 + 0.2`
возможен результат `0.30000000000000004`.

## Состояние, логи и остановка

```powershell
docker compose ps
docker compose logs -f
docker compose down
```

Последняя команда удалит контейнеры и сеть проекта. Образы останутся.
После изменения кода повторите `docker compose up --build -d`.

## Docker Hub

Docker Hub username: `PavelTsaran`, namespace для тегов: `paveltsaran`.
Репозиторий бэкенда: [paveltsaran/python-docker-test](https://hub.docker.com/r/paveltsaran/python-docker-test).

Для следующей публикации изменений:

```powershell
docker login
docker compose build backend
docker compose push backend
```

Загрузка образа и отдельный запуск бэкенда:

```powershell
docker pull paveltsaran/python-docker-test:latest
docker run --rm -p 127.0.0.1:8000:8000 paveltsaran/python-docker-test:latest
```

Публикация образа: [официальная инструкция Docker](https://docs.docker.com/docker-hub/repos/manage/hub-images/push/).

## Бэкенд без Docker

При установленном Python 3.12 или новее:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest -v
.\.venv\Scripts\python.exe app.py
```

Flask будет доступен на http://localhost:8000. Для остановки нажмите `Ctrl+C`.
В контейнере приложение запускается через Gunicorn. `GET /` и `GET /health`
сохранены для проверки бэкенда; веб-интерфейс обслуживает отдельный сервис.

Документация: [сеть Compose](https://docs.docker.com/compose/how-tos/networking/),
[Flask](https://flask.palletsprojects.com/en/stable/quickstart/),
[проксирование Nginx](https://nginx.org/en/docs/http/ngx_http_proxy_module.html).
