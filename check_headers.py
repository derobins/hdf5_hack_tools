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

# A dictionary that maps package names to descriptive text
package_text = {
    'H5'   : 'Generic Functions',
    'H5A'  : 'Attributes',
    'H5AC' : 'Metadata Cache',
    'H5B'  : 'B-Trees (Version 1)',
    'H5B2' : 'B-Trees (Version 2)',
    'H5C'  : 'Cache',
    'H5CS' : 'Function Stack',
    'H5CX' : 'API Contexts',
    'H5D'  : 'Datasets',
    'H5E'  : 'Error Handling',
    'H5EA' : 'Extensible Arrays',
    'H5F'  : 'Files',
    'H5FA' : 'Fixed Arrays',
    'H5FD' : '(Virtual) File Drivers',
    'H5FL' : 'Free Lists',
    'H5FO' : 'File Objects',
    'H5FS' : 'Free Space Management',
    'H5G'  : 'Groups',
    'H5HF' : 'Fractal Heaps',
    'H5HG' : 'Global Heaps',
    'H5HL' : 'Local Heaps',
    'H5HP' : 'Heaps',
    'H5I'  : 'Identifiers',
    'H5L'  : 'Links',
    'H5MF' : 'File Memory Management',
    'H5MM' : 'Memory Management',
    'H5MP' : 'Memory Pools',
    'H5O'  : 'Object Headers',
    'H5P'  : 'Property Lists',
    'H5PB' : 'Page Buffering',
    'H5PL' : 'Plugins',
    'H5R'  : 'References',
    'H5RS' : 'Reference-Counted Strings',
    'H5S'  : 'Dataspaces',
    'H5SL' : 'Skip Lists',
    'H5SM' : 'Shared Object Header Messages',
    'H5ST' : 'Ternary Search Trees',
    'H5T'  : 'Datatypes',
    'H5TS' : 'Thread-Safety',
    'H5UC' : 'Reference-Counted Buffers',
    'H5VL' : 'Virtual Object Layer',
    'H5VM' : 'Vector Functions',
    'H5WB' : 'Wrapped Buffers',
    'H5Z'  : 'Data Filters'
}

# A regular expression to pull out package names from strings
pkg_re = re.compile(r'(H5[A-Z][A-Z2]?)')

def process_line(line, this_package, destination_set) :

    packages = pkg_re.findall(line)

    for pkg in packages :
        if pkg in package_text :
            destination_set.add(pkg)

def print_set(string, set_to_print) :
    if len(set_to_print) > 0 :
        print(string)
        print(sorted(list(set_to_print)))


def process_file(filename) :

    # Ignore module headers, which should not require any included headers
    if "module" in filename :
        return

    # H5private will not match
    this_package = pkg_re.findall(filename)
    if len(this_package) > 0 :
        this_package = this_package[0]
    else :
        return

    required_packages = set()
    included_headers = set()
    friends = set()

    with open(filename, 'r') as f :

        for line in f :
            if "#include" in line :
                process_line(line, this_package, included_headers)
            elif "FRIEND" in line:
                process_line(line, this_package, friends)
            else :
                process_line(line, this_package, required_packages)

    useless_headers = included_headers - required_packages
    missing_headers = required_packages - included_headers

#   Print all headers for initial fixup. Change back later.
#    if len(useless_headers) > 0 or len(missing_headers) > 0 :
    print(filename)
    if len(friends) > 0 :
        print_set("FRIENDS", friends)
    if len(useless_headers) > 0 :
        print_set("USELESS HEADERS", useless_headers)
    if len(missing_headers) > 0 :
        print_set("MISSING HEADERS", missing_headers)
    generate_header_block(filename, this_package, required_packages, friends)
    print()

def generate_header_block(filename, this_package, packages, friends) :

    print("PROPOSED HEADER BLOCK")
    print("CHECK TO ENSURE THEY ARE REALLY NEEDED!!!")

    # H5private.h always comes first
    generate_header("H5", this_package, filename, friends)
 
    for p in sorted(list(packages)) :
        generate_header(p, this_package, filename, friends)

# NB - filename and friends probably at the wrong abstraction layer...
def generate_header(package, this_package, filename, friends) :
    # Start of open comment at column 33
    col_1 = 33
    # Start of close comment at column 77
    col_2 = 77

    # What kind of file is this?
    is_private = "private.h" in filename;
    is_pkg     = "pkg.h"     in filename;
    is_public  = "public.h"  in filename;
    is_src     = ".c"        in filename;

    text = ""

    if is_public :
        # Public headers always include other public headers
        # They do NOT include a header for their own package
        if package != this_package :
            text = "#include \"" + package + "public.h\""
    elif is_private :
        # Private headers always include private headers
        # They do NOT include a header for their own package
        if package != this_package :
            text = "#include \"" + package + "private.h\""
    elif is_pkg :
        # Package headers always include private headers
        # They DO include a header for their own package
        text = "#include \"" + package + "private.h\""
    else :
        # Source files include private headers
        # They include pkg headers for their own package and friends
        if package == this_package or package in friends :
            text = "#include \"" + package + "pkg.h\""
        else :
            text = "#include \"" + package + "private.h\""

    if text == "" :
        return

    # Space between include file name and start of comment
    spaces_1 = " " * (col_1 - len(text) - 1)

    text = text + spaces_1 + "/* " + package_text[package]

    # Space between comment text and end of comment
    spaces_2 = " " * (col_2 - len(text) - 1)

    text = text + spaces_2 + "*/"

    print(text)

def main() :

    print("HDF5 header check program")
    print("BE CAREFUL OF DEFINED CONSTANTS!!!")
    print("H5Fprivate.h, for example defines H5X constants")
    print("so you don't need those header files.")
    print()

    for filename in sys.argv[1:] :
        process_file(filename)

if __name__ == "__main__" :
    main()
