ffprobe python module
=====================

A wrapper around the ffprobe command to extract metadata from media files.

# Usage

## Library

```
#!/usr/bin/env python

from ffprobe import FFProbe

metadata = FFProbe("test-media-file.mov")

print "Duration: %i" % metadata.durationSeconds()
print "Bitrate: %i" % metadata.bitrate()
print "HTML5 Source Type: %s" % metadata.html5SourceType()

for s in metadata.streams:
  if s.isVideo():
      print "Framerate: %f" % s.frameRate()
      print "Frames: %i" % s.frames()
      print "Width: %i" % s.frameSize()[0]
      print "Height: %i" %  s.frameSize()[1]
  print "Duration: %i" % s.durationSeconds()
  print "Bitrate: %i" % s.bitrate()
  print "Codec: %s" % s.codec()
```

### Specifing path for ffprobe
`metadata = FFProbe('multimedia-file.mov', ffprobe_path='/usr/local/bin/ffprobe')`

## Command line
```python ffprobe.py <file>|<directory>```

## Unit test
```python ffprobe-test.py```

# License
(The MIT License)

Copyright (C) 2013 Simon Hargreaves simon@simon-hargreaves.com Permission is hereby granted,
free of charge, to any person obtaining a copy of this software and associated documentation
files (the 'Software'), to deal in the Software without restriction, including without
limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
sell copies of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING
BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
