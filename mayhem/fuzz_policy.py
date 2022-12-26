#!/usr/bin/env python3

import atheris
import sys
import fuzz_helpers

with atheris.instrument_imports(include=['parliament']):
    from parliament import analyze_policy_string

def TestOneInput(data):
    fdp = fuzz_helpers.EnhancedFuzzedDataProvider(data)
    analyzed_policy = analyze_policy_string(fdp.ConsumeRemainingString())
    for _ in analyzed_policy.findings:
        pass

def main():
    atheris.Setup(sys.argv, TestOneInput)
    atheris.Fuzz()


if __name__ == "__main__":
    main()
