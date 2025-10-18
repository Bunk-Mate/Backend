# Bunk Mate - (Backend)

This repository contains the source code and documentation for the bunkmate backend.

## Tech Stack

- **Django Rest Framework:** For serving the main API.
- **Celery:** Celery is used for distributed task processing, here it is used for the resource intensive process of creating hundreds of sessions for a certain timetable.
- **Redis:** For message brokering between djano and celery.
- **PostgreSQL:** Database to store user data.

## Getting Started

The recommended way to setup the bunkmate backend is to use the docker compose file, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/Bunk-Mate/backend
   ```

2. Set up env:

   ```bash
   cp .env.sample .env
   ```

3. Run the docker compose file (this will setup everything for you, including celery, postgres and redis):

   ```python
   docker compose up
   ```

The backend server will be up and running at `http://localhost:8000/`.

### Using Bruno Collections

This repository has a [bruno](https://www.usebruno.com/) collection checked in under `/bruno` which you can open using the app for testing out the different API endpoints. Start from the register/login requests to populate the `auth-token` variable which is required for the other requests.

## Roadmap
- [x] Implement better authentication
- [x] Set up sentry
- [ ] Refactor codebase
- [x] Set up logging and remove print statements
- [ ] Implement **ranked bunking**
- [ ] Test out timetable autodetection from images

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit).

---
