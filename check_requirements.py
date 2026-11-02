import sys
import os
import urllib.request
import urllib.error
import json
from packaging.specifiers import SpecifierSet
from packaging.version import Version

PYPI = "https://pypi.org/pypi"
PYTHON = "3.11"


def get(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError:
        return None


def compatible(requires_python):
    if not requires_python:
        return True
    return Version(PYTHON) in SpecifierSet(requires_python)


def min_version(requires_python):
    if not requires_python:
        return None
    for s in SpecifierSet(requires_python):
        if ">=" in s.operator:
            return Version(str(s.version))
    return None


# --- read requirements file (default: requirements.txt next to this script) ---
script_dir = os.path.dirname(os.path.abspath(__file__))
default_req = os.path.join(script_dir, "requirements.txt")
req_file = sys.argv[1] if len(sys.argv) > 1 else default_req
lines = open(req_file).read().splitlines()
lines = [l.strip() for l in lines if l.strip() and not l.startswith("#")]

not_found = 0
incompatible = 0
best_ver = None
best_label = ""

for line in lines:
    name, version = line.split("==")

    # check if this exact version exists
    data = get(f"{PYPI}/{name}/{version}/json")
    if data is None:
        not_found += 1
        continue

    req_py = data["info"].get("requires_python") or ""

    if not compatible(req_py):
        incompatible += 1

    mv = min_version(req_py)
    if mv and (best_ver is None or mv > best_ver):
        best_ver = mv
        best_label = f"{name}=={version} (>={mv})"

print(f"Dependencies checked: {len(lines)}")
print(f"Not found on PyPI: {not_found}")
print(f"Incompatible with Python 3.11: {incompatible}")
print(f"Highest requirement: {best_label or 'none'}")
