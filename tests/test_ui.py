from app.ui import run_app


def test_ui_module_imports():
    assert callable(run_app)
