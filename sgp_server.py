"""
sgp_server.py — MCP server exposing SGP (Sailplane Grand Prix) competition data.

A thin wrapper over sgp_api.py. Exposes six read-only tools:
  - list_competitions
  - get_competition
  - get_pilots
  - get_task
  - get_task_waypoints
  - get_task_length
  - get_day_results
  - get_total_results

Served over HTTP (streamable-http transport). Launch with run.sh.
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
    flarm id, and ranking id for each pilot.
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


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
