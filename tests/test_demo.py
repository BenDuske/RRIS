from datetime import datetime
from backend.ingestion.normalizer import normalize_report
from backend.intelligence.extraction import estimate_injuries
from backend.intelligence.fusion import process_event, reset_state, INCIDENT_META

I27 = dict(lat=33.5351, lng=-101.8452, address="I-27 NB near Exit 6")


def ingest(**kw):
    return process_event(normalize_report(kw))


def test_injury_count_ignores_stray_digits():
    assert estimate_injuries("At least 2 injuries on I-27, Exit 1") == 2
    assert estimate_injuries("Standing water 1 foot deep, no injuries") == 0
    assert estimate_injuries("Traffic backing up to Exit 2") is None


def test_flash_flood_warning_has_severity():
    reset_state()
    inc = ingest(source_id="nws1", source_type="nws", confidence=1.0,
                 raw_text="Flash Flood Warning for Lubbock County. Low water crossings may flood.",
                 lat=33.5779, lng=-101.8552)
    assert inc.events[0].parsed_fields.severity_estimate >= 5
    assert inc.priority > 8


def test_fusion_and_escalation():
    reset_state()
    a = ingest(source_id="c1", source_type="cad", confidence=0.85,
               raw_text="Vehicle collision I-27. 2 injuries reported.", **I27)
    b = ingest(source_id="c2", source_type="cad", confidence=0.9,
               raw_text="Fuel leak from tanker. Fire hazard present. Requesting HazMat.", **I27)
    assert a is b and len(a.events) == 2
    assert a.incident_type == "HazMat Incident"
    assert a.priority >= 60


def test_confirmation_flags_new_evidence():
    reset_state()
    inc = ingest(source_id="c1", source_type="cad", raw_text="Vehicle collision. 1 injury.", **I27)
    INCIDENT_META.setdefault(inc.id, {}).update(confirmed=True, confirmed_ai_priority=inc.priority)
    frozen = inc.priority
    ingest(source_id="c2", source_type="cad", raw_text="Fuel leak, fire hazard, entrapment.", **I27)
    assert inc.priority == frozen
    assert INCIDENT_META[inc.id]["stale_confirmation"] is True


def test_naive_timestamp_does_not_crash():
    reset_state()
    ingest(source_id="a", source_type="cad", raw_text="Crash", timestamp=datetime(2026, 9, 29, 12, 0), **I27)
    ingest(source_id="b", source_type="cad", raw_text="Crash update", timestamp=datetime(2026, 9, 29, 12, 1), **I27)


def test_short_agency_keywords_need_word_boundary():
    from backend.intelligence.extraction import detect_agencies
    assert "police" not in detect_agencies("Update: HazMat team dispatched. Expanding perimeter.")
    assert "police" in detect_agencies("Suspect fled, PD en route")


def test_different_scene_type_does_not_fuse():
    reset_state()
    a = ingest(source_id="t1", source_type="cad", raw_text="Vehicle collision, lanes blocked.", **I27)
    b = ingest(source_id="f1", source_type="cad", raw_text="Structure fire, smoke visible from building.", **I27)
    assert a is not b


def test_medical_call_joins_nearby_crash():
    reset_state()
    a = ingest(source_id="t1", source_type="cad", raw_text="Vehicle collision, lanes blocked.", **I27)
    b = ingest(source_id="m1", source_type="manual", raw_text="Patient with chest pain, EMS on scene.", **I27)
    assert a is b


def test_report_c_medical_elsewhere_stays_separate():
    reset_state()
    a = ingest(source_id="t1", source_type="cad", raw_text="Vehicle collision, 2 injuries.", **I27)
    c = ingest(source_id="m2", source_type="cad", raw_text="Adult male collapsed near Buddy Holly and Broadway, patient conscious.",
               lat=33.584, lng=-101.847)
    assert a is not c


def test_ingest_validation():
    from fastapi.testclient import TestClient
    from backend.main import app
    c = TestClient(app)
    ok = {"source_id": "v1", "source_type": "cad", "raw_text": "Crash", "lat": 33.5, "lng": -101.8}
    assert c.post("/ingest", json=ok).status_code == 200
    assert c.post("/ingest", json={**ok, "lat": 999}).status_code == 422
    assert c.post("/ingest", json={**ok, "raw_text": ""}).status_code == 422
    assert c.post("/ingest", json={**ok, "source_type": "bogus"}).status_code == 422
    bad = dict(ok); del bad["lat"]
    assert c.post("/ingest", json=bad).status_code == 422
