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
   - Derek Tan is a direct subordinate of Jack Sim, so his WFH requests will be handled by Jack Sim

1. Manager (Role 3)

   - Name: Siti Abdullah
   - Department: Sales
   - Staff ID: 140879
   - Siti Abdullah is a direct subordinate of Derek Tan, so her WFH requests will be handled by Derek Tan

1. Employee (Role 2)
   - Name: Sirirat Chaiyaporn
   - Department: Sales
   - Staff ID: 140001
   - Sirirat Chaiyaporn is a direct subordinate of Siti Abdullah, so her WFH requests will be handled by Siti Abdullah

The roles are predefined in the application given the approval by the teaching team that we do not need to create the login and authentication process. To switch between roles, you can click on the user icon in the top right corner of the application.

## Known Limitations

- The application is optimised for desktop viewing
- Session data is stored in browser localStorage
- API rate limits may apply for free-tier cloud services
