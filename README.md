# IS212 AY2024/25 G3T2: WFH Management Tool

This project is a work-from-home management tool that consists of a backend built with Flask and a frontend built with Vue 3 using Vite.

## Deployed version

We deployed the Vue frontend and Flask backend to Vercel, a cloud platform for web development. Our database is hosted on NeonDB, a serverless PostgreSQL database provider.

The deployed version of the tool can be accessed via [https://is212-frontend.vercel.app/](https://is212-frontend.vercel.app/).

## Database

The database is a MySQL database, with multiple tables for employee data, request data, and status log data given the microservices architecture our project adopts:

- `employee`: Stores employee data such as name, email, and phone number. The dummy data in this table was provided by the teaching team.
- `request`: Stores request data such as request ID, employee ID, request date, and request status.
- `request_dates`: Stores the dates for work-from-home requests, in consideration of one-time and recurring requests.
- `status_log`: Stores status log data such as request ID, employee ID, request date, and status change.

### Setting Up the Database

1. Run the SQL script in the `SQL` directory to create the database and tables.

## Backend

The backend consists of multiple Flask applications, each serving a specific purpose. The applications are:

- `employee.py`: Manages employee data.
- `request.py`: Handles requests for work-from-home.
- `request_dates.py`: Manages the dates for work-from-home requests.
- `view_schedule.py`: Provides the schedule view for employees.
- `view_requests.py`: Allows employees to view their own requests.
- `reject_requests.py`: Handles the rejection of requests.
- `status_log.py`: Logs the status changes of requests.

### Setting Up the Backend

1. Navigate to the backend directory:

   ```sh
   cd backend
   ```

2. Install the required Python packages:

   ```sh
   pip install -r requirements.txt
   ```

3. On Windows, run the `run_flask.bat` script:

   ```sh
   run_flask.bat
   ```

4. Otherwise, run each Flask application individually:
   ```sh
   python employee.py
   python request.py
   python request_dates.py
   python view_schedule.py
   python view_requests.py
   python reject_requests.py
   python status_log.py
   ```

## Frontend

The frontend is built with Vue 3 and Vite. It uses various libraries such as Vuetify for UI components and PrimeVue for additional UI elements.

### Project Setup

1. Navigate to the frontend directory:

   ```sh
   cd frontend
   ```

2. Install the required npm packages:
   ```sh
   npm install
   ```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

### Lint with [ESLint](https://eslint.org/)

```sh
npm run lint
```
