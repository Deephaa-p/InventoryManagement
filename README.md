This project includes a frontend and a Django backend, with PostgreSQL and Redis handled via Docker Compose.

To get started, clone the repository and follow the instructions below.

---

## 🛠️ Setup Instructions

- The `frontend` folder contains the frontend code.
- The `backend` folder contains the Django backend code.
- From the project root (which contains `docker-compose.yml`), run:

  ```bash
  docker-compose up --build

- to run backend
- create virtual environment, install dependencies , create env file, make db migrations
- sample credential
- ENGINE=django.db.backends.postgresql
DB_NAME=""
DB_USER=""
DB_PASSWORD=""
DB_HOST=""
DB_PORT=""

- to navigate to the UI run localhost:3000 on browser
