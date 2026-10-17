# OpenEats

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

### Prerequisites

Install Node.js and npm.

### Start the development server

From the repository root, go into the frontend directory:

```bash
cd frontend
```

Install the packages:

```bash
npm install
```

Start the Web UI:

```bash
npm run dev
```

Open the URL printed by Vite (normally `http://localhost:5173/`).

### Using the UI

On the startup screen, choose **Customer** to browse restaurants or **Restaurant** to select an existing restaurant or create a new one. The restaurant view has tabs for general details and menu items.

### Build

From the `frontend` directory, create a production build with:

```bash
npm run build
```

## API Endpoints

The API provides the following endpoints:

| Method | Path | Description |
|---|---|---|
| GET | `/health` | `Checks if the API is running.` |
| GET | `/restaurants` | `Lists all the restaurants.` |
| GET | `/restaurants?{query}` | `Lists all the restaurants that match searching query: name=...&hasMenu=...&sort_by=...&sort_desc=...` |
| GET | `/restaurants/{restaurant_id}` | `Retrieves a specific restaurant by its ID.` |
| POST | `/restaurants` | `Creates a restaurant. Returns 201, 409 if the same name and address already exist, 422 for invalid input.` |
| PATCH | `/restaurants/{restaurant_id}` | `Updates only the fields sent. Returns 200, 404 for an unknown ID, 409 for a duplicate, 422 for invalid input.` |
| POST | `/restaurants/{restaurant_id}/menu-items` | `Creates a new menu item. Returns 201, 404 if the restaurant is not found, 422 for invalid input.` |
| PATCH | `/restaurants/{restaurant_id}/menu-items/{menu_item_id}` | `Updates a menu item's fields. Returns 200, 404 if the item or restaurant is not found, 422 for invalid input.` |
| DELETE | `/restaurants/{restaurant_id}/menu-items/{menu_item_id}` | `Deletes a specific menu item. Returns 204 on success, 404 if not found.` |


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
├── docs/PROVENANCE.md
├── scrum/
├── frontend/                # React and Vite Web UI
│   ├── src/
│   │   ├── api/            # Backend request functions
│   │   ├── components/     # Reusable UI components
│   │   ├── pages/          # Application screens
│   │   ├── schemas/        # Frontend data types
│   │   ├── main.tsx        # App entry point and routes
│   │   └── index.css       # Shared styles
│   ├── index.html          # HTML entry point
│   ├── package.json        # Dependencies and npm scripts
│   └── vite.config.ts      # Vite configuration
├── README.md
└── .gitignore 
```
