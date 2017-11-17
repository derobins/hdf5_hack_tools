# Script to check that headers are included properly in HDF5 source code.
#
# Process directories or files, header and/or source
#
# Check that appropriate headers are included for any packages used in the
# files
#
# Make a list of forward declarations that are necessary in other header
# files
#
# In the future, perform the surgery automatically.

# To begin with, let's make a special purpose header emit script that
# deals with one file at a time, passed in via the command line.

import re
import sys


# A regular expression to pull out package names from strings
pkg_re = re.compile(r'(H5[A-Z][A-Z2]*)')

def process_line(line, destination_set) :

    packages = pkg_re.findall(line)

    for pkg in packages :
        destination_set.add(pkg)

def print_set(string, set_to_print) :
    if len(set_to_print) > 0 :
        print(string)
        print(sorted(list(set_to_print)))


def process_file(filename) :

    this_package = pkg_re.findall(filename)
    if len(this_package) > 0 :
        this_package = this_package[0] + '_'
    else :
        return

    required_packages = set()
    included_headers = set()

    with open(filename, 'r') as f :

        for line in f :
            if line.startswith('#include') :
                process_line(line, included_headers)
            else :
                process_line(line, required_packages)

    useless_headers = included_headers - required_packages
    missing_headers = required_packages - included_headers

    if len(useless_headers) > 0 or len(missing_headers) > 0 :
        print(filename)
        if len(useless_headers) > 0 :
            print_set("USELESS HEADERS", useless_headers)
        if len(missing_headers) > 0 :
            print_set("MISSING HEADERS", missing_headers)
        print()

def main() :

    print("HDF5 header check program")
    print()

    for filename in sys.argv[1:] :
        process_file(filename)

if __name__ == "__main__" :
    main()
