"""Validate Mermaid by rendering each source to an SVG preview in design/diagrams/."""

import json
import os
import subprocess
import tempfile
from pathlib import Path


def main():
    executable = os.environ.get("MERMAID_CLI", "/tmp/indra-mermaid/node_modules/.bin/mmdc")
    browser = os.environ.get("CHROMIUM_PATH")
    if not browser:
        candidates = list(
            (Path.home() / ".cache/ms-playwright").glob("chromium-*/chrome-linux/chrome")
        )
        if candidates:
            browser = str(sorted(candidates)[-1])
    config = {"args": ["--no-sandbox"]}
    if browser:
        config["executablePath"] = browser
    results = {}
    with tempfile.TemporaryDirectory(prefix="indra-mermaid-") as temporary:
        configuration = Path(temporary) / "puppeteer.json"
        configuration.write_text(json.dumps(config))
        for source in sorted(Path("design/diagrams").glob("*.mmd")):
            command = [
                executable,
                "-i",
                str(source),
                "-o",
                str(source.with_suffix(".svg")),
                "-p",
                str(configuration),
                "-b",
                "transparent",
            ]
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=60, check=False
                )
                results[source.name] = {
                    "exit_code": result.returncode,
                    "output": result.stdout + result.stderr,
                }
            except (OSError, subprocess.TimeoutExpired) as error:
                results[source.name] = {"exit_code": 127, "output": str(error)}
    evidence = Path("design/qa/evidence")
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / "diagram-validation.json").write_text(json.dumps(results, indent=2))
    print(json.dumps({name: value["exit_code"] for name, value in results.items()}, indent=2))
    return int(any(value["exit_code"] for value in results.values()))


if __name__ == "__main__":
    raise SystemExit(main())
