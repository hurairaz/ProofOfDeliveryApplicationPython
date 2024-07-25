# Proof Of Delivery Application Python

The Proof Of Delivery Application is designed to manage dispatches using FastAPI, SQLAlchemy, PostgreSQL, and Alembic. The application includes features for user authentication and efficient dispatch management.

## Project Structure

The project directory is organized as follows:

```
ProofOfDeliveryApplicationPython/
│
├── .gitignore
├── alembic.ini
├── auth_handler.py
├── crud.py
├── database.py
├── main.py
├── models.py
├── requirements.txt
├── schemas.py
│
├── alembic/
│   ├── versions
│   ├── env.py
│   └── script.py.mako
│
└── router/
    ├── __init__.py
    ├── auth.py
    └── dispatches.py
```
**Note:** For detailed instructions on integrating FastAPI with PostgreSQL and initializing Alembic, please refer to my repository [Integrating-FastAPI-with-SQLAlchemy-PostgreSQL-and-Alembic](https://github.com/hurairaz/Integrating-FastAPI-with-SQLAlchemy-PostgreSQL-and-Alembic).

### Features

The application offers several key features:

- **User Authentication**: Provides functionality for user sign-up and login using JWT token-based authentication. This ensures secure access to the application and its features.
  
- **Dispatch Management**: Allows users to create, accept, start, and complete dispatches. This feature supports the full lifecycle management of dispatch records within the system.

- **Filtering**: Enables retrieval of dispatches with filters based on status, date, and other criteria. This helps in efficiently managing and querying dispatch records.


## Setup and Installation

To set up and run the application, follow these steps:

 **Clone the Repository**

   Clone the repository to your local machine:

   ```bash
   git clone https://github.com/hurairaz/ProofOfDeliveryApplicationPython.git
   cd ProofOfDeliveryApplicationPython
   ```

 **Create and Activate a Virtual Environment**

   Create a virtual environment and activate it:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

 **Install Required Dependencies**

   Install the necessary Python packages:

   ```bash
   pip install -r requirements.txt
   ```

 **Configure the Database**

   Update the database connection details in `database.py`. After configuring, apply the migrations with Alembic:

   ```bash
   alembic upgrade head
   ```

 **Run the Application**

   Start the FastAPI application:

   ```bash
   uvicorn main:app --reload
   ```

   The application will be available for interaction.

---

