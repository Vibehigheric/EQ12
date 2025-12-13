import importlib.util
from pathlib import Path


def load_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location("graphics_alert", str(path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_generate_graphic(tmp_path) -> None:
    base = Path("C:/EQ12/graphics/graphics_alert.py")
    assert base.exists(), f"Expected graphics module at {base}"
    mod = load_module_from_path(base)

    data = {"id": "t1", "title": "Test Deal", "merchant": "Store", "price": "$1.23"}
    out = tmp_path / "out.png"
    res = mod.generate_graphic(data, template=None, out_path=str(out))
    assert Path(res).exists()
    assert Path(res).stat().st_size > 0
