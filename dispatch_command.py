#!/usr/bin/env python
"""
Run dispatch command for OS / and release
"""
import argparse
import os

# templates for 'gh' command
templates = {
        "watertap": "gh workflow run .github/workflows/build-dispatch.yml -f project=watertap -f os-version={os}-latest -f artifact-name=WaterTAP-Flowsheet-Processor -f pip-install-target=watertap@git+https://github.com/watertap-org/watertap@{release}",
        "idaes": "gh workflow run .github/workflows/build-dispatch.yml -f project=idaes -f os-version={os}-latest -f artifact-name=IDAES-Flowsheet-Processor -f pip-install-target=idaes-pse@git+https://github.com/IDAES/idaes-pse@{release}",
        "prommis": "gh workflow run .github/workflows/build-dispatch.yml -f project=prommis -f os-version={os}-latest -f artifact-name=PROMMIS-Flowsheet-Processor -f pip-install-target=prommis@git+https://github.com/prommis/prommis@{release}"
        }

def main():
    p = argparse.ArgumentParser()
    p.add_argument("os", choices=["windows", "macos"], help="target operating system")
    p.add_argument("project", choices=["watertap", "idaes", "prommis"], help="target project")
    p.add_argument("--release", "-r", default="main", help="release tag (default=main)", metavar="TAG")
    p.add_argument("--norun", "-n", action="store_true", help="do not attempt to run command, just print it")
    args = p.parse_args()
    #
    t = templates[args.project].format(os=args.os, release=args.release)
    print("COMMAND:")
    print(t)
    if args.norun:
        return
    answer = input("RUN (y/N)?")
    if answer.lower() == "y":
        exec_args = t.split()
        os.execvp("gh", exec_args)

if __name__ == "__main__":
    main()

