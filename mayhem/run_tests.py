#!/usr/bin/python3
"""run_tests.py — RUN parliament's own pytest suite and print a parseable summary.

Invoked via the `/mayhem/parliament-tests` ELF launcher (NOT directly), so the verify-repo
sabotage oracle can neuter the launcher and prove the test oracle is behavioral.

It runs the real suite (tests/unit/*.py — known-answer cases asserting that
analyze_policy_string(...).finding_ids / findings equal exact expected values), writes a
JUnit XML, parses the counts, and prints one line:

    RUNTESTS tests=<n> passed=<p> failed=<f> skipped=<s>

Exit 0 iff failed == 0. mayhem/test.sh parses that line into a CTRF report.
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET

import pytest

XML = "/tmp/parliament-junit.xml"
TESTS_DIR = "/mayhem/tests/unit"

# Known-broken on PRISTINE upstream HEAD (duo-labs/parliament @ ba58b69), independent of this
# integration: the bundled iam_definition.json makes expand_action("iAm:li*sTuS*rs") return
# `iam:ListUsers` TWICE, so this de-dup known-answer assertion (expects exactly 1) fails on
# upstream itself. Deselected so the oracle reflects upstream's real passing suite; the remaining
# 65 known-answer cases keep it behavioral (a no-op/exit(0) patch still fails).
DESELECT = [
    "tests/unit/test_action_expansion.py::TestActionExpansion::test_expand_action_with_casing",
]


def main() -> int:
    args = ["-q", "-p", "no:cacheprovider", TESTS_DIR, "--junitxml", XML]
    for nodeid in DESELECT:
        args += ["--deselect", nodeid]
    pytest.main(args)

    root = ET.parse(XML).getroot()
    suites = root.findall("testsuite") or ([root] if root.tag == "testsuite" else [])
    if not suites:
        print("RUNTESTS tests=0 passed=0 failed=1 skipped=0")
        return 1

    tests = failed = skipped = 0
    for s in suites:
        tests += int(s.get("tests", 0))
        failed += int(s.get("failures", 0)) + int(s.get("errors", 0))
        skipped += int(s.get("skipped", 0))
    passed = tests - failed - skipped

    print(f"RUNTESTS tests={tests} passed={passed} failed={failed} skipped={skipped}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
