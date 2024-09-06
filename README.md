# Bunk Mate - (Backend)

This repository contains the source code and documentation for the attendence tracker backend

## Tech Stack

- **Django Rest Framework:** For the building the main API.
- **Celery:** Celery is used for distributed task processing, here it is used for the resource intensive process of creating hundreds of sessions for a certain timetable.
- **Redis:** For message brokering between djano and celery.
- **PostgreSQL:** Database to store user data.

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
   * `CACHELOCATION` and `BROKERLOCATION` correspond to the urls of the redis databases.
   * This env file is used for a local development environment, for production - 
       - Set the environment variable `WEBSITE_HOSTNAME` to the domain of the website.
       - Load the above listed variables into the environment using platform specific methods.
3. Set up the database:

   ```bash
   python manage.py migrate
   ```

4. Run the development server:

   ```bash
   python manage.py runserver
   ```

The backend server will be up and running at `http://localhost:8000/`.

## Roadmap
- [ ] Implement better authentication
- [ ] Set up sentry
- [ ] Refactor codebase
- [ ] Set up logging and remove print statements
- [ ] Implement **ranked bunking**
- [ ] Test out timetable autodetection from images

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit).

---
