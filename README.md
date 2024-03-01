# Bunk Mate - (Backend)

Many of us have faced the dilemma of wanting to take a day off from college for various reasons but hesitating due to the strict attendance requirements. Bunk Mate, a revolutionary app/website, is here to make your life easier by providing a convenient solution to track your classes and keep you informed about your attendance status.

## Features

- **Attendance Tracking:** Keep a record of your attended classes effortlessly.
  
- **Live Updates:** Get real-time updates on your remaining classes to meet the attendance target.

- **User-Friendly Interface:** An intuitive interface that makes attendance tracking a breeze.

## Tech Stack

- **Django Rest Framework:** Built on the powerful Django framework for a robust and scalable backend.

- **Redis:** Utilizing Redis for caching to enhance performance.

- **Celery:** Employing Celery for distributed task processing, ensuring efficient background task execution.

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

- **GET /api/users:** Get a list of users.
- **GET /api/user/{pk}/:** Get details of a specific user.
- **POST /api/register:** Register a new user.
- **POST /api/login:** User login.
- **POST /api/logout:** User logout.

### Model Management

- **POST /api/collection:** Create a new collection.
- **GET /api/collections:** Get a list of collections.
- **POST /api/collection_selector:** Select a collection.
- **POST /api/course_schedules/{course_id}:** Create a schedule for a specific course.
- **GET /api/schedules:** Get a list of schedules.
- **GET /api/schedule/{pk}:** Get details of a specific schedule.
- **GET /api/session/{pk}:** Get details of a specific session.
- **POST /api/schedule_selector:** Select a schedule.
- **GET /api/courses:** Get a list of courses.

### Query Endpoints

- **POST /api/datequery:** Query by date.
- **POST /api/statquery:** Statistical query.

Refer to the API documentation for detailed information on each endpoint.

## Contributing

We welcome contributions! If you have any ideas for improvement, open an issue or submit a pull request. 

## License

This project is licensed under the [MIT License](https://opensource.org/license/mit).

---

Feel free to reach out with any questions or feedback. Happy coding with Bunk Mate! 🚀
