# Bunk Mate - (Backend)

This repository contains the source code and documentation for the attendence tracker backend

## Tech Stack

- **Django Rest Framework:** Built on the powerful Django framework for a robust and scalable backend.

- **Redis:** Utilizes Redis for message brokering between djano and celery.

- **Celery:** Celery is used for distributed task processing, here it is used for the resource intensive process of creating hundreds of sessions for a certain timetable.

- **PostgreSQL:** A reliable and scalable database to store and manage data efficiently.

## Getting Started

To get started with the Bunk Mate backend, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Bunk-Mate/backend
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.creds` file following this template:
   ```bash
   DBNAME=
   DBHOST=
   DBUSER=
   DBPASS=
   CACHELOCATION=
   BROKERLOCATION=
   SECRET_KEY=
   ```
   * `CACHELOCATION` and `BROKERLOCATION` correspond to the urls of the redis databases
   * This env file is used for a local development environment, for production include the environment variable `WEBSITE_HOSTNAME` which is set to the domain of the website.
3. Set up the database:

   ```bash
   python manage.py migrate
   ```

4. Run the development server:

   ```bash
   python manage.py runserver
   ```

The backend server will be up and running at `http://localhost:8000/`.

## API Endpoints

### User Management

- **POST /register:** Register a new user.
- **POST /login:** User login, returns the token of the user.
- **POST /logout:** User logout.

### Model Management

- **POST /collection:** Create a new collection.
- **GET /collections:** Get a list of all the collections.
- **POST /collection_selector:** Select a particular collection to copy to the user.
- **GET /courses:** Get a list of courses that the user has.
- **POST /courses:** Create a new course.
- **GET /course_schedules/{course_id}:** Gets a list of schedules under a particular course.
- **POST /course_schedules/{course_id}:** Create a schedule for a specific course.
- **GET /schedules:** Get a list of all the schedules that the user has.
- **GET /schedule/{pk}:** Get details of a specific schedule.
- **GET /session/{pk}:** Get details of a specific session.
- **PATCH /session/{pk}:** Update details of a specific session.
- **POST /schedule_selector:** Select a schedule for a particular date.

### Query Endpoints

- **POST /datequery:** Query which all session are there today.
- **POST /statquery:** Get statistics about every course.

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit).

---
