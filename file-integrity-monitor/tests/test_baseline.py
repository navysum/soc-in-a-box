import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from baseline import calculate_sha256, build_baseline


def test_calculate_sha256(tmp_path):
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello", encoding="utf-8")

    result = calculate_sha256(test_file)

    assert result == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_build_baseline(tmp_path):
    test_file = tmp_path / "config.txt"
    test_file.write_text("trusted config", encoding="utf-8")

    baseline = build_baseline(tmp_path)

    assert str(test_file) in baseline
    assert len(baseline[str(test_file)]) == 64