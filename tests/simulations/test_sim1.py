"""SIM-1 stays as registered, and the runner can still report a refutation (research/simulations/SIM1_PREREG.md)."""
import subprocess
import sys
from pathlib import Path

SIM = Path(__file__).resolve().parents[2] / "research" / "simulations" / "sim1.py"
REGISTERED_SHA256 = "aabad186eb7763a14c8ca21a23b36704e70b4cd6c936b3b17c57564a6a9fe12c"


def _sv_importable():
    p = subprocess.run([sys.executable, "-c", "import sovereign_veritas.workflow"], capture_output=True)
    return p.returncode == 0


def run(*args):
    return subprocess.run([sys.executable, str(SIM), *args], capture_output=True, text=True)


def test_registered_run_holds_and_reproduces_its_digest():
    p = run()
    assert p.returncode == 0, p.stdout
    if not _sv_importable():
        # Eunoia's own CI does not install sovereign-veritas: B2-B3c must say NOT RUN, never pass silently.
        assert p.stdout.count("NOT RUN (sovereign_veritas not importable)") == 4
        assert "VERDICT  19 of 19 as registered" in p.stdout
        return
    assert "VERDICT  23 of 23 as registered" in p.stdout
    assert f"RESULTS_SHA256 {REGISTERED_SHA256}" in p.stdout


def test_sabotage_is_seen():
    p = run("--sabotage")
    assert p.returncode == 1
    assert "A0   N=400 ALLOW=400" in p.stdout and "REFUTED" in p.stdout
