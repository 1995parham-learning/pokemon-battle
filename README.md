# Pokemon Battle

A Pokemon battle simulator that fetches data from PokeAPI and determines battle outcomes based on stats and type effectiveness.

## Features

- REST API for Pokemon battles
- Fetches Pokemon data from [PokeAPI](https://pokeapi.co/)
- In-memory caching for Pokemon data
- Battle outcome determined by comprehensive algorithm
- PostgreSQL persistence for Pokemon and battle records
- Fully containerized with Docker Compose

## Requirements

- Python 3.14+
- PostgreSQL 16+
- Docker and Docker Compose (for containerized deployment)
- [uv](https://docs.astral.sh/uv/) package manager

## Installation

### Local Development

1. Clone the repository:

```bash
git clone <repository-url>
cd pokemon-battle
```

2. Install dependencies with uv:

```bash
uv sync --dev
```

3. Set up configuration (uses Python 3.14's `tomllib`):

```bash
cp config.toml.example config.toml
# Edit config.toml with your settings
```

4. Start PostgreSQL (or use Docker):

```bash
docker run -d \
  --name pokemon-db \
  -e POSTGRES_USER=pokemon \
  -e POSTGRES_PASSWORD=pokemon \
  -e POSTGRES_DB=pokemon_battle \
  -p 5432:5432 \
  postgres:16-alpine
```

5. Run the application:

```bash
uv run uvicorn pokemon_battle.main:app --reload
```

### Docker Compose (Recommended)

```bash
docker compose up -d
```

The API will be available at `http://localhost:8000`.

## API Documentation

Once running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Endpoints

#### Health Check

```
GET /api/v1/health
```

Returns the API health status.

#### Pokemon

**Get Pokemon by name:**

```
GET /api/v1/pokemon/{name}
```

Fetches Pokemon data. If not in database, retrieves from PokeAPI and caches locally.

**List all Pokemon:**

```
GET /api/v1/pokemon?limit=100&offset=0
```

Lists all Pokemon stored in the database.

#### Battles

**Start a battle:**

```
POST /api/v1/battles
Content-Type: application/json

{
  "pokemon1_name": "pikachu",
  "pokemon2_name": "charizard"
}
```

Response:

```json
{
  "id": 1,
  "pokemon1": { "name": "pikachu", ... },
  "pokemon2": { "name": "charizard", ... },
  "winner": { "name": "charizard", ... },
  "pokemon1_score": 45.5,
  "pokemon2_score": 72.3,
  "battle_log": "...",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Get battle by ID:**

```
GET /api/v1/battles/{id}
```

**List all battles:**

```
GET /api/v1/battles?limit=100&offset=0
```

## Battle Algorithm

The battle algorithm determines the winner based on a comprehensive scoring system:

### 1. Base Stats Power (50% weight)

Calculates a power score from Pokemon stats:

- **Offensive Power**: `(Attack + Special Attack) / 2`
- **Defensive Power**: `(Defense + Special Defense) / 2`
- **Base Power**: `(HP × 0.5 + Offensive + Defensive + Speed) / 4`

### 2. Type Effectiveness (30% weight)

Uses the official Pokemon type chart to calculate advantages:

- **Super Effective (2x)**: Fire → Grass, Water → Fire, etc.
- **Not Very Effective (0.5x)**: Fire → Water, Electric → Ground, etc.
- **Immune (0x)**: Normal → Ghost, Ground → Flying, etc.
- **Dual Types**: Multipliers stack (e.g., Electric → Water/Flying = 4x)

Type bonus = `type_effectiveness × base_power × 0.3`

### 3. Speed Advantage (20% weight)

Faster Pokemon get a bonus (they would attack first in real battles):

- Speed ratio = `attacker_speed / defender_speed`
- Speed bonus = `min(speed_ratio, 2.0) × base_power × 0.2`

### Final Score Calculation

```
Score = (base_power × 0.5) + type_bonus + speed_bonus
```

- The Pokemon with the higher score wins
- If scores are within 1% of each other, it's a draw

### Rationale

This algorithm balances:

1. **Raw power** - Stronger Pokemon generally win
2. **Type matchups** - Strategic advantage matters (like in real Pokemon)
3. **Speed** - Being faster provides an edge

It's simplified from actual Pokemon battles (no moves, abilities, items) but captures the essential factors that determine battle outcomes.

## Development

### Running Tests

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=src/pokemon_battle --cov-report=html
```

### Code Quality

**Linting with ruff:**

```bash
uv run ruff check src/ tests/
```

**Format code:**

```bash
uv run ruff format src/ tests/
```

**Type checking with mypy:**

```bash
uv run mypy src/
```

### Project Structure

```
pokemon-battle/
├── src/
│   └── pokemon_battle/
│       ├── __init__.py      # Package initialization
│       ├── api.py           # REST API endpoints
│       ├── battle.py        # Battle algorithm
│       ├── config.py        # Configuration settings
│       ├── database.py      # Database connection
│       ├── exceptions.py    # Custom exceptions
│       ├── main.py          # FastAPI application
│       ├── models.py        # SQLAlchemy models
│       ├── pokeapi.py       # PokeAPI client with caching
│       ├── schemas.py       # Pydantic schemas
│       └── services.py      # Business logic
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_api.py          # API endpoint tests
│   ├── test_battle.py       # Battle algorithm tests
│   └── test_pokeapi.py      # PokeAPI client tests
├── compose.yaml             # Docker Compose configuration
├── Dockerfile               # Application container
├── pyproject.toml           # Project configuration
└── README.md
```

## Database Schema

### Pokemon Table

| Column          | Type         | Description           |
| --------------- | ------------ | --------------------- |
| id              | INTEGER      | Primary key           |
| pokeapi_id      | INTEGER      | PokeAPI identifier    |
| name            | VARCHAR(100) | Pokemon name          |
| hp              | INTEGER      | Hit points            |
| attack          | INTEGER      | Attack stat           |
| defense         | INTEGER      | Defense stat          |
| special_attack  | INTEGER      | Special attack stat   |
| special_defense | INTEGER      | Special defense stat  |
| speed           | INTEGER      | Speed stat            |
| types           | VARCHAR(100) | Comma-separated types |
| sprite_url      | VARCHAR(500) | Sprite image URL      |
| created_at      | TIMESTAMP    | Record creation time  |
| updated_at      | TIMESTAMP    | Last update time      |

### Battles Table

| Column         | Type      | Description                             |
| -------------- | --------- | --------------------------------------- |
| id             | INTEGER   | Primary key                             |
| pokemon1_id    | INTEGER   | First Pokemon (FK)                      |
| pokemon2_id    | INTEGER   | Second Pokemon (FK)                     |
| winner_id      | INTEGER   | Winner Pokemon (FK, nullable for draws) |
| pokemon1_score | FLOAT     | First Pokemon's battle score            |
| pokemon2_score | FLOAT     | Second Pokemon's battle score           |
| battle_log     | TEXT      | Detailed battle log                     |
| created_at     | TIMESTAMP | Battle timestamp                        |

## Configuration

The application uses TOML for configuration (Python 3.14's built-in `tomllib`):

```toml
# config.toml
[database]
url = "postgresql+asyncpg://pokemon:pokemon@localhost:5432/pokemon_battle"

[pokeapi]
base_url = "https://pokeapi.co/api/v2"
timeout = 30.0

[cache]
pokemon_ttl = 3600  # TTL in seconds

[api]
title = "Pokemon Battle API"
version = "1.0.0"
debug = false
```

If `config.toml` is not present, sensible defaults are used.

## Caching

The application implements an in-memory cache for Pokemon data fetched from PokeAPI:

- Default TTL: 1 hour (configurable via `cache.pokemon_ttl` in config.toml)
- Reduces API calls to PokeAPI
- Improves response times for repeated requests

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `201`: Resource created (battles)
- `400`: Bad request (e.g., same Pokemon battling)
- `404`: Pokemon or battle not found
- `502`: PokeAPI communication error
- `500`: Internal server error

Error responses include a `detail` message explaining the issue.

## License

MIT
