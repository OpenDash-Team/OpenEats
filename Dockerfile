# Stage 1: Build the frontend

FROM node:22-alpine AS frontend-build

WORKDIR /frontend

# Copy the files required for installing packages
COPY frontend/package.json frontend/package-lock.json ./

# Install packages
RUN npm ci

# Copy the source code
COPY frontend/ ./

# Compile the frontend
RUN npm run build


# Stage 2: Prepare the backend + docker container

FROM python:3.12-slim

WORKDIR /app

# Copy the requirements file
COPY backend/requirements.txt ./

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code
COPY backend/app/ ./backend/

# Copy the compiled frontend files
COPY --from=frontend-build /frontend/dist ./frontend/

# Port of the webserver
EXPOSE 8000

# Start the FastAPI application
CMD ["uvicorn", "backend.main:main", "--host", "0.0.0.0", "--port", "8000"]