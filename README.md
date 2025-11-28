EV Auto Repair Shop Management System
- A comprehensive desktop application designed to manage the daily operations of an auto repair shop. Built with Python, this system provides an admin-focused interface for managing clients, vehicles, repair orders, and generating reports. It uses a local SQLite database for persistent data storage, ensuring all information is saved between sessions.

Features
- The application is organized into several key modules, accessible from a side navigation menu after a secure login.

Secure Login
- Admin Authentication: The application starts with a secure login window.
- Password Hashing: Passwords are securely hashed using SHA-256 before being stored in the database.

Dashboard
- Today's Overview: Get a real-time snapshot of the current day's activities, including:
  - Today's Sales
  - Total Repairs Today
  - In-progress Repairs
  - Completed Repairs
- Monthly Overview: View aggregated statistics for the current month to track performance over time.

Client & Vehicle Management
- Add Clients: Easily register new customers with their contact information.
- Add Vehicles: Associate one or more vehicles to a client, specifying the vehicle type, brand, and model.
- Client/Vehicle List: View a comprehensive table of all clients and their registered vehicles.

Service & Repair Order Management
- Create Repair Orders: A dedicated form to create new service orders for a selected client and vehicle.
- Service Catalog: Choose from a predefined, categorized catalog of services (e.g., Preventive Maintenance, Engine Repair).
- Auto-filled Details: Selecting a service automatically populates:
  - Recommended parts
  - Suggested mechanics based on specialization
  - Estimated time for completion
  - Minor and Major repair costs
- Track Status: Monitor the status of each repair order (`Check-in` or `Pickup`).
- Order Aggregation: The service view groups multiple repairs for the same vehicle under a single, expandable entry for clarity.
- Mark as Done: Easily update the status of a repair to "Pickup," which automatically records the completion time.

Reports & Analytics
- All Service History: Generate a detailed report of all repair orders ever created.
- Filter by Client: Narrow down the report to view the service history for a specific client.
- Sales by Month: Calculate and display the total sales for any given month and year.
- Mechanic Summary: View a performance summary for each mechanic, including the number of completed jobs and the total sales they've generated.

Daily History
- Today's Log: A separate view that shows a clean, chronological list of all services initiated or completed on the current day.

Technologies Used

- Language: Python 
- GUI Framework: CustomTkinter for a modern and themed user interface.
- Database: SQLite 3 for local, file-based data persistence.
- Standard Libraries: `tkinter`, `datetime`, `hashlib`.

Setup and Installation
- Follow these steps to get the application running on your local machine.

Prerequisites
- Python 3.8 or newer.

Installation
1. Clone the repository or download the source code.

2. Install the required Python library.
    Open your terminal or command prompt and run the following command:
    ```sh
    pip install customtkinter
    ```

3.  Run the application.
    Navigate to the project directory and run the main Python script:
    ```sh
    python "main.py"
    ```

4.  Login.
    The application will start and display a login window. Use the default credentials to log in:
    - Username: `admin`
    - Password: `admin123`

Upon the first run, a database file named `ev_auto_repairshop.db` will be automatically created in the same directory.

How to Use
1. Login: Start the application and log in with the admin credentials.
2.  Add a Client:
    - Go to the Client page.
    - Fill in the customer's name, contact info, and vehicle details.
    - Click "Save Client + Vehicle".
3. Create a Service Order:
    - Go to the Service page.
    - Select the client and their vehicle from the dropdown menus.
    - Choose the "Type of Job" and the "Specific Service".
    - Adjust details like severity, description, and assigned mechanics if needed.
    - Click "Save service". The new order will appear in the "Existing Repair Orders" table.
4.  Complete a Repair:
    - On the Service page, select the order from the table.
    - Click "Mark as Done (Pickup)". The status will be updated, and the completion time will be recorded.
5.  View Reports:
    - Go to the Reports page to see mechanic summaries and overall service history.
    - Use the "Sales by Month" feature to check financial performance.