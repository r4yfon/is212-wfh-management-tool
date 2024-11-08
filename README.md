# IS212 AY2024/25 G3T2: WFH Management Tool

This project is a work-from-home management tool that consists of a backend built with Flask and a frontend built with Vue 3 using Vite.

## Project Description

WFH Management Tool is a comprehensive solution designed to manage work-from-home (WFH) schedules for employees. It consists of a backend built with Flask and a frontend developed using Vue 3 with Vite. The tool facilitates various functionalities such as employee management, WFH request handling, schedule viewing, and status logging.

## Prerequisites

- Node.js and npm
- Python 3.x
- MySQL

## Key Features

### For All Users (Employees)

- View own schedule (weekly, daily)
- Apply for WFH request (one-time or recurring)
  - If employee already has a request for a specific shift (AM/PM/Full) for a day, they cannot apply for the same or overlapping shift
  - e.g., If Sirirat is working from home on 08 November 2024 for the PM shift, she cannot apply for another WFH request on 08 November 2024 for the PM or Full shift, but can apply to WFH for the AM shift
- View WFH requests made by oneself
- Withdraw a WFH request (only if request's status is "Pending approval" or "Approved")
- WFH requests will have one of the following statuses:
  - "Pending approval": when employee first makes a request, it needs to be approved by their direct superior
    - For CEO Jack Sim, his requests will be automatically approved
  - "Approved": WFH request is approved by employee's direct superior
  - "Withdrawn": employee makes a WFH request, but withdraws it afterwards
    - If WFH request has not yet been approved by direct superior, i.e., current status is "Pending approval", request will be withdrawn automatically without requiring approval from direct superior
    - If WFH request has already been approved by direct superior, i.e., current status is "Approved", withdrawal will need to be approved by direct superior again (new status is "Pending withdrawal")
  - "Rejected": WFH request is rejected by direct superior
  - "Rescinded": WFH request was previously approved by direct superior, but superior changes their mind and now wants that subordinate to report back to office for that day

### HR & Management (Role 1)

- View work arrangements by department (In Office, WFH - AM, WFH - PM, WFH - Full)
- Easily see when the attendance rate of a department in office on a particular day is below 50%
- Approve or reject work-from-home requests made by their direct subordinates
- Rescind previously-approved WFH requests made by their direct subordinates
- Given that a request has already been approved, when the direct subordinate withdraws a request, HR and Management can approve the request (request's status becomes "Withdrawn") or reject it (status goes back to "Approved")

### Director (Role 1)

- View the work arrangements of the teams of the managers under a director (In Office, WFH - AM, WFH - PM, WFH - Full)
- Approve or reject work-from-home requests made by their direct subordinates
- Rescind previously-approved WFH requests made by their direct subordinates
- Easily see when the attendance rate of a particular team in office on a particular day is below 50%
- Given that a request has already been approved, when the direct subordinate withdraws a request, HR and Management can approve the request (request's status becomes "Withdrawn") or reject it (status goes back to "Approved")

### Manager (Role 3)

- View the work arrangements of the team under oneself (In Office, WFH - AM, WFH - PM, WFH - Full)
- Approve or reject work-from-home requests within their team (direct subordinates)
- Rescind previously-approved WFH requests made by their direct subordinates

### Employee (Role 2)

- View the schedule of one's colleagues in the same team (i.e. excluding the manager and oneself)

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

2. Place the 2 different .env.dev files provided in the `frontend` and `backend` directories.

### Database Setup

3. Run the SQL script in the `backend/SQL` directory to create the database and tables.

### Backend Setup

4. Navigate to the backend directory:

   ```sh
   cd backend
   ```

5. Install dependencies:

   ```sh
   pip install -r requirements.txt
   ```

6. On Windows, run the `run_flask.bat` script:

   ```sh
   run_flask.bat
   ```

7. Otherwise, run each Flask application individually:
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

8. Navigate to the `frontend` directory:

   ```sh
   cd ../frontend
   ```

9. Install the dependencies:

   ```sh
   npm install
   ```

10. Compile and Hot-Reload for Development:

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
