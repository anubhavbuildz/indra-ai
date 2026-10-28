"""Download pinned Linux/amd64 QA CLIs; verify release checksums before extraction."""

import hashlib
import io
import tarfile
import urllib.request
from pathlib import Path

TOOLS = {
    "actionlint": (
        "rhysd/actionlint",
        "1.7.7",
        "actionlint_1.7.7_linux_amd64.tar.gz",
        "actionlint_1.7.7_checksums.txt",
    ),
    "gitleaks": (
        "gitleaks/gitleaks",
        "8.24.3",
        "gitleaks_8.24.3_linux_x64.tar.gz",
        "gitleaks_8.24.3_checksums.txt",
    ),
    "trivy": (
        "aquasecurity/trivy",
        "0.76.1",
        "trivy_0.76.1_Linux-64bit.tar.gz",
        "trivy_0.76.1_checksums.txt",
    ),
}


def install():
    destination = Path("/tmp/indra-qa-bin")
    destination.mkdir(exist_ok=True)
    for name, (repository, version, archive, sums) in TOOLS.items():
        base = f"https://github.com/{repository}/releases/download/v{version}/"
        with urllib.request.urlopen(base + sums, timeout=60) as response:
            checksums = response.read().decode()
        expected = next(
            line.split()[0] for line in checksums.splitlines() if line.endswith(archive)
        )
        with urllib.request.urlopen(base + archive, timeout=60) as response:
            data = response.read()
        if hashlib.sha256(data).hexdigest() != expected:
            raise ValueError(f"Checksum mismatch: {name}")
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as package:
            member = next(m for m in package.getmembers() if m.name in {name, f"./{name}"})
            stream = package.extractfile(member)
            if stream is None:
                raise ValueError(f"Missing binary: {name}")
            (destination / name).write_bytes(stream.read())
        (destination / name).chmod(0o755)
        print(f"Verified {name} {version}: {destination / name}")


if __name__ == "__main__":
    install()
