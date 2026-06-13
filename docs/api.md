# ProtoForge AI Backend API Documentation

The backend services expose standard RESTful endpoints on `http://localhost:8000`.

## Key Endpoints

### 1. Project Management

- **GET `/api/v1/projects`**: List all user projects.
- **POST `/api/v1/projects`**: Create a new project.
  - *Payload*: `{"name": "string", "description": "string", "prompt": "string"}`
- **GET `/api/v1/projects/{id}`**: Fetch details of a specific project.
- **DELETE `/api/v1/projects/{id}`**: Delete a project.

### 2. Assets & Generation

- **POST `/api/v1/projects/{id}/generate`**: Trigger generative CAD synthesis.
  - *Payload*: `{"prompt": "string", "format": "step" | "stl" | "gltf"}`
- **GET `/api/v1/projects/{id}/assets`**: Retrieve links to generated 3D meshes, 4K renders, and ISO drawings.

### 3. Simulation (FEA)

- **POST `/api/v1/projects/{id}/simulate`**: Run finite element stress and thermal analysis.
- **GET `/api/v1/projects/{id}/simulations`**: Retrieve simulation status and stress meshes.

### 4. Billing & Subscriptions

- **GET `/api/v1/subscriptions/status`**: Check subscription tier status (Free, Starter, Pro, Enterprise).
