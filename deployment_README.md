# WFH Management Tool - Cloud Deployment

## Deployment Links

- Frontend: [https://is212-frontend.vercel.app](https://is212-frontend.vercel.app)
- Backend: [https://is212-backend.vercel.app](https://is212-backend.vercel.app)
- Database: NeonDB (PostgreSQL)

## Architecture

The application is deployed using the following cloud services:

- Frontend: Vercel (Vue.js application)
- Backend: Vercel (Flask microservices)
- Database: NeonDB (PostgreSQL database)

## Features Available

### General

- View own schedule (weekly, daily)
- Apply for WFH request (one-time or recurring)
- View WFH requests made by oneself
- Withdraw requests made by oneself that have status "Pending Approval" or "Approved"

### HR & Management (Role 1)

- View work arrangements by department (In Office, WFH - AM, WFH - PM, WFH - Full)
- Easily see when the attendance rate of a department in office on a particular day is below 50%

### Director (Role 1)

- View the work arrangements of the teams of the managers under a director (In Office, WFH - AM, WFH - PM, WFH - Full)
- Approve or reject work-from-home requests made by their direct subordinates
- Rescind previously-approved WFH requests made by their direct subordinates
- Easily see when the attendance rate of a particular team in office on a particular day is below 50%

### Manager (Role 3)

- View the work arrangements of the team under oneself (In Office, WFH - AM, WFH - PM, WFH - Full)
- Approve or reject work-from-home requests within their team (direct subordinates)
- Rescind previously-approved WFH requests made by their direct subordinates

### Employee (Role 2)

- View the schedule of one's colleagues in the same team (i.e. excluding the manager and oneself)

## Accessing the Application

### Test Users

You can log in as different types of users to test various functionalities:

1. HR & Management (Role 1)

   - Name: Jack Sim
   - Department: CEO
   - Staff ID: 130002

1. Director (Role 1)

   - Name: Derek Tan
   - Department: Sales
   - Staff ID: 140001

1. Manager (Role 3)

   - Name: Siti Abdullah
   - Department: Sales
   - Staff ID: 140879

1. Employee (Role 2)
   - Name: Sirirat Chaiyaporn
   - Department: Sales
   - Staff ID: 140001

The roles are predefined in the application given the approval by the teaching team that we do not need to create the login and authentication process. To switch between roles, you can click on the user icon in the top right corner of the application.

## Known Limitations

- The application is optimised for desktop viewing
- Session data is stored in browser localStorage
- API rate limits may apply for free-tier cloud services
