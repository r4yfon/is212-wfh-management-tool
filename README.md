# IS212 AY2024/25 G3T2: WFH Management Tool

This project is a work-from-home management tool that consists of a backend built with Flask and a frontend built with Vue 3 using Vite.

## Project Description

WFH Management Tool is a comprehensive solution designed to manage work-from-home (WFH) schedules for employees. It consists of a backend built with Flask and a frontend developed using Vue 3 with Vite. The tool facilitates various functionalities such as employee management, WFH request handling, schedule viewing, and status logging.

### Key Features:

- Employee Management: Manage employee data including personal details and roles.
- WFH Requests: Employees can submit one-time or recurring WFH requests.
- Schedule Management: View and manage WFH schedules for employees.
- Request Handling: Approve, reject, or rescind WFH requests.
- Status Logging: Log and track the status changes of WFH requests.

## Prerequisites

- Node.js and npm
- Python 3.x
- MySQL

## Deployment

The project is deployed on Vercel, with the frontend and backend hosted on the platform. The database is managed using NeonDB, a serverless PostgreSQL database provider.

The deployed version of the application can be accessed via [https://is212-frontend.vercel.app/](https://is212-frontend.vercel.app/).

## Database

The project uses a MySQL database with multiple tables to store employee data, request data, and status logs. The database schema supports the microservices architecture adopted by the project.

- `employee`: Stores employee data such as name, email, and phone number. The dummy data in this table was provided by the teaching team.
- `request`: Stores request data such as request ID, employee ID, request date, and request status.
- `request_dates`: Stores the dates for work-from-home requests, in consideration of one-time and recurring requests.
- `status_log`: Stores status log data such as request ID, employee ID, request date, and status change.

## Backend

The backend is composed of multiple Flask applications, each dedicated to a specific functionality such as managing employees, handling requests, and logging status changes.

- `employee.py`: Manages employee data.
- `request.py`: Handles requests for work-from-home.
- `request_dates.py`: Manages the dates for work-from-home requests.
- `view_schedule.py`: Provides the schedule view for employees.
- `view_requests.py`: Allows employees to view their own requests.
- `reject_requests.py`: Handles the rejection of requests.
- `status_log.py`: Logs the status changes of requests.

## Frontend

The frontend is built with Vue 3 and Vite, utilising libraries like Vuetify for UI components and PrimeVue for additional UI components. The frontend provides an intuitive interface for employees to manage their WFH schedules and for managers to oversee and approve requests.

## Project Setup

1. Clone the repository:

   ```sh
   git clone https://github.com/r4yfon/is212-wfh-management-tool.git
   ```

### Database Setup

2. Run the SQL script in the `backend/SQL` directory to create the database and tables.

### Backend Setup

3. Navigate to the backend directory:

   ```sh
   cd backend
   ```

4. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

5. On Windows, run the `run_flask.bat` script:

   ```sh
   run_flask.bat
   ```

6. Otherwise, run each Flask application individually:
   ```sh
   python employee.py
   python request.py
   python request_dates.py
   python view_schedule.py
   python view_requests.py
   python reject_requests.py
   python status_log.py
   ```

### Frontend Setup

7. Navigate to the `frontend` directory:

   ```sh
   cd ../frontend
   ```

8. Install the dependencies:

   ```sh
   npm install
   ```

9. Compile and Hot-Reload for Development:

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
