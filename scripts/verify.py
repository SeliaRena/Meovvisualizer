from __future__ import annotations

import argparse
import importlib.util
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class Check:
    name: str
    command: tuple[str, ...]
    required_module: str | None = None


def _run(check: Check, env: dict[str, str]) -> bool:
    print(f"\n== {check.name} ==")
    if check.required_module and importlib.util.find_spec(check.required_module) is None:
        print(f"missing required tool: {check.required_module}")
        return False
    return subprocess.run(check.command, cwd=ROOT, env=env, check=False).returncode == 0


def _environment() -> dict[str, str]:
    env = os.environ.copy()
    source = str(ROOT / "src")
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = source if not existing else source + os.pathsep + existing
    env.setdefault("QT_QPA_PLATFORM", "offscreen")
    return env


def _qml_check(*, strict: bool, env: dict[str, str]) -> bool:
    qml_files = [str(path) for path in (ROOT / "src").rglob("*.qml")]
    if not qml_files:
        return True

    print("\n== qmllint ==")
    executable = shutil.which("qmllint")
    if executable:
        return (
            subprocess.run((executable, *qml_files), cwd=ROOT, env=env, check=False).returncode == 0
        )

    message = "qmllint unavailable; install Qt tooling to lint QML"
    print(message)
    return not strict


def main() -> int:
    parser = argparse.ArgumentParser(description="Run repository quality gates")
    parser.add_argument("--fast", action="store_true", help="run tests and smoke checks only")
    parser.add_argument(
        "--ci", action="store_true", help="treat missing optional tooling as failure"
    )
    args = parser.parse_args()

    python = sys.executable
    env = _environment()
    checks: list[Check] = []
    if not args.fast:
        checks.extend(
            [
                Check("ruff format", (python, "-m", "ruff", "format", "--check", "."), "ruff"),
                Check("ruff lint", (python, "-m", "ruff", "check", "."), "ruff"),
                Check(
                    "pyright",
                    (python, "-m", "pyright", "--pythonpath", python),
                    "pyright",
                ),
            ]
        )
    checks.extend(
        [
            Check("pytest", (python, "-m", "pytest"), "pytest"),
            Check("core smoke", (python, "scripts/smoke_test.py")),
        ]
    )

    gui_smoke = ROOT / "scripts" / "gui_smoke_test.py"
    if gui_smoke.exists():
        checks.append(Check("GUI smoke", (python, str(gui_smoke))))

    results = [_run(check, env) for check in checks]
    results.append(_qml_check(strict=args.ci, env=env))

    if all(results):
        print("\nAll required checks passed.")
        return 0

    print("\nOne or more required checks failed.")
    if not args.fast:
        print('Install development tools with: python -m pip install -e ".[dev,gui]"')
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
