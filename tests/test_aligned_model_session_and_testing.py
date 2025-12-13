from scripts.aligned_model import AlignedModel


def test_session_resume() -> None:
    model = AlignedModel("t", {"AS1": "..."})
    res = model._simulate_session_management("resume", "last")
    assert isinstance(res, str)
    assert "resum" in res.lower()


def test_testing_and_iteration_returns_string() -> None:
    model = AlignedModel("t", {"AS1": "..."})
    out = model._simulate_testing_and_iteration("run tests", max_cycles=2)
    assert isinstance(out, str)
    assert "Test" in out or "Tests" in out or "Task" in out
