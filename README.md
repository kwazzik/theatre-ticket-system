# Theatre Ticket System

Theatre Ticket System is a web application built with Django REST Framework (DRF) for managing theatre plays, performances, reservations, and tickets.

## Features

- Browse and manage plays, actors, genres  
- Create performances in specific theatre halls  
- Make reservations and assign tickets to specific seats  
- Track seat availability  
- User authentication and admin permissions  

## Requirements

- Python 3.x  
- Django (as specified in `requirements.txt`)  
- Django REST Framework  

## Installation

1. **Clone the repository**:

    ```bash
    git clone <repository-url>
    cd pc-components-store
    ```

2. **(Optional) Create and activate a virtual environment**:

    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3. **Install dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run migrations**:

    ```bash
    python manage.py migrate
    ```

5. **Run the development server**:

    ```bash
    python manage.py runserver
    ```

## Run with Docker (Optional)


1. Build the image:

    ```bash
    docker build -t theatre-ticket-system .
    ```

2. Run the container:

    ```bash
    docker run -p 8000:8000 theatre-ticket-system
    ```

3. Run migrations:

    ```bash
    docker run theatre-ticket-system python manage.py migrate
    ```

4. Create superuser:

    ```bash
    docker run -it theatre-ticket-system python manage.py createsuperuser
    ```

5. API will be available at:

    ```bash
    http://localhost:8000
    ```

---

## Usage

- Open your browser and go to `http://localhost:8000` (if running locally).  
- Use the DRF Browsable API or a REST client (Postman, Insomnia) to:  
  - List, create, update, and delete **plays**, **actors**, **genres**, **performances**, **theatre halls**, **reservations**, and **tickets**  
- Admin users can manage all resources via Django Admin at `http://localhost:8000/admin/`.  
- Regular users can create **reservations** and view their **tickets**.  
- Use token-based authentication to access protected endpoints.


---

## Test

You can use the following test account to log in and explore the application:

| Field                | Value             |
|----------------------|-------------------|
| **Username / email** | `admin@admin.com` |
| **Password**         | `admin12345`      |

---

## Notes

- Remember to set up your `SECRET_KEY` as an environment variable before running the project.
- Static and media files are configured as per Django defaults.
