"""
Unit tests for the SGP decoders.

These run against saved API fixtures (no network), verifying that the terse
single-letter keys are mapped to readable fields.
"""

import json
import pathlib

import sgp_api

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_decode_competition():
    comp = sgp_api.decode_competition(_load("comp_91.json"))
    assert comp["id"] == 91
    assert comp["name"] == "Italy SGP 2026"
    assert comp["short_name"] == "Italy SGP"
    assert comp["first_day"] == "2026-05-23"
    assert comp["pilot_count"] == 16
    assert len(comp["days"]) == 8
    # First day is a practice day with a known id.
    assert comp["days"][0]["day_id"] == 1609
    assert comp["days"][0]["type_label"] == "Practice"
    # Race days are type 1.
    assert any(d["day_id"] == 1610 and d["type_label"] == "Race" for d in comp["days"])


def test_decode_pilots():
    comp_obj = _load("comp_91.json")
    pilots = [sgp_api.decode_pilot(comp_obj["p"][k]) for k in comp_obj["p"]]
    assert len(pilots) == 16
    michele = next(p for p in pilots if p["last_name"] == "Chiarelli")
    assert michele["name"] == "Michele Chiarelli"
    assert michele["competition_number"] == "MC"
    assert michele["country"] == "IT"
    assert michele["aircraft"] == "Ventus 3 FES"
    assert michele["registration"] == "D-KKMC"
    assert michele["flarm_id"] == "FLRD003A2"


def test_decode_task():
    task = sgp_api.decode_task(_load("day_91_1610.json"))
    assert task["task_id"] == 1112
    assert task["name"] == "20260524 Task B"
    assert task["length"] == "205.16 km"
    assert task["airfield"] == "Calcinate del Pesce"
    assert task["timezone"] == "Europe/Rome"
    assert task["start_altitude"] == 1500
    assert task["finish_altitude"] == 400
    assert len(task["turnpoints"]) == 6
    # First turnpoint is the start, a line of radius 2500.
    start = task["turnpoints"][0]
    assert start["role"] == "Start"
    assert start["observation_zone"] == "Line"
    assert start["radius"] == 2500
    # Last turnpoint is the finish.
    assert task["turnpoints"][-1]["role"] == "Finish"
    # Middle turnpoints are cylinders.
    assert task["turnpoints"][1]["observation_zone"] == "Cylinder"


def test_decode_task_missing():
    assert "error" in sgp_api.decode_task({})


def test_decode_day_results():
    day = _load("day_92_1620.json")
    out = sgp_api.decode_day_results(day)
    assert out["day_id"] == 1620
    assert out["results_status"] == 2
    assert out["results_status_label"] == "official"
    assert len(out["results"]) == 20
    # Results are ranked; the winner scored 10 points.
    winner = out["results"][0]
    assert winner["rank"] == 1
    assert winner["competition_number"] == "3V"
    assert winner["points"] == 10
    assert winner["distance_km"] == 113.9
    assert winner["speed_kph"] == 80.1
    assert winner["task_time_seconds"] == 5118.0
    assert winner["igc_file"] == "LXV-AKN_"


def test_decode_day_results_with_pilots():
    day = _load("day_92_1620.json")
    pilots_by_id = {1206: {"name": "Tilo Holighaus", "country": "DE"}}
    out = sgp_api.decode_day_results(day, pilots_by_id)
    assert out["results"][0]["name"] == "Tilo Holighaus"
    assert out["results"][0]["country"] == "DE"


def test_decode_total_results():
    day = _load("day_92_1620.json")
    out = sgp_api.decode_total_results(day)
    assert out["day_id"] == 1620
    assert len(out["standings"]) == 20
    # Standings are ranked by total points; leader has the most.
    leader = out["standings"][0]
    assert leader["rank"] == 1
    assert leader["pilot_id"] == 1206
    assert leader["total_points"] == 10
    # On the first race day, cumulative total equals the day's winning points.
    assert leader["total_points"] >= out["standings"][-1]["total_points"]


def test_decode_results_missing():
    assert "error" in sgp_api.decode_day_results({})
    assert "error" in sgp_api.decode_total_results({})


def test_build_igc_filename():
    # Characters 4-6 of the flight-recorder string form the middle component.
    assert sgp_api.build_igc_filename("YO", "LXV-8AQ_") == "YO.8AQ.igc"
    # Missing/short flight-recorder string drops the middle component.
    assert sgp_api.build_igc_filename("YO", "") == "YO.igc"
    assert sgp_api.build_igc_filename("YO", None) == "YO.igc"


def test_find_igc_file_ref():
    day = _load("day_91_1610.json")
    ref = sgp_api.find_igc_file_ref(day, "YO")
    assert ref is not None
    assert ref["file_num"] == 38032
    assert ref["pilot_id"] == 1166
    assert ref["flight_recorder"] == "LXV-8AQ_"
    assert ref["filename"] == "YO.8AQ.igc"
    # Comp-number match is case-insensitive.
    assert sgp_api.find_igc_file_ref(day, "yo")["file_num"] == 38032


def test_find_igc_file_ref_not_found():
    day = _load("day_91_1610.json")
    assert sgp_api.find_igc_file_ref(day, "ZZ") is None
    assert sgp_api.find_igc_file_ref({}, "YO") is None


def test_decode_ranking_pilot_valid():
    out = sgp_api.decode_ranking_pilot(_load("ranking_pilot_2834.json"), 2834)
    assert out["valid"] is True
    assert out["ranking_id"] == "2834"
    assert out["pilot_id"] == 2834
    assert out["name"] == "Lars Rune Bjørnevik"
    assert out["nationality"] == "NOR"
    assert out["ranking_points"] == 0
    assert out["ranking_position"] == 0


def test_decode_ranking_pilot_object_name_shape():
    # Older (PDF) shape nests records under "object_name"; decoder handles it too.
    payload = {"object_name": [{"pilotid": "2834", "firstname": "Lars Rune",
                                "surname": "Bjørnevik", "nationality": "NOR"}]}
    out = sgp_api.decode_ranking_pilot(payload, 2834)
    assert out["valid"] is True
    assert out["name"] == "Lars Rune Bjørnevik"


def test_decode_ranking_pilot_not_found():
    # FAI returns {"data": null} (parsed to None for the value) for an unknown id.
    for payload in (None, {}, {"data": None}, {"object_name": []}):
        out = sgp_api.decode_ranking_pilot(payload, 999999)
        assert out["valid"] is False
        assert out["ranking_id"] == "999999"
        assert "message" in out


def test_decode_ranking_pilot_id_mismatch():
    # A returned record whose pilotid differs from the request is not a match.
    out = sgp_api.decode_ranking_pilot(_load("ranking_pilot_2834.json"), 1)
    assert out["valid"] is False
    assert out["pilot_id"] == 2834
