# e_commerce_backend
#  E-Commerce Backend API

A modular and scalable **E-Commerce REST API** built using **FastAPI**, **SQLAlchemy**, **Alembic**, and **JWT-based Authentication**.

---

## Features

- User registration, login, and role-based access (admin/user)
- JWT token-based authentication
- Product management (CRUD by admin)
- Cart management
- Checkout system with simulated payments
- Order history
- Password reset via token
- Configurable environment using `pydantic-settings`

---

## Tech Stack

- **Backend**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Database Migration**: [Alembic](https://alembic.sqlalchemy.org/)
- **Auth**: [Python-Jose](https://python-jose.readthedocs.io/en/latest/) (JWT)
- **Database**: PostgreSQL (can be swapped with SQLite for local use)
- **Validation**: [Pydantic](https://docs.pydantic.dev/latest/)

---

##  Project Structure
"""
├── app/
│   ├── core/
│   │   ├── config.py, database.py, deps.py
│   │
│   ├── auth/
│   │   ├── models.py, schemas.py, routes.py, utils.py
│   │
│   ├── products/
│   │   ├── models.py, schemas.py, routes.py, public_routes.py
│   │
│   ├── cart/
│   │   ├── models.py, schemas.py, routes.py
│   │
│   ├── checkout/
│   │   ├── schemas.py, routes.py
│   │
│   ├── orders/
│   │   ├── models.py, schemas.py, routes.py
│
├── alembic.ini
├── main.py
├── requirements.txt
└── README.md
"""
