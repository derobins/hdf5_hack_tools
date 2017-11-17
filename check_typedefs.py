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

# A regular expression to pull out type names from strings
type_re = re.compile(r'(H5[A-Z][A-Z2]*\_\w+\_t)')

# A regular expression to pull out package names from strings
pkg_re = re.compile(r'(H5[A-Z][A-Z2]*)')

# All the types we found in all files
all_types_found = set()

def process_line(line, this_package, destination_set) :

    types = type_re.findall(line)

    for t in types :
        if not (this_package in t):
            destination_set.add(t)
            all_types_found.add(t)

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

    found_types = set()

    with open(filename, 'r') as f :

        for line in f :
            process_line(line, this_package, found_types)

    if len(found_types) > 0 :
        print(filename)
        print_set("FOUND TYPES", found_types)
        print()

def emit_typedefs(type_set) :
    for t in sorted(list(type_set)) :
        print("typedef struct " + t + ";")

def main() :

    print("HDF5 typedef check program")
    print()

    for filename in sys.argv[1:] :
        process_file(filename)

    print_set("ALL TYPES FOUND", all_types_found)

    emit_typedefs(all_types_found)

if __name__ == "__main__" :
    main()
