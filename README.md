# SGP MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that exposes **Sailplane Grand Prix (SGP)** competition data from [crosscountry.aero](https://www.crosscountry.aero) — the official data source for gliding championships.

## What it does

Read-only access to SGP competition datasets: events, pilots, daily tasks, turnpoints, day results, and cumulative standings. Also validates individual pilot FAI ranking-list IDs.

## Quick start

```bash
# Direct (no Docker)
./run.sh

# Docker
make build
make exec
```

The server listens on **`http://0.0.0.0:9010/sgp`** (streamable HTTP transport).

## Tools

| Tool | Description |
|------|-------------|
| `list_competitions` | List all SGP competitions (id, title, venue, country, dates, status) |
| `get_competition(comp_id)` | Get one competition's details + day index (each day carries a `day_id`) |
| `get_pilots(comp_id)` | List pilots entered in a competition (name, country, aircraft, registration, flarm, ranking\_id) |
| `get_task(comp_id, day_id)` | Get the task for a given day (name, type, length, airfield, start/finish altitude, decoded turnpoints) |
| `get_task_waypoints(comp_id, day_id)` | Get just the ordered turnpoints (index, name, role, lat/lng, observation zone, radius) |
| `get_task_length(comp_id, day_id)` | Get task length and waypoint count (lightweight summary) |
| `get_day_results(comp_id, day_id)` | Get individual daily results (rank, points, speed, distance, task time, IGC file) |
| `get_total_results(comp_id, day_id)` | Get cumulative standings as of a given day (total points, ranked) |
| `validate_ranking_id(ranking_id)` | Validate a pilot's FAI ranking-list ID against the FAI ranking API |

### Typical workflow

```
list_competitions()
  → pick an id (e.g. 91 for "Italy SGP 2026")
get_competition(91)
  → pick a day_id (e.g. 1610)
get_task(91, 1610)        → task geometry + turnpoints
get_task_waypoints(91, 1610)  → turnpoints only
get_task_length(91, 1610) → length summary
get_pilots(91)            → pilot roster
get_day_results(91, 1610) → daily scoring
get_total_results(91, 1610) → cumulative standings
```

## Architecture

```
sgp_server.py          ← MCP tools (FastMCP, HTTP transport)
sgp_api.py             ← API fetchers + pure decoders (single-letter keys → readable dicts)
tests/                 ← 12 unit tests against JSON fixtures (no network needed)
tests/fixtures/        ← Saved API responses for offline testing
```

- **`sgp_server.py`** (122 lines) — Thin MCP server wrapping `sgp_api.py`. 8 tools exposed.
- **`sgp_api.py`** (365 lines) — Core library. Pure `decode_*` functions (raw dict in, clean dict out) and `fetch_*` wrappers (HTTP + decode). Decodes the terse single-letter-key JSON from crosscountry.aero.

### Data sources

| Endpoint | URL |
|----------|-----|
| Competition list | `https://data.crosscountry.aero/public/get/events` |
| Competition + pilots + days | `https://www.crosscountry.aero/c/sgp/rest/comp/{id}` |
| Task + results | `https://www.crosscountry.aero/c/sgp/rest/day/{comp_id}/{day_id}` |
| FAI ranking validation | `https://rankingdata.fai.org/rest/api/rlpilot?id={id}` |

## Dependencies

```
mcp[cli]
httpx
```

Install: `pip install -r requirements.txt`

## Running & deployment

| Method | Command |
|--------|---------|
| Direct | `./run.sh` |
| Docker | `make build && make exec` |
| Docker stop | `make clean` |
| Manual Docker | `docker run -d -p 9010:9010 --restart unless-stopped --name sgpmcp sgpmcp` |

### Docker environment variables

| Variable | Default |
|----------|---------|
| `SGP_MCP_TRANSPORT` | `http` |
| `SGP_MCP_HOST` | `0.0.0.0` |
| `SGP_MCP_PORT` | `9010` |
| `SGP_MCP_PATH` | `/sgp` |
| `SGP_API_URL` | `http://localhost:8000` |
| `SGP_HTTP_TIMEOUT_SEC` | `60` |
| `SGP_VERIFY_TLS` | `true` |

## Tests

```bash
cd tests
python -m pytest test_sgp_api.py -v
```

12 tests covering all decoder functions against saved fixtures. No network required.

## Project structure

```
SGP/
├── sgp_server.py        # MCP server (FastMCP, HTTP)
├── sgp_api.py           # API fetchers + decoders
├── requirements.txt     # mcp[cli], httpx
├── run.sh               # Launch script
├── Makefile             # Docker build/exec/clean
├── Dockerfile           # python:3.12-slim base
├── dockerrun.sh         # Docker run helper
├── addmcp.sh            # MCP config helper
├── tests/
│   ├── test_sgp_api.py  # 12 unit tests
│   └── fixtures/        # 4 JSON fixture files
└── README.md            # This file
```
