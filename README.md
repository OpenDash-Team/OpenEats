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

## Development

### Virtual Environment

Create a virtual environment:

#### Linux / macOS

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
```

#### Windows

```powershell
python -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
```

### Install Dependencies

Install the required dependencies:

```bash
pip install -r backend/requirements.txt
```

### Sample Data (Optional, First Run Only)

To use the sample data, rename `backend/sample-data` to `backend/data`.

#### Linux / macOS

```bash
mv backend/sample-data backend/data
```

#### Windows

```powershell
Rename-Item backend/sample-data backend/data
```

### Running the API

Start the application with:

```bash
fastapi dev --entrypoint backend.app.main:main
```

The application will be available at:

```
http://127.0.0.1:8000
```

### Running the Web UI

#### Prerequisites

Install Node.js and npm.

#### Start the development server

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

## Production

### Prerequisites

Install Docker with Docker Compose.

### Sample Data (Optional, First Run Only)

To start with the sample restaurants, move `backend/sample-data` to `data` in the repository root before starting the application.

#### Linux / macOS

```bash
mv backend/sample-data ./data
```

#### Windows

```powershell
Move-Item backend/sample-data data
```

### Start the Application

From the repository root, run:

```bash
docker compose up --build -d
```

If there have been no changes since you last built the image, you may run:

```bash
docker compose up -d
```

### Open the Application

```text
http://127.0.0.1:8000/
```

### Stop the Application

```bash
docker compose down
```

## Using the UI

On the startup screen, choose **Customer** to browse restaurants or **Restaurant** to select an existing restaurant or create a new one. The restaurant view has tabs for general details and menu items.

## API Endpoints

The API provides the following endpoints:

| Method | Path | Description |
|---|---|---|
| GET | `/api/v1/health` | `Checks if the API is running.` |
| GET | `/api/v1/restaurants` | `Lists all the restaurants.` |
| GET | `/api/v1/restaurants?{query}` | `Lists all the restaurants that match searching query: name=...&hasMenu=...&sort_by=...&sort_desc=...` |
| GET | `/api/v1/restaurants/{restaurant_id}` | `Retrieves a specific restaurant by its ID.` |
| POST | `/api/v1/restaurants` | `Creates a restaurant. Returns 201, 409 if the same name and address already exist, 422 for invalid input.` |
| PATCH | `/api/v1/restaurants/{restaurant_id}` | `Updates only the fields sent. Returns 200, 404 for an unknown ID, 409 for a duplicate, 422 for invalid input.` |
| POST | `/api/v1/restaurants/{restaurant_id}/menu-items` | `Creates a new menu item. Returns 201, 404 if the restaurant is not found, 422 for invalid input.` |
| PATCH | `/api/v1/restaurants/{restaurant_id}/menu-items/{menu_item_id}` | `Updates a menu item's fields. Returns 200, 404 if the item or restaurant is not found, 422 for invalid input.` |
| DELETE | `/api/v1/restaurants/{restaurant_id}/menu-items/{menu_item_id}` | `Deletes a specific menu item. Returns 204 on success, 404 if not found.` |
| POST | `/api/v1/customers` | `Registers a customer. Returns 201 (without the password), 409 if the email is already registered, 422 for invalid input.` |
| GET | `/api/v1/customers/me` | `Returns the signed-in customer's info. Returns 401 if not signed in.` |
| PATCH | `/api/v1/customers/me` | `Updates the signed-in customer's name, email, telephone or delivery address. Returns 200, 401, 409 if the email is taken, 422 for invalid input.` |
| DELETE | `/api/v1/customers/me` | `Deactivates the signed-in customer's account (kept but marked inactive). Returns 204, 401 if not signed in.` |
| GET | `/api/v1/cart` | `Returns the signed-in customer's active cart (creates an empty one the first time) with current prices, subtotal and total. Returns 200, 401 if not signed in.` |
| POST | `/api/v1/cart/items` | `Adds a menu item (or increases its quantity). Returns 200, 401, 404 for an unknown item, 409 if it's out of stock, from another restaurant or would go over 99, 422 for an invalid quantity.` |
| PATCH | `/api/v1/cart/items/{menu_item_id}` | `Sets an item's quantity (1-99). Returns 200, 401, 404 if the item isn't in the cart or was removed from the menu, 409 if raising the quantity of an out of stock item, 422 for an invalid quantity.` |
| DELETE | `/api/v1/cart/items/{menu_item_id}` | `Removes an item from the cart. Returns 200 with the updated cart, 401, 404 if the item isn't in the cart.` |
| DELETE | `/api/v1/cart` | `Clears the cart. Returns 200 with the empty cart, 401 if not signed in.` |


## API Documentation

API documentation is available at:

```text
http://127.0.0.1:8000/api/v1/docs
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
├── docs/
│   └── PROVENANCE.md       # AI Usage information
├── scrum/
├── frontend/               # React and Vite Web UI
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
