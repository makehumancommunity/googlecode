#!/usr/bin/env python
# -*- coding: utf-8 -*-

# HINT: You need to run 
#
#   apt-get install devscripts equivs rsync subversion
#
# ... in order for this script to function at all


# --- CONFIGURATION SETTINGS --- 


# These scripts are run before building deb contents, in the array order
pre_deb_scripts = ["cleanpyc.sh","cleannpz.sh","compile_targets.py","compile_models.py"]

rsync = "/usr/bin/rsync"
rsync_common_args = "-av --delete"
rsync_main_excludes = ["deb","SConstruct",".svn","*.pyc","*.nsi","*.pyd","*.c","*.h"]

svn = "/usr/bin/svn"

# Set to true to skip compiling targets and models etc
do_not_execute_scripts = False

files_to_chmod_executable = [
    "usr/bin/makehuman",
    "usr/share/makehuman/docs/drupal-export/parse.pl",
    "usr/share/makehuman/docs/drupal-export/syncimages.bash",
    "usr/share/makehuman/makehuman",
    "usr/share/makehuman/utils/fixmesh/fixall",
    "usr/share/makehuman/utils/fixmesh/fixshapes",
    "usr/share/makehuman/utils/fixmesh/macrodet",
    "usr/share/makehuman/cleannpz.sh",
    "usr/share/makehuman/cleanpyc.sh",
    "usr/share/makehuman/compile_models.py",
    "usr/share/makehuman/compile_targets.py",
    "usr/share/makehuman/compressTargetsASCII.py",
    "usr/share/makehuman/makehuman.py",
    "usr/share/makehuman/tools/standalone/maketarget/compilePyinstaller.sh"
    ]

package_name = "makehumansvn"
package_replaces = "makehuman-nightly,makehuman-alpha"


# --- EVERYTHING BELOW THIS POINT IS LOGIC, HANDS OFF ---


import sys
import os
import string
import re
import subprocess

dest = os.getenv('makehuman_dest',0)

if dest == 0:
  print "You must explicitly set the makehuman_dest environment variable to point at a work directory. I will violently destroy and mutilate the contents of this directory."
  exit(1)

destdir = os.path.abspath(dest)
if not os.path.exists(destdir):
  print destdir + " does not exist"
  exit(1)

if not os.path.exists(rsync):
  print "Rsync is not installed."
  exit(1)

debdir = os.path.dirname(os.path.abspath(__file__))
scriptdir = os.path.abspath( os.path.join(debdir,'..') )

print "Makehuman directory: " + scriptdir
print "Destination directory: " + destdir

target = os.path.join(destdir,"debroot")
if not os.path.exists(target):
  os.mkdir(target)

controldir = os.path.join(target,"DEBIAN")
if not os.path.exists(controldir):
  os.mkdir(controldir)

print "Control directory: " + controldir

srccontrol = os.path.join(debdir,"debian");

if not os.path.exists(srccontrol):
  print "The debian directory does not exist in the source deb folder. Something is likely horribly wrong. Eeeeek! Giving up and hiding..."
  exit(1)

tmp = os.path.join(target,"usr")
if not os.path.exists(tmp):
  os.mkdir(tmp)

bindir = os.path.join(tmp,"bin")
if not os.path.exists(bindir):
  os.mkdir(bindir)

print "Bin directory: " + bindir

srcbin = os.path.join(scriptdir,"deb");
srcbin = os.path.join(srcbin,"bin");

if not os.path.exists(srcbin):
  print "The bin directory does not exist in the source deb folder. Something is likely horribly wrong. Eeeeek! Giving up and hiding..."
  exit(1)

tmp = os.path.join(tmp,"share")
if not os.path.exists(tmp):
  os.mkdir(tmp)

docdir = os.path.join(tmp,"doc")
if not os.path.exists(docdir):
  os.mkdir(docdir)

docdir = os.path.join(docdir,package_name)
if not os.path.exists(docdir):
  os.mkdir(docdir)

print "Doc dir: " + docdir

programdir = os.path.join(tmp,"makehuman")
if not os.path.exists(programdir):
  os.mkdir(programdir)

print "Program directory: " + programdir

print "\nABOUT TO EXECUTE SCRIPTS\n"

if not do_not_execute_scripts:
  os.chdir(scriptdir)
  for s in pre_deb_scripts:
    exe = "./" + s
    os.system(exe)

print "\nABOUT TO RSYNC CONTENTS TO DEB DEST\n"

rsyncmain = rsync + " " + rsync_common_args

for e in rsync_main_excludes:
  rsyncmain = rsyncmain + " --exclude=" + e

rsyncmain = rsyncmain + " " + scriptdir + "/ " + programdir + "/"

print rsyncmain
os.system(rsyncmain)

rsyncbin = rsync + " " + rsync_common_args
rsyncbin = rsyncbin + " " + srcbin + "/ " + bindir + "/"

print rsyncbin
os.system(rsyncbin)

svnrevfile = os.path.join(docdir,"SVNREV.txt")
os.system("svn info " + scriptdir + " | grep Revision | cut -f 2 --delimiter=' ' > " + svnrevfile)

rsynccontrol = rsync + " " + rsync_common_args
rsynccontrol = rsynccontrol + " " + srccontrol + "/ " + controldir + "/"

print rsynccontrol
os.system(rsynccontrol)

os.chdir(controldir)

f = open(svnrevfile,"r")
svnrev = f.readline().rstrip()
f.close()

os.system("du -cks " + target + " | cut -f 1 | uniq > /tmp/makehumansize")
f = open("/tmp/makehumansize","r")
size = f.readline().rstrip()
f.close()

os.system("sed -i -e 's/SVNREV/" + svnrev + "/' control")
os.system("sed -i -e 's/PKGNAME/" + package_name + "/' control")
os.system("sed -i -e 's/REPLACES/" + package_replaces + "/' control")
os.system("sed -i -e 's/SIZE/" + size + "/' control")

os.chdir(target)

copysrc = os.path.join(controldir,"copyright")
copydest = os.path.join(docdir,"copyright")

os.system("mv " + copysrc + " " + copydest)

tmp = os.path.join(programdir,"license.txt")
tmp2 = os.path.join(docdir,"LICENSE.txt")
os.system("mv " + tmp + " " + tmp2)

maketargetlicense = "usr/share/makehuman/utils/maketarget/license.txt"
if os.path.exists(maketargetlicense):
  mtl = os.path.join(docdir,"LICENSE.maketarget.txt")
  os.system("mv " + maketargetlicense + " " + mtl)

os.system("chown -R 0:0 " + target)
os.system("chmod -R 644 " + target)
os.system('find ' + target + ' -type d -exec "chmod" "755" {} ";"')

for x in files_to_chmod_executable:
  if os.path.exists(x):
    os.system("chmod 755 " + x)

outputdir = os.path.join(destdir,"output")

if not os.path.exists(outputdir):
  os.mkdir(outputdir)

os.chdir(outputdir)

debfile = os.path.join(outputdir,package_name + "-" + svnrev + ".deb")

debcmd = "dpkg-deb -Z bzip2 -z 9 -b ../debroot " + debfile + "\n"

print debcmd
os.system(debcmd)

print "\n\n\nPackage is now available in " + debfile + "\n"
print "If you are building for release, you should now run:\n"
print "  lintian " + debfile + "\n"
print "... in order to check the deb file.\n"
