import pytest
from wraith_cli.main import main

def test_argparse_validation(monkeypatch):
    from wraith_cli.main import _uint8
    import argparse

    # Test _uint8 directly
    assert _uint8("0") == 0
    assert _uint8("255") == 255
    assert _uint8("128") == 128

    with pytest.raises(argparse.ArgumentTypeError, match="out of range"):
        _uint8("256")

    with pytest.raises(argparse.ArgumentTypeError, match="out of range"):
        _uint8("-1")

    with pytest.raises(argparse.ArgumentTypeError, match="not a valid integer"):
        _uint8("abc")

def test_cli_help(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--help"])
    assert e.value.code == 0
    out, err = capsys.readouterr()
    assert "Wraith W75 vendor HID CLI" in out

def test_cli_invalid_rgb(capsys):
    # Test that invalid RGB values trigger argparse error and SystemExit
    for arg in ["--r", "--g", "--b", "--speed", "--brightness", "--direction"]:
        with pytest.raises(SystemExit) as e:
            main(["set-color", arg, "256", "--mode", "static"])
        assert e.value.code != 0
        out, err = capsys.readouterr()
        assert "out of range (0-255)" in err

def test_cli_invalid_int(capsys):
    with pytest.raises(SystemExit) as e:
        main(["set-color", "--r", "notanint", "--mode", "static"])
    assert e.value.code != 0
    out, err = capsys.readouterr()
    assert "is not a valid integer" in err
