# Project Name

## Team Name

**Team: OpenDash**

## Python Version

This project requires:

```
Python 3.12+
```

## Setup

Clone the repository:

```bash
git clone https://github.com/RealUltra/OpenEats
cd OpenEats
```

## Virtual Environment

Create a virtual environment:

### Linux / macOS

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
```

### Windows

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
```

## Install Dependencies

Install the required dependencies:

```bash
pip install -r backend/requirements.txt
```

## Sample Data

To use the sample data, rename `backend/sample-data` to `backend/data`.

### Linux / macOS

```bash
mv backend/sample-data backend/data
```

### Windows

```powershell
Rename-Item backend/sample-data backend/data
```

## Running the API

Start the application with:

```bash
uv run fastapi dev --entrypoint backend.app.main:main
```

The application will be available at:

```
http://127.0.0.1:8000
```

## Running the Web UI

Go into the frontend directory:
```bash
cd frontend
```

Install the packages:
```bash
npm i
```

Run the Web UI in development mode:
```bash
npm run dev
```

The web UI will be available at:

```
http://localhost:5173/
```


## API Endpoints

The API provides the following endpoints:

| Method | Path | Description |
|---|---|---|
| GET | `/health` | `Checks if the API is running.` |
| GET | `/restaurants` | `Lists all the restaurants.` |

## API Documentation

API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Running Tests

Run the test suite from the appropriate project directory:

```bash
python -m pytest backend/tests -q -s --tb=short
```

## Repository Structure

```text
OpenEats/
├── backend/
│   ├── app/
│   │   ├── api/            # API route definitions
│   │   ├── core/           # Functionality code
│   │   ├── repositories/   # Data-access logic
│   │   ├── schemas/        # Pydantic models/schemas
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── data/               # Application data
│   ├── sample-data/        # Sample application data
│   ├── scrum/              # Project documents
│   ├── tests/              # Automated tests
│   │   └── test-data/      # Test data
│   └── requirements.txt    # Python dependencies
├── frontend/
├── README.md
└── .gitignore 
```
