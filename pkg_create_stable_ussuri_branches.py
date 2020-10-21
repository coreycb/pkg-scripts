#!/usr/bin/env python3
#
# Create stable branches for stable/ussuri
# (requires projects file with list of projects, one name per line)
#
# Example: pkg-create-stable-ussuri-branches ~/src/scripts/packaging/projects
#

import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projects", help="Path to projects file")
    args = parser.parse_args()

    with open(args.projects, "r") as f:
        for line in f.readlines():
            project = line.rstrip()
            cmd = ['pkg-create-stable-branch', project, 'stable/ussuri']
            try:
                subprocess.check_call(cmd)
            except subprocess.CalledProcessError:
                continue

if __name__ == "__main__":
    main()
