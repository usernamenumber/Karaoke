#!/usr/bin/python
import os, os.path, re, shutil, sys
from pysqlite2 import dbapi2 as sqlite
import ConfigParser


reCdgBaseFn = re.compile("(.*)\.cdg$",re.I)
musicExtensions = ['mp3','ogg','wav']
c = ConfigParser.ConfigParser()
if len(sys.argv) < 2:
	usage()
	sys.exit(1)
configFn = sys.argv[1]
destDir = sys.argv[2]

if not os.path.isdir(destDir):
	sys.stderr.write("ERROR: Could not find dir %s\n" % destDir)
	sys.exit(1)

c.read(configFn)
musicDir = c.get("general","musicDir")
dbFn = c.get("general","dbFn")

conn = sqlite.connect(dbFn)
cursor = conn.cursor()
q = "select archiveFn,cdgfn from playlist inner join music where playlist.song_id = music.id";
res = cursor.execute(q).fetchall()

for track in res:
	zipFn = track[0]
	cdgFn = track[1]
	if zipFn == u'NULL':
		baseFn = reCdgBaseFn.match(cdgFn).groups()[0]	
		musicFn = None
		for ext in musicExtensions:
			testFn = baseFn+"."+ext
			#print "TESTING: %s" % testFn
			if os.path.isfile(testFn):
				musicFn = testFn
				break
		if not musicFn:
			sys.stderr.write("Could not find matching music file for %s\n" % cdgFn)
		else:
			print "Copying %s to %s" % (cdgFn,destDir)
			shutil.copy(cdgFn,destDir)
			print "Copying %s to %s" % (musicFn,destDir)
			shutil.copy(musicFn,destDir)
	else:
		print "Copying %s to %s" % (zipFn,destDir)
		shutil.copy2(zipFn,destDir)
	
