# Status App Backend

This is the backend for the Status App, built using Python and FastAPI.

## Getting Started

### Prerequisites

- Python 3.x
- pip (Python package manager)

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd status-app/backend
   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

To start the application, use the following command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Project Structure

- `app/`: Contains the main application code.

  - `core/`: Core utilities and configurations.
  - `db/`: Database related modules.
  - `dependencies/`: Dependency management.
  - `middleware/`: Middleware components.
  - `models/`: Data models.
  - `routes/`: API route definitions.
  - `schemas/`: Data validation schemas.
  - `websocket_manager.py`: WebSocket management.

- `Procfile`: Used for deployment configurations.
- `start.sh`: Script to start the application.

### Dependencies

The project uses several Python packages, including but not limited to:

- FastAPI
- Uvicorn
- Firebase Admin
- Pydantic
- Google Cloud Firestore

For a complete list, see `requirements.txt`.

### Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

### License

This project is licensed under the MIT License.
