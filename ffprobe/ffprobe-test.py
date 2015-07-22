#!/usr/bin/python

import sys
from os import listdir
from os.path import isfile, join
from ffprobe import FFProbe

path = sys.argv[1]
files = [ f for f in listdir(path) if isfile(join(path,f)) ]
for file in files:
	if not file.startswith("."):
		m = FFProbe(path + file)
		print "[ " + file + " ]"
		stream_count = 1
		for s in m.streams:
			type = "Video" if s.isVideo else "Audio"
			print "[ Stream #%s - %s ]" % (stream_count, type)
			stream_count += 1
			if s.isVideo():
				if s.durationSeconds() != 0:
					framerate = s.frames()/s.durationSeconds()
					print "Framerate: %f" % framerate
				print "Frames: %i" % s.frames()
				print "Width: %i" % s.frameSize()[0]
				print "Height: %i" %  s.frameSize()[1]
			print "Duration: %i" % s.durationSeconds()
			print "Bitrate: %i" % s.bitrate()
			print ""
