#!/usr/bin/env python
# **********************************************************************
#
# Copyright (c) 2003-2015 ZeroC, Inc. All rights reserved.
#
# This copy of Ice is licensed to you under the terms described in the
# ICE_LICENSE file included in this distribution.
#
# **********************************************************************

import os, sys, shutil, glob, fnmatch, string, re
from stat import *

#
# NOTE: See lib/DistUtils.py for default third-party locations and
# languages to be built on each platform.
#

iceVersion = "3.6.0"

distDir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(os.path.join(distDir, "lib"))
import DistUtils
from DistUtils import copy

make = "make"

#
# Defines which languages are to also be built in 64bits mode
#
# NOTE: makebindist.py doesn't currently support different third party locations
# for 32 and 64 bits. This is an issue on HP-UX for example where Bzip2 32bits is
# in /usr/local and in /opt for the 64bits version.
#
build_lp64 = { \
    'SunOS' : ['cpp'], \
}

#
# Program usage.
#
def usage():
    print "Usage: " + sys.argv[0] + " [options] tag"
    print
    print "Options:"
    print "-c    Clean previous build"
    print "-n    Don't build any language mapping"
    print "-h    Show this message."
    print "-v    Be verbose."

#
# Instantiate the gobal platform object with the given third-parties
#
thirdParties = [
    "BerkeleyDB", \
    "Expat", \
    "OpenSSL", \
    "Mcpp", \
    "Iconv", \
    "Proguard", \
    "JavaApplicationBundler"
]
platform = DistUtils.getPlatform(thirdParties)

#
# Check arguments
#
verbose = 0
forceclean = 0
nobuild = 0
buildLanguages = [ ]
for x in sys.argv[1:]:
    if x == "-h":
        usage()
        sys.exit(0)
    elif x == "-v":
        verbose = 1
    elif x == "-c":
        forceclean = 1
    elif x == "-n":
        nobuild = 1
    elif x.startswith("-"):
        print sys.argv[0] + ": unknown option `" + x + "'"
        print
        usage()
        sys.exit(1)
    else:
        if not x in platform.languages:
            print sys.argv[0] + ": language `" + x + "' not supported on this platform"
            print
            usage()
            sys.exit(1)
        buildLanguages.append(x)

if len(buildLanguages) == 0:
    buildLanguages = platform.languages

if nobuild:
    buildLanguages = []

if verbose:
    quiet = "v"
else:
    quiet = ""

#
# Ensure the script is being run from the dist directory.
#
cwd = os.getcwd()
if not os.path.exists(os.path.join(distDir, "src", "windows", "LICENSE.rtf")):
    print sys.argv[0] + ": you must run makebindist.py from the dist-" + iceVersion + " directory created by makedist.py"
    sys.exit(1)

print "Building Ice " + iceVersion + " binary distribution (" + platform.getPackageName("Ice", iceVersion) + ".tar.gz)"
print "Using the following third party libraries:"
if not platform.checkAndPrintThirdParties():
    print "error: some required third party dependencies were not found"
    sys.exit(1)

#
# Ensure that the source archive or directory exists and create the build directory.
#
buildRootDir = os.path.join(distDir, "..", os.path.join("build-" + platform.pkgPlatform + "-" + iceVersion))
srcDir = os.path.join(buildRootDir, "Ice-" + iceVersion + "-src")
buildDir = os.path.join(buildRootDir, "Ice-" + iceVersion)

if forceclean or not os.path.exists(srcDir) or not os.path.exists(buildDir):
    if os.path.exists(buildRootDir):
        print "Removing previous build from " + os.path.join("build-" + platform.pkgPlatform + "-" + iceVersion) + "...",
        sys.stdout.flush()
        shutil.rmtree(buildRootDir)
        print "ok"
    os.mkdir(buildRootDir)

    #
    # If we can't find the source archive in the current directory, ask its location
    #
    if not os.path.exists(os.path.join(cwd, "Ice-" + iceVersion + ".tar.gz")):
        print
        src = raw_input("Couldn't find Ice-" + iceVersion + ".tar.gz in current directory, please specify\n" + \
                        "where to download or copy the source distribution or hit enter to \n" + \
                        "download it from sun:/share/srcdists/" + iceVersion + ": ")
        if src == "":
            src = "sun:/share/srcdists/" + iceVersion + "/Ice-" + iceVersion + ".tar.gz"
        elif not src.endswith("Ice-" + iceVersion + ".tar.gz"):
            src = os.path.join(src, "Ice-" + iceVersion + ".tar.gz")

        if os.system("scp " + src + " ."):
            print sys.argv[0] + ": couldn't copy " + src
            sys.exit(1)

    print "Unpacking ./Ice-" + iceVersion + ".tar.gz ...",
    sys.stdout.flush()
    os.chdir(buildRootDir)
    if os.system("gunzip -c " + os.path.join(cwd, "Ice-" + iceVersion + ".tar.gz") + " | tar x" + quiet + "f -"):
        print sys.argv[0] + ": failed to unpack ./Ice-" + iceVersion + ".tar.gz"
        sys.exit(1)
    os.rename("Ice-" + iceVersion, srcDir)

    if "cpp-64" in buildLanguages:
        if os.system("gunzip -c " + os.path.join(cwd, "Ice-" + iceVersion + ".tar.gz") + " | tar x" + quiet + "f -"):
            print sys.argv[0] + ": failed to unpack ./Ice-" + iceVersion + ".tar.gz"
            sys.exit(1)
        os.rename("Ice-" + iceVersion, srcDir + "-64")

    if "cpp-11" in buildLanguages:
        if os.system("gunzip -c " + os.path.join(cwd, "Ice-" + iceVersion + ".tar.gz") + " | tar x" + quiet + "f -"):
            print sys.argv[0] + ": failed to unpack ./Ice-" + iceVersion + ".tar.gz"
            sys.exit(1)
        os.rename("Ice-" + iceVersion, srcDir + "-11")

    os.chdir(cwd)
    print "ok"

    os.mkdir(buildDir)

#
# Build and install each language mappings supported by this platform in the build directory.
#
for l in buildLanguages:
    print
    print "============= Building " + l + " sources ============="
    print

    if l == "cpp-64":
        os.chdir(os.path.join(srcDir + "-64", "cpp"))
    elif l == "cpp-11":
        os.chdir(os.path.join(srcDir + "-11", "cpp"))
    else:
        os.chdir(os.path.join(srcDir, l))

    makeOptions = platform.getMakeOptions() + " " + platform.getMakeEnvs(iceVersion, l) + " prefix=" + buildDir

    if l == "java":
        buildCmd = (platform.getJavaEnv() + " " + make + " " + " prefix=" + buildDir +
                    " " + platform.getJavaBuildOptions() + " install")
    else:
        buildCmd = make + " " + makeOptions + " install"

    print "Building with " + buildCmd

    if os.system(buildCmd) != 0:
        print sys.argv[0] + ": `" + l + "' build failed"
        os.chdir(cwd)
        sys.exit(1)


    os.chdir(os.path.join(cwd))
    print
    print "============= Finished buiding " + l + " sources ============="
    print

if os.path.exists(os.path.join(buildDir, "doc")):
    shutil.rmtree(os.path.join(buildDir, "doc"))

#
# Copy platform third party dependencies.
#
print "Copying third party dependencies..."
sys.stdout.flush()
platform.copyThirdPartyDependencies(buildDir)
platform.completeDistribution(buildDir, iceVersion)

#
# Copy platform specific files (README, SOURCES, etc)
#
print "Copying distribution files (README, SOURCES, etc)...",
sys.stdout.flush()
platform.copyDistributionFiles(distDir, buildDir)
copy(os.path.join(srcDir, "CHANGES"), os.path.join(buildDir, "CHANGES"))
print "ok"

#
# Everything should be clean now, we can create the binary distribution archive
#
platform.createArchive(cwd, buildRootDir, distDir, iceVersion, quiet)

#
# Done.
#
if forceclean:
    print "Cleaning up...",
    sys.stdout.flush()
    shutil.rmtree(buildRootDir)
    print "ok"

os.chdir(cwd)
