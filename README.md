# cAIber Backend

This repository contains the backend services for the cAIber Threat Intelligence Platform. It's built using a microservices architecture with Python, FastAPI, and Neo4j.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+

### Installation & Running

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd cAIber-backend
    ```

2.  **Environment Variables:**
    Create a `.env` file and add the following configuration for the Neo4j database:
    ```
    NEO4J_URI=bolt://neo4j:7687
    NEO4J_USER=neo4j
    NEO4J_PASSWORD=yourstrongpassword
    ```

3.  **Build and run the services using Docker Compose:**
    ```bash
    docker-compose up --build
    ```

4.  **Access the API:**
    The API will be available at `http://localhost:8000`. You can access the auto-generated documentation at `http://localhost:8000/docs`.

---