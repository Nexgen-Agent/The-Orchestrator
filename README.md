# Frontier Orchestration Gateway (FOG)

FOG is a scalable orchestration and coordination gateway that sits at the front of a multi-AI ecosystem. It dispatches tasks to external supporting systems (agents), tracks task lifecycles, and manages system state and backups.

## Core Features

- **Agent Registration**: Dynamically connect supporting systems/agents.
- **Task Dispatching**: Structured task packets validated with Pydantic.
- **State Management**: File-based JSON store for tracking tasks, agents, and backups.
- **Automatic Backups**: Versioned snapshots before any modification tasks.
- **Rollback Support**: Quickly revert projects to a previous state.
- **Dependency Mapping**: Scan Python projects to build import dependency graphs.
- **Audit Trail**: Structured logging of all orchestration decisions and actions.

## Installation

1. Install dependencies:
   ```bash
   pip install fastapi pydantic uvicorn httpx
   ```

2. The project structure is as follows:
   - `fog/api`: FastAPI application and endpoints.
   - `fog/core`: Core logic (Engine, Backup, Mapper, etc.).
   - `fog/models`: Pydantic schemas.
   - `backups/`: Directory for project snapshots.
   - `storage/`: Directory for state and audit logs.

## Running the Gateway

Start the FastAPI server:
```bash
python3 -m fog.api.main
```
The API will be available at `http://localhost:8000`.

## API Endpoints

- `POST /register-agent`: Register a new agent connector.
- `POST /submit-project`: Submit a project path for tracking and initial backup.
- `POST /submit-task`: Dispatch a task packet to a registered agent.
- `GET /task-status/{id}`: Check the status of a specific task.
- `POST /rollback/{backup_id}`: Roll back a project to a specific version.
- `GET /dependency-map?project_path=...`: Generate a dependency graph for a Python project.
- `GET /system-state`: View the current state of the gateway.

## Example Usage

Check `examples/run_orchestration.py` for a full demonstration of the gateway's capabilities, including agent registration, task submission, auto-backup, and rollback.

To run the demo:
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 examples/run_orchestration.py
```

## Running Tests

Run the unit test suite:
```bash
export PYTHONPATH=$PYTHONPATH:.
python3 -m unittest discover tests
```
