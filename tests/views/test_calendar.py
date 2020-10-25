import json
import pytest

from flask import url_for, session
from flask_babel import gettext

import backend.models as md
import backend.schedules as schd


def test_index(client):
    """Test the index route"""
    rv = client.get(url_for("calendar.index"))

    assert rv.status_code == 200
    assert b"DOCTYPE html" in rv.data


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_clear(client, user):
    """Test the clear route"""
    rv = client.delete(url_for("calendar.clear"))
    data = json.loads(rv.data)
    schd = session["current_schedule"]

    # Check the Session
    assert schd.label == "New schedule"
    assert schd.is_empty()

    # Check the returned data
    assert data["current_schedule"]["id"] == schd.id
    assert data["current_schedule"]["label"] == gettext(schd.label)
    assert data["current_schedule"]["color_palette"] == schd.color_palette
    assert data["current_project_id"] == schd.project_id


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_get_data(client, manager, user):
    """Test the get_data route"""
    rv = client.get(url_for("calendar.get_data"))
    data = json.loads(rv.data)

    assert data["project_id"] == manager.get_project_ids()
    assert data["current_project_id"] == session["current_schedule"].project_id
    assert data["current_schedule"]["id"] == session["current_schedule"].id
    assert data["current_schedule"]["label"] == session["current_schedule"].label
    assert (
        data["current_schedule"]["color_palette"]
        == session["current_schedule"].color_palette
    )
    assert data["n_schedules"] == len(session["current_schedule"].best_schedules)
    assert data["events"] == session["current_schedule"].get_events(json=True)
    assert data["codes"] == session["current_schedule"].codes
    assert data["autosave"] == getattr(user, "autosave", False)
    if user.is_authenticated:
        assert data["schedules"] == list(
            map(
                lambda s: {"id": s.id, "label": gettext(s.data.label)},
                user.get_schedules(),
            )
        )
    else:
        assert data["schedules"] == []


def test_load_schedule(client, jyl):
    """Test the load_schedule(id) route"""
    schedules = jyl.get_schedules()

    rv = client.get(url_for("calendar.load_schedule", id=42666))

    assert rv.status_code == 403

    rv = client.get(url_for("calendar.load_schedule", id=schedules[1].id))

    assert rv.status_code == 200
    assert session["current_schedule"].id == schedules[1].id


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_search_code(client, user):
    """Test the search_code route"""

    # Test for "ELME2M"
    rv = client.get(url_for("calendar.search_code", search_key="EL"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert "ELME2M" in data["codes"]

    rv = client.get(url_for("calendar.search_code", search_key="ELME"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert "ELME2M" in data["codes"]

    rv = client.get(url_for("calendar.search_code", search_key="ELME2M"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert "ELME2M" in data["codes"]

    rv = client.get(url_for("calendar.search_code", search_key="ELME42M"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert len(data["codes"]) == 0

    # Test for LEPLXXXX
    rv = client.get(url_for("calendar.search_code", search_key="LEPL"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert "LEPL1104" in data["codes"]
    assert "LEPL1109" in data["codes"]


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_add_code(client, user):
    """Test the add_code route"""

    # Test for "ELME2M"
    rv = client.patch(url_for("calendar.add_code", code="ELME2M"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert "ELME2M" in data["codes"]
    assert "ELME2M" in session["current_schedule"].codes

    # Test for "LEPL1109"
    rv = client.patch(url_for("calendar.add_code", code="LEPL1109"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert "LEPL1109" in data["codes"]
    assert "LEPL1109" in session["current_schedule"].codes

    # Test for non-existing code
    rv = client.patch(url_for("calendar.add_code", code="FAKECODE"))

    assert rv.status_code == 404
    assert "FAKECODE" not in session["current_schedule"].codes


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_remove_code(client, user):
    """Test the remove_code route"""

    # Test for "LEPL1104"
    rv = client.delete(url_for("calendar.remove_code", code="LEPL1104"))

    assert rv.status_code == 200
    assert "LEPL1104" not in session["current_schedule"].codes

    # Test for code not in the current schedule
    rv = client.delete(url_for("calendar.remove_code", code="ELME2M"))

    assert rv.status_code == 200
    assert "ELME2M" not in session["current_schedule"].codes

    # Test for non-existing code
    rv = client.delete(url_for("calendar.remove_code", code="FAKECODE"))

    assert rv.status_code == 200
    assert "FAKECODE" not in session["current_schedule"].codes


def test_get_info(client):
    """Test the get_info route"""
    # TODO
    assert True


def test_add_custom_event(client):
    """Test the add_custom_event route"""
    # TODO
    assert True


def test_delete_custom_event(client):
    """Test the delete_custom_event(id) route"""
    # TODO
    assert True


def test_update_custom_event(client):
    """Test the update_custom_event(id) route"""
    # TODO
    assert True


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_save(client, user):
    """Test the save route"""
    rv = client.post(url_for("calendar.save"))

    if user.is_authenticated:
        data = json.loads(rv.data)
        assert rv.status_code == 200
        assert not session["current_schedule_modified"]
        assert data["schedules"] == list(
            map(
                lambda s: {"id": s.id, "label": gettext(s.data.label)},
                user.get_schedules(),
            )
        )
    else:
        assert rv.status_code == 401


def test_download(client):
    """Test the download route"""
    # TODO
    assert True


def test_share(client, jyl, gerom):
    """Test the share route"""
    data = dict(link=gerom.get_schedules()[0].get_link().link)
    rv = client.get(url_for("calendar.share"), query_string=data)

    assert rv.status_code == 302  # There is a redirect
    assert session["current_schedule"].label == "GEROM'S SCHEDULE"

    data = dict(link="does_not_exist")
    rv = client.get(url_for("calendar.share"), query_string=data)

    assert rv.status_code == 400


def test_apply_filter(client):
    """Test the apply_filter route"""
    # TODO
    assert True


def test_update_project_id(client):
    """Test the update_poject_id route"""
    # TODO
    assert True


def test_export(client, jyl):
    """Test the export route"""
    rv = client.get(url_for("calendar.export"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert data["link"] == jyl.get_schedules()[0].get_link().link


def test_export_anonymous(client, louwi):
    """Test the export route, anonymous user version"""
    rv = client.get(url_for("calendar.export"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert session["current_schedule"].id is not None

    schd = md.Schedule.query.filter(
        md.Schedule.id == session["current_schedule"].id
    ).first()
    assert schd.data.label == "LOUWI'S SCHEDULE"
    assert data["link"] == schd.link.link


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_get_events(client, user):
    """Test the get_event route"""
    for i in range(5):
        rv = client.get(
            url_for("calendar.get_events"), query_string=dict(schedule_number=i)
        )
        data = json.loads(rv.data)

        assert rv.status_code == 200
        assert data["events"] == session["current_schedule"].get_events(
            json=True, schedule_number=i
        )


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_compute(client, user):
    """Test the compute route"""
    rv = client.put(url_for("calendar.compute"))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert data["n_schedules"] == len(session["current_schedule"].best_schedules)
    assert data["events"] == session["current_schedule"].get_events(
        json=True, schedule_number=1
    )
    assert (data["selected_schedule"]) == (
        1 if len(session["current_schedule"].best_schedules) > 0 else 0
    )


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_update_color(client, user):
    """Test the update_color route"""
    data = dict(color_palette=["BLACK", "YELLOW", "RED"], schedule_number=0)
    rv = client.post(url_for("calendar.update_color"), json=data)
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert data["events"] == session["current_schedule"].get_events(json=True)
    assert session["current_schedule"].color_palette == ["BLACK", "YELLOW", "RED"]


@pytest.mark.parametrize("user", ["jyl", "louwi"], indirect=True)
def test_reset_color(client, user):
    """Test the reset_color route"""
    rv = client.delete(url_for("calendar.reset_color"), json=dict(schedule_number=0))
    data = json.loads(rv.data)

    assert rv.status_code == 200
    assert data["events"] == session["current_schedule"].get_events(json=True)
    assert data["color_palette"] == schd.COLOR_PALETTE
    assert session["current_schedule"].color_palette == schd.COLOR_PALETTE
