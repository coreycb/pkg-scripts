#!/usr/bin/python3
#
# Updates debian/control (Build-)Depends(-Indep) based on
# (test-)requirements.txt and doc/requirements.txt. Must be
# run in the root directory of the package.
#
# Example: pkg-update-deps bionic
#

import argparse
import logging as log
import os
import shutil
import tempfile
import subprocess


cpython3 = '/usr/share/dh-python/dist/cpython3_fallback'
req_files = ['requirements.txt', 'test-requirements.txt',
             'driver-requirements.txt',  # ironic uses this
             os.path.join('doc', 'requirements.txt')]

indent = None
tmp_dir = tempfile.mkdtemp()
packages = []
build_depends_packages = []
depends_packages = []


def get_ubuntu_package_name(upstream_name):
    '''
    Return Ubuntu package name based on upstream package name.
    If Ubuntu package name is not found, returns 'ENOTFOUND'.
    '''
    pkg_name = 'ENOTFOUND'
    cpython_file = cpython3

    try:
        with open(cpython_file, 'r') as cpython_fp:
            for line in cpython_fp:
                line_upstream = line.split(' ')[0].rstrip()
                line_upstream_underscore = line_upstream.replace("_", "-")

                if line_upstream.lower() == upstream_name.lower():
                    pkg_name = line.split(' ')[1].rstrip()
                    break
                elif line_upstream_underscore.lower() == upstream_name.lower():
                    pkg_name = line.split(' ')[1].rstrip()
                    break
    except FileNotFoundError:
        log.critical("Please install dh_python before running this script")
        raise

    if pkg_name == 'ENOTFOUND':
        python_version = 'python3'
        log.warning("Could not find {} Ubuntu package name for upstream "
                    "python package: {}".format(python_version, upstream_name))

    return pkg_name


def rmadison(packages):
    '''
    Calls rmadison on the package list and writes the results to the temp
    directory as rmadison.txt.
    '''
    results = subprocess.run(["rmadison", ' '.join(packages)], check=True,
                             stdout=subprocess.PIPE)
    rmad_file = os.path.join(tmp_dir, "rmadison.txt")
    with open(rmad_file, 'w') as fp_out:
        fp_out.write(results.stdout.decode("utf-8"))


def find_package_line_in_req_file(req_file, pkg_name):
    '''
    Searches for a package in a requirements file. If the package is found,
    its line in the requirements file is returned. Otherwise None is returned.
    '''
    if not os.path.isfile(req_file):
        return None

    with open(req_file, 'r') as req_fp:
        for line in req_fp:
            pkg_name_req = line.split('(')[0].strip()
            if pkg_name == pkg_name_req:
                return line
    return None


def swap_package_name_and_min_version(line, upstream_name, pkg_name,
                                      has_min_version):
    '''
    Given a line from a requirements file, replaces the upstream name with
    the Ubuntu package name, and retains only the minimum required version.
    Also keeps a list of Ubuntu package names for later use by rmadison.
    '''
    if pkg_name == "ENOTFOUND":
        output_line = line.replace(upstream_name,
                                   "ENOTFOUND({})".format(upstream_name))
        return output_line.rstrip()

    if has_min_version:
        try:
            min_version = line.split('>=')[1].split(',')[0].rstrip()
        except IndexError:
            log.warning("Unable to find min version in line: {}. Will "
                        "use pinned version as min version in control file."
                        "".format(line.rstrip()))
            try:
                min_version = line.split('==')[1].split(',')[0].rstrip()
            except IndexError:
                log.warning("Unable to find pinned version in line: {}. Will "
                            "not specify version in control file."
                            "".format(line.rstrip()))
                output_line = "{}".format(pkg_name)
                packages.append(pkg_name)
                return output_line
        output_line = "{} (>= {})".format(pkg_name, min_version)
        packages.append(pkg_name)
    else:
        output_line = "{}".format(pkg_name)
        packages.append(pkg_name)
    return output_line


def process_requirements_files_phase1():
    '''
    Process the (test-)requirements.txt and doc/requirements.txt files in the
    current directory by stripping comments, replacing upstream package names
    with py3 Ubuntu package names, and retaining only the minimum
    required version. The updated requirements files are written to the temp
    directory as (test-)requirements.txt.phase1 and
    doc/requirements.txt.phase1. Finally rmadison is called with the Ubuntu
    package list.
    '''

    for req_file in req_files:
        req_file_out = os.path.join(tmp_dir, '{}.phase1'.format(req_file))

        if not os.path.isfile(req_file):
            log.warning("requirement file not found: {}".format(req_file))
            continue

        if os.path.dirname(req_file) == 'doc':
            doc_dir = os.path.join(tmp_dir, 'doc')
            if not os.path.exists(doc_dir):
                os.mkdir(doc_dir)

        with open(req_file, 'r') as fp_in, open(req_file_out, 'w') as fp_out:
            for line in fp_in:
                # Skip empty and commented lines
                if not line.strip() or line.strip().startswith('#'):
                    continue

                # Strip trailing comments and determine first operator index
                line = line.split('#')[0]
                line = line.split(';')[0]
                indexes = sorted([line.find('>'), line.find('<'),
                                  line.find('!'), line.find('=')])
                indexes = [x for x in indexes if x >= 0]
                try:
                    upstream_name = line[0:indexes[0]]
                    has_min_version = True
                except IndexError:
                    log.warning("Version specifier not found in line: "
                                "{}".format(line.rstrip()))
                    upstream_name = line.split(' ')[0].rstrip()
                    has_min_version = False

                pkg_name_py3 = get_ubuntu_package_name(upstream_name)
                for pkg_name in [pkg_name_py3]:
                    out_line = swap_package_name_and_min_version(line,
                                                                 upstream_name,
                                                                 pkg_name,
                                                                 has_min_version)  # noqa
                    fp_out.write(out_line + '\n')

    rmadison(packages)


def process_requirements_files_phase2(release):
    '''
    Process the (test-)requirements.txt.phase1 and doc/requirements.txt.phase1
    files in the temp directory by adjusting the min version to include the
    Ubuntu package epoch if the rmadison output has an epoch for the package.
    The updated requirements files are written to the temp directory as
    (test-)requirements.txt.phase2 and doc/requirements.txt.phase2.
    '''
    rmad_file = os.path.join(tmp_dir, "rmadison.txt")

    for req_f in req_files:
        req_f_in = os.path.join(tmp_dir, '{}.phase1'.format(req_f))
        req_f_out = os.path.join(tmp_dir, '{}.phase2'.format(req_f))

        if not os.path.isfile(req_f):
            continue

        with open(req_f_in, 'r') as fp_in, open(req_f_out, 'w') as fp_out:
            for line in fp_in:
                found = False
                epoch_index = 0
                pkg_name = line.split('(')[0].rstrip()
                # Read rmadison output in reverse order to ensure we get
                # proposed versions first.
                for rmad_line in reversed(open(rmad_file, 'r').readlines()):
                    if pkg_name in rmad_line and release in rmad_line:
                        found = True
                        epoch_index = rmad_line.find(':')-1
                        break
                if epoch_index > 0:
                    out_line = line.replace("(>= ", "(>= {}:".format(
                        rmad_line[epoch_index]))
                else:
                    out_line = line
                if not found and pkg_name != "ENOTFOUND":
                    log.warning("{} not found for release "
                                "{}".format(pkg_name, release))
                fp_out.write(out_line)


def process_control_file_phase1():
    '''
    Process the debian/control file in the current directory by replacing
    min version for any existing dependencies with the min version from
    (test-)requirements.txt.phase2 or doc/requirements.txt.phase2. The
    updated control file is written to the temp directory as
    control.phase1. This function also collects 2 lists of packages, one
    for depends (from requirements.txt) and the other for build-depends
    (from (test-)requirements.txt and doc/requirements.txt).
    '''
    global indent

    control_file = 'debian/control'
    control_file_out = os.path.join(tmp_dir, 'control.phase1')
    req_f = os.path.join(tmp_dir, '{}.phase2'.format('requirements.txt'))
    treq_f = os.path.join(tmp_dir, '{}.phase2'.format('test-requirements.txt'))
    dreq_f = os.path.join(tmp_dir, 'doc', '{}.phase2'.format('requirements.txt'))  # noqa

    with open(control_file, 'r') as fp_in:
        with open(control_file_out, 'w') as fp_out:
            processing_deps = False

            for control_line in fp_in:
                start_of_depends_section = False
                if 'Build-Depends-Indep' in control_line:
                    section = 'Build-Depends-Indep'
                    start_of_depends_section = True
                elif 'Build-Depends' in control_line:
                    section = 'Build-Depends'
                    start_of_depends_section = True
                elif 'Depends' in control_line:
                    section = 'Depends'
                    start_of_depends_section = True

                if start_of_depends_section or not processing_deps:
                    fp_out.write(control_line)
                    if start_of_depends_section:
                        processing_deps = True
                    continue

                if control_line.startswith(" "):
                    # Must be a dependency - replace line in control file with
                    # package name and min version from
                    # (test-)requirements.txt.phase2 or
                    # doc/requirements.txt.phase2.
                    pkg_name = control_line.split(',')[0].split('(')[0].strip()
                    indent = control_line.split(pkg_name)[0]

                    out_line = find_package_line_in_req_file(req_f, pkg_name)
                    if not out_line:
                        if (section == 'Build-Depends' or
                                section == 'Build-Depends-Indep'):
                            out_line = find_package_line_in_req_file(treq_f,
                                                                     pkg_name)
                    if not out_line:
                        if (section == 'Build-Depends' or
                                section == 'Build-Depends-Indep'):
                            out_line = find_package_line_in_req_file(dreq_f,
                                                                     pkg_name)
                    if out_line:
                        fp_out.write(indent + out_line.rstrip() + ',\n')
                        if (section == 'Build-Depends' or
                                section == 'Build-Depends-Indep'):
                            build_depends_packages.append(pkg_name)
                        elif section == 'Depends':
                            depends_packages.append(pkg_name)
                    else:
                        fp_out.write(control_line)
                else:
                    # Must be a non-dependency line following a dependency
                    # section.
                    fp_out.write(control_line)
                    processing_deps = False


def process_control_file_phase2():
    '''
    Process the control.phase1 file in the temp directory by writing any new
    dependencies from (test-)requirements.txt or doc/requirements.txt that
    don't already exist in the control file. The updated control file is
    written to the temp directory as control.phase2 and to debian/control.
    '''
    global indent

    control_file_in = os.path.join(tmp_dir, 'control.phase1')
    control_file_out = os.path.join(tmp_dir, 'control.phase2')

    with open(control_file_in, 'r') as fp_in:
        with open(control_file_out, 'w') as fp_out:
            processing_new_deps = False

            for control_line in fp_in:
                if 'Build-Depends-Indep' in control_line:
                    fp_out.write(control_line)
                    processing_new_deps = True
                    continue

                if not processing_new_deps:
                    fp_out.write(control_line)
                    continue

                # Write the new deps
                new_dep_lines = []
                for req_f in req_files:

                    r_file = os.path.join(tmp_dir, '{}.phase2'.format(req_f))
                    if not os.path.isfile(r_file):
                        continue

                    with open(r_file, 'r') as fp_r:
                        for r_line in fp_r:
                            pkg_name = r_line.split('(')[0].strip()
                            if ((req_f == 'requirements.txt' and
                                    pkg_name not in depends_packages) or
                                (req_f == 'test-requirements.txt' and
                                    pkg_name not in build_depends_packages) or
                                (req_f == os.path.join('doc', 'requirements.txt') and  # noqa
                                    pkg_name not in build_depends_packages)):
                                new_dep_lines.append(indent + r_line)

                    fp_out.write("*** new {} deps (start)\n".format(req_f))
                    for line in sorted(new_dep_lines):
                        fp_out.write(line.rstrip() + ",\n")
                    fp_out.write("*** new {} deps (end) ***\n".format(req_f))

                fp_out.write(control_line)
                processing_new_deps = False

    # Finally copy the control.phase2 file to debian/control
    shutil.copyfile(control_file_out, 'debian/control')


def main():
    '''
    Process (test-)requirements.txt and doc/requirements.txt files and update
    debian/control file with updated version requirements.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("release", help="Ubuntu release code name")
    parser.add_argument("--debug", help="Enable verbose logging and retain "
                        "temp directory for debugging", action='store_true')
    args = parser.parse_args()

    loglevel = log.WARNING
    if args.debug:
        loglevel = log.DEBUG
    log.basicConfig(format='%(levelname)s: %(message)s', level=loglevel)

    process_requirements_files_phase1()
    process_requirements_files_phase2(args.release)

    process_control_file_phase1()
    process_control_file_phase2()

    if loglevel != log.DEBUG:
        shutil.rmtree(tmp_dir)

    log.info("Done! Check the temp directory for debugging: "
             "{}".format(tmp_dir))


if __name__ == "__main__":
    main()
