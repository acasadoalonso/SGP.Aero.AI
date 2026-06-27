"""
sgp_server.py — MCP server exposing SGP (Sailplane Grand Prix) competition data.

A thin wrapper over sgp_api.py. Exposes ten tools (read-only, except
download_sgp_file which can also save an IGC file to disk):
  - list_competitions
  - get_competition
  - get_pilots
  - get_task
  - get_task_waypoints
  - get_task_length
  - get_day_results
  - get_total_results
  - validate_ranking_id
  - download_sgp_file

Served over HTTP (streamable-http transport). Launch with run.sh.
26-June-2026 La Toja, Galicia, Spain
"""

from mcp.server.fastmcp import FastMCP

import sgp_api

mcp = FastMCP("sgp", host="0.0.0.0", port=9010, streamable_http_path="/sgp")


@mcp.tool()
def list_competitions() -> list[dict]:
    """List all SGP competitions known to crosscountry.aero.

    Returns id, title, venue, country, status, and dates for each edition.
    Use the returned id with the other tools.
    """
    return sgp_api.fetch_competitions()


@mcp.tool()
def get_competition(comp_id: int) -> dict:
    """Get one SGP competition's details and its index of days.

    Returns the competition name, short name, first/last day, pilot count, and
    a list of days. Each day carries a `day_id` to pass to `get_task`.
    """
    return sgp_api.fetch_competition(comp_id)


@mcp.tool()
def get_pilots(comp_id: int) -> list[dict]:
    """List the pilots entered in an SGP competition.

    Returns name, competition number, country, aircraft, registration,
    flarm id, and IGC ranking-id for each pilot.
    """
    return sgp_api.fetch_pilots(comp_id)


@mcp.tool()
def get_task(comp_id: int, day_id: int) -> dict:
    """Get the task set on a given competition day.

    `day_id` comes from `get_competition`. Returns task name/type, length,
    airfield, start/finish altitude, start time, and the decoded turnpoints.
    """
    return sgp_api.fetch_task(comp_id, day_id)


@mcp.tool()
def get_task_waypoints(comp_id: int, day_id: int) -> list[dict]:
    """Get just the waypoints (turnpoints) of a given competition day's task.

    `day_id` comes from `get_competition`. Returns the ordered turnpoints, each
    with index, name, role (Start/Turnpoint/Finish), latitude, longitude,
    observation zone (Line/Cylinder), and radius.
    """
    return sgp_api.fetch_task_waypoints(comp_id, day_id)


@mcp.tool()
def get_task_length(comp_id: int, day_id: int) -> dict:
    """Get the task length for a given competition day.

    `day_id` comes from `get_competition`. Returns the task id, name, type,
    length (e.g. "205.16 km"), and waypoint count.
    """
    return sgp_api.fetch_task_length(comp_id, day_id)


@mcp.tool()
def get_day_results(comp_id: int, day_id: int) -> dict:
    """Get the individual results scored on a given competition day.

    `day_id` comes from `get_competition`. Returns the results status and a list
    of pilots ranked for that day, each with rank, competition number, name,
    points, speed (km/h), distance (km), task time, and IGC filename.
    """
    return sgp_api.fetch_day_results(comp_id, day_id)


@mcp.tool()
def get_total_results(comp_id: int, day_id: int) -> dict:
    """Get the cumulative competition standings as of a given day.

    `day_id` comes from `get_competition`; pass the last race day for the final
    overall standings. Returns each pilot's total points to date, ranked, with
    name, country, and competition number.
    """
    return sgp_api.fetch_total_results(comp_id, day_id)


@mcp.tool()
def validate_ranking_id(ranking_id: str) -> dict:
    """Validate a pilot's FAI ranking-list id against the FAI ranking list.

    IGC `ranking_id` is the value carried by each pilot in `get_pilots` (the FAI
    ranking-list id). Looks it up via the FAI ranking-list REST API and returns
    `valid` (whether a matching entry exists) plus, when found, the pilot's
    name, nationality, ranking points, and ranking position.a
    It can be used to match in a competition that is a valid and correct ID for each pilot
    """
    return sgp_api.fetch_ranking_pilot(ranking_id)


@mcp.tool()
def download_sgp_file(comp_id: int, day_id: int, competition_number: str,
                      save_dir: str | None = None) -> dict:
    """Download a pilot's IGC flight log for a given competition day.

    `day_id` comes from `get_competition`; `competition_number` is the pilot's
    contest number (the `competition_number` field from `get_pilots` /
    `get_day_results`, e.g. "YO"). Resolves the pilot's download file number from
    that day's results and fetches the raw IGC from crosscountry.aero.

    Returns the resolved `file_num`, the `filename` (`<comp_number>.<frq>.igc`),
    `size_bytes`, and the IGC `content` as text. If `save_dir` is given, the IGC
    is also written there and the path returned as `saved_path`.
    """
    return sgp_api.fetch_igc_file(comp_id, day_id, competition_number, save_dir)


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
