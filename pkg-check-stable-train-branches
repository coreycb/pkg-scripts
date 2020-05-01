#!/usr/bin/env python3
#
# Check if stable branches exist for stable/train
# (requires projects file with list of projects, one name per line)
#
# Example: pkg-check-stable-train-branches ~/src/scripts/packaging/projects
#

import argparse
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projects", help="Path to projects file")
    args = parser.parse_args()

    projs = args.projects
    with open(projs, 'r') as f, open('yes', 'w') as yes, open('no', 'w') as no:
        for line in f.readlines():
            project = line.rstrip()
            cmd = ['pkg-check-stable-branch', project, 'stable/train']
            if subprocess.call(cmd) == 0:
                yes.write("{}".format(line))
            else:
                no.write("{}".format(line))


if __name__ == "__main__":
    main()
