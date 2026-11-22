# Copyright (c) 2026 Tanvir. ClipDude project tests.
import pytest
from fastapi.testclient import TestClient

from app import main

YT = "https://www.youtube.com/watch?v=abc123"


@pytest.fixture
def client(monkeypatch):
    submitted = []
    monkeypatch.setattr(main._pool, "submit", lambda fn, *a: submitted.append(a))  # never run the pipeline
    monkeypatch.setattr(main, "_jobs", {})
    c = TestClient(main.app)
    c.submitted = submitted
    return c


def test_status_reports_styles(client):
    data = client.get("/api/status").json()
    assert set(data["styles"]) == {"yellow", "green", "beast", "anton", "bebas", "clean", "reveal", "cyan", "pink", "minimal", "neon", "classic"}
    look = data["style_looks"]["yellow"]
    assert look["font"] == "Arial Black" and look["upper"] is True and look["active"].startswith("#")
    assert "missing" in data


def test_create_job_queues_it(client):
    res = client.post("/api/jobs", json={"url": YT, "clip_count": 3})
    assert res.status_code == 200
    job = res.json()
    assert job["status"] == "queued" and job["options"]["clip_count"] == 3
    assert len(client.submitted) == 1
    assert client.get(f"/api/jobs/{job['id']}").json()["id"] == job["id"]


@pytest.mark.parametrize("body, message", [
    ({"url": "https://example.com/video"}, "YouTube"),
    ({"url": YT, "min_len": 60, "max_len": 30}, "shorter"),
    ({"url": YT, "style": "rainbow"}, "caption style"),
    ({"url": YT, "layout": "zoom"}, "layout"),
])
def test_create_job_rejects_bad_input(client, body, message):
    res = client.post("/api/jobs", json=body)
    assert res.status_code == 400
    assert message in res.json()["detail"]
    assert client.submitted == []


def test_clip_count_is_bounded(client):
    assert client.post("/api/jobs", json={"url": YT, "clip_count": 1001}).status_code == 422


def test_short_links_are_accepted(client):
    assert client.post("/api/jobs", json={"url": "https://youtu.be/abc123"}).status_code == 200


def test_unknown_job_is_404(client):
    assert client.get("/api/jobs/nope").status_code == 404


def test_cannot_delete_running_job(client):
    job = client.post("/api/jobs", json={"url": YT}).json()
    assert client.delete(f"/api/jobs/{job['id']}").status_code == 409


def test_delete_finished_job(client):
    job = client.post("/api/jobs", json={"url": YT}).json()
    main._jobs[job["id"]]["status"] = "done"
    assert client.delete(f"/api/jobs/{job['id']}").json() == {"ok": True}
    assert client.get(f"/api/jobs/{job['id']}").status_code == 404


def _finished_job_with_clips(client, n=3):
    job = client.post("/api/jobs", json={"url": YT}).json()
    d = main._job_dir(job["id"])
    d.mkdir(parents=True, exist_ok=True)
    clips = []
    for i in range(n):
        name = f"clip_{i + 1:02d}"
        (d / f"{name}.mp4").write_bytes(b"v")
        (d / f"{name}.jpg").write_bytes(b"j")
        clips.append({"title": name, "video": f"/media/{job['id']}/{name}.mp4", "thumb": f"/media/{job['id']}/{name}.jpg"})
    main._jobs[job["id"]].update(status="done", clips=clips)
    return job["id"], d


def test_delete_one_clip_removes_it_and_its_files(client):
    job_id, d = _finished_job_with_clips(client)
    assert client.delete(f"/api/jobs/{job_id}/clips/1").json() == {"ok": True}
    titles = [c["title"] for c in client.get(f"/api/jobs/{job_id}").json()["clips"]]
    assert titles == ["clip_01", "clip_03"]
    assert not (d / "clip_02.mp4").exists() and not (d / "clip_02.jpg").exists()
    assert (d / "clip_01.mp4").exists()


def test_delete_clip_out_of_range_is_404(client):
    job_id, _ = _finished_job_with_clips(client, 1)
    assert client.delete(f"/api/jobs/{job_id}/clips/5").status_code == 404


def test_cannot_delete_clip_while_job_runs(client):
    job_id, _ = _finished_job_with_clips(client)
    main._jobs[job_id]["status"] = "running"
    assert client.delete(f"/api/jobs/{job_id}/clips/0").status_code == 409




def test_only_one_video_job_can_run_at_a_time(client):
    first = client.post("/api/jobs", json={"url": YT})
    assert first.status_code == 200
    second = client.post("/api/jobs", json={"url": YT})
    assert second.status_code == 409
    main._jobs[first.json()["id"]]["status"] = "done"
    third = client.post("/api/jobs", json={"url": YT})
    assert third.status_code == 200


def test_custom_clipdude_render_options_are_saved(client):
    res = client.post("/api/jobs", json={
        "url": YT,
        "aspect": "21:9",
        "watermark": "Tanvir",
        "watermark_position": "top-left",
        "watermark_motion": True,
        "part_numbers": True,
        "caption_position": "middle",
        "caption_min_duration": 0.35,
        "extra_instructions": "Prefer practical explanations.",
    })
    assert res.status_code == 200
    options = res.json()["options"]
    assert options["aspect"] == "21:9"
    assert options["watermark"] == "Tanvir" and options["watermark_position"] == "top-left"
    assert options["watermark_motion"] is True and options["part_numbers"] is True
    assert options["caption_position"] == "middle" and options["caption_min_duration"] == 0.35
    assert options["extra_instructions"] == "Prefer practical explanations."


def test_api_accepts_full_video_subtitle_mode(client):
    res = client.post("/api/jobs", json={
        "url": YT,
        "mode": "subtitles",
        "subtitle_style": "beast",
        "aspect": "original",
        "start_time": 12.5,
        "end_time": 80,
    })
    assert res.status_code == 200
    options = res.json()["options"]
    assert options["mode"] == "subtitles"
    assert options["subtitle_style"] == "beast"
    assert options["aspect"] == "original"
    assert options["start_time"] == 12.5 and options["end_time"] == 80


def test_api_rejects_unknown_subtitle_style(client):
    res = client.post("/api/jobs", json={"url": YT, "mode": "subtitles", "subtitle_style": "rainbow"})
    assert res.status_code == 400
    assert "caption style" in res.text


def test_api_rejects_overlapping_subtitle_cut_ranges(client):
    res = client.post("/api/jobs", json={
        "url": YT, "mode": "subtitles", "cut_ranges": [[10, 25], [20, 30]]
    })
    assert res.status_code == 400
    assert "cannot overlap" in res.text


def test_full_video_subtitle_pipeline_renders_one_continuous_range(client, monkeypatch, tmp_path):
    from app.source import Source, Word

    response = client.post("/api/jobs", json={
        "url": YT,
        "mode": "subtitles",
        "subtitle_style": "beast",
        "aspect": "original",
        "start_time": 2,
        "end_time": 7,
        "cut_ranges": [[4, 5]],
    })
    assert response.status_code == 200
    job_id = response.json()["id"]
    req = client.submitted[0][1]
    source_video = tmp_path / "source.mp4"
    source_video.write_bytes(b"placeholder")
    src = Source(
        video_path=source_video,
        title="Test full video",
        duration=10,
        language="en",
        words=[Word("first", 0.2, 0.6), Word("middle", 3, 3.5), Word("last", 8, 8.5)],
        transcript_source="whisper",
    )
    captured = {}
    monkeypatch.setattr(main.source, "download", lambda *args, **kwargs: src)

    def fake_render(video, words, start, end, out_dir, name, **kwargs):
        captured.update(start=start, end=end, words=words, **kwargs)
        return {"layout": "source", "length": end - start, "width": 640, "height": 360}

    monkeypatch.setattr(main.render, "render_clip", fake_render)
    main._run(job_id, req)

    job = main._jobs[job_id]
    assert job["status"] == "done"
    assert job["selection"] == "subtitles"
    assert len(job["clips"]) == 1
    assert captured["start"] == 2 and captured["end"] == 7
    assert captured["style"] == "beast"
    assert captured["aspect"] == "original"
    assert captured["keep"] == [(0.0, 2.0), (3.0, 5.0)]
