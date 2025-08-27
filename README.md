# MiniLink

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111.1-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red?logo=sqlalchemy)
![Pydantic](https://img.shields.io/badge/Pydantic-2.8.2-lightgrey)
![Pytest](https://img.shields.io/badge/pytest-8.3.2-yellow)
![MkDocs](https://img.shields.io/badge/MkDocs-1.6.1-black?logo=markdown)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

## 📖 Overview
**MiniLink** is a lightweight **URL shortening service** built with FastAPI.  
It provides a secure RESTful API with authentication, user management, and short URL creation features.  

## ✨ Features
- 🔐 **JWT Authentication** – secure token-based access
- 👤 **User Management** – registration, login, profile access
- ✅ **URL Management**
  - Create short links
  - Delete links
  - Update links
  - List user-specific links
- 📦 **Dockerized Setup** – easy deployment with Docker

## 🛠️ Tech Stack

| Layer         | Tool / Tech             |
|---------------|-------------------------|
| **Language**  | Python 3.10             |
| **Framework** | FastAPI                 |
| **Database**  | PostgreSQL              |
| **ORM**       | SQLAlchemy (asyncio)    |
| **Container** | Docker                  |
| **Testing**   | Pytest                  |
| **Docs**      | MkDocs + terminal theme |

## 📚 Documentation
The API documentation is available via **GitHub Pages**, generated with **MkDocs**.  
It includes detailed explanations of all endpoints, authentication flow, and request/response examples.  

🔗 [View Full Documentation](https://rastr-0.github.io/MiniLink/)

## 🚀 Getting Started
Clone the repository and run the project locally with Docker:

```bash
git clone https://github.com/rastr-0/minilink.git
cd MiniLink
docker-compose up --build
