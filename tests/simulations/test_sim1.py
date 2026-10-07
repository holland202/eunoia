"""SIM-1 stays as registered, and the runner can still report a refutation (research/simulations/SIM1_PREREG.md)."""
import subprocess
import sys
from pathlib import Path

SIM = Path(__file__).resolve().parents[2] / "research" / "simulations" / "sim1.py"
REGISTERED_SHA256 = "aabad186eb7763a14c8ca21a23b36704e70b4cd6c936b3b17c57564a6a9fe12c"


def run(*args):
    return subprocess.run([sys.executable, str(SIM), *args], capture_output=True, text=True)


def test_registered_run_holds_and_reproduces_its_digest():
    p = run()
    assert p.returncode == 0, p.stdout
    assert "VERDICT  23 of 23 as registered" in p.stdout
    assert f"RESULTS_SHA256 {REGISTERED_SHA256}" in p.stdout


def test_sabotage_is_seen():
    p = run("--sabotage")
    assert p.returncode == 1
    assert "A0   N=400 ALLOW=400" in p.stdout and "REFUTED" in p.stdout
