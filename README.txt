=======
FFProbe
=======
A wrapper around the ffprobe command to extract metadata from media files.

Usage::

    #!/usr/bin/env python

    from ffprobe import FFProbe

    metadata = FFProbe("test-media-file.mov")

    for s in metadata.streams:
      if s.isVideo():
          print "Framerate: %f" % s.frameRate()
          print "Frames: %i" % s.frames()
          print "Width: %i" % s.frameSize()[0]
          print "Height: %i" %  s.frameSize()[1]
      print "Duration: %i" % s.durationSeconds()
      print "Bitrate: %i" % s.bitrate()
