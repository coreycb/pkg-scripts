#!/usr/bin/env python3
#
# Push stable branches for stable/ussuri
# (requires projects-push file with list of projects, one name per line)
#
# Example: pkg-push-stable-ussuri-branches ~/src/scripts/packaging/projects
#

import argparse
import os
import subprocess

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("projects", help="Path to projects file")
    args = parser.parse_args()

    with open(args.projects, "r") as f:
        for line in f.readlines():
            project = line.rstrip()
            print("Processing project: {}".format(project))
            saved_path = os.getcwd()
            os.chdir(project)
            cmd = ['git', 'checkout', 'stable/ussuri']
            subprocess.check_call(cmd)
            cmd = ['git', 'push', '--all']
            subprocess.check_call(cmd)
            os.chdir(saved_path)

if __name__ == "__main__":
    main()
