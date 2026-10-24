from colombia_dev.projections import ProjectionConfig, project, forecast_error

def test_reproducibility():
    cfg = ProjectionConfig(paths=200, years=3)
    assert project(cfg) == project(cfg)

def test_ordering():
    for row in project(ProjectionConfig(paths=200, years=4)):
        assert row["p05"] <= row["p50"] <= row["p95"]
        assert row["p05"] > 0

def test_zero_volatility():
    rows = project(ProjectionConfig(paths=100, years=3, annual_volatility=0))
    assert all(abs(r["p95"]-r["p05"]) < 1e-10 for r in rows)

def test_error_metrics():
    assert forecast_error([1,2,3],[1,2,3]) == {"mae": 0.0, "rmse": 0.0}
