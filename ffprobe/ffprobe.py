#!/usr/bin/python
# Filename: ffprobe.py
"""
Python wrapper for ffprobe command line tool. ffprobe must exist in the path or in a common installation path
"""

version = '0.4'

import subprocess
import re
import os
import sys
from os import listdir
from os.path import isfile, join
import json
import mimetypes

class FFProbe(object):
    """
    FFProbe wraps the ffprobe command and pulls the data into an object form::
    metadata = FFProbe('multimedia-file.mov')
    OR
    metadata = FFProbe(file_contents)
    OR
    metadata = FFProbe('multimedia-file.mov', ffprobe_path='/usr/local/bin/ffprobe')
    """
    def __init__(self, source, ffprobe_path=None):
        ffprobe_cmd = None
        if ffprobe_path is not None and os.path.exists(ffprobe_path):
            ffprobe_cmd = ffprobe_path
        else:
            ffprobe_cmd = os.environ.get('FFPROBE', 'ffprobe')
            try:
                with open(os.devnull, 'w') as tempf:
                    subprocess.check_call([ffprobe_cmd, "-h"], stdout=tempf,
                                          stderr=tempf)
            except:
                paths = {
                    "Windows": ["ffprobe.exe"],
                    "Darwin": ["ffprobe", "/opt/local/bin/ffprobe", "/usr/local/bin/ffprobe"],
                    "Linux": ["ffprobe", "/opt/local/bin/ffprobe", "/usr/local/bin/ffprobe"]
                }

                # Find path of transcoder
                found = False
                for path in paths[platform.system()]:
                    if os.path.exists(path):
                        ffprobe_cmd = path
                        found = True

                if not found:
                    raise IOError('ffprobe not found')

        self.streams = []
        self.video = []
        self.audio = []
        self.duration = 0.0
        self.mimetype = None
        self.returncode = None

        # If source is file and it exists the use path, otherwise
        # open file and send contents to ffprobe through stdin
        DEVNULL = open(os.devnull, 'wb')
        args = [ffprobe_cmd, "-show_streams", "-print_format", "json", "-show_format", "-i"]
        if os.path.isfile(source):
            try:
                type, encoding = mimetypes.guess_type(source)
                self.mimetype = type
            except:
                pass
            args.append(source)
            proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=DEVNULL)
        else:
            args.append("-")
            proc = subprocess.Popen(args, stdin=source, stdout=subprocess.PIPE, stderr=DEVNULL)

        raw_out = ""
        while self.returncode is None:
            for line in proc.stdout:
                raw_out += line
            self.returncode = proc.poll()

        proc.stdout.close()

        if self.returncode != 0:
            raise IOError('ffprobe failed')

        json_out = json.loads(raw_out)

        for key in json_out["format"]:
            self.__dict__[key] = json_out["format"][key]

        for stream in json_out["streams"]:
            self.streams.append(FFStream(stream))

        for stream in self.streams:
            if stream.isAudio() or stream.isVideo():
                if "duration" not in stream.__dict__ or stream.__dict__["duration"] == 0.0:
                    stream.__dict__["duration"] = self.duration

            if stream.isAudio():
                self.audio.append(stream)
            if stream.isVideo():
                self.video.append(stream)

    # @todo Needs to follow http://tools.ietf.org/html/rfc6381
    # @todo Need to add mp4v and mp4a (aac)
    def html5SourceType(self):
        string = ''
        if self.mimetype is not None:
            string += self.mimetype
            video = self.video[0]
            audio = self.audio[0]
            if video is not None or audio is not None:
                string += '; codecs="'
                codecs = []
                if video is not None:
                    if video.codec() == 'h264':
                        codec = 'avc1.'
                        profile = video.__dict__["profile"]
                        if profile == 'High':
                            codec += '6400'
                        elif profile == 'Baseline':
                            codec += '42E0'
                        elif profile == 'Constrained Baseline':
                            codec += '42E0'
                        elif profile == 'Main':
                            codec += '4D40'
                        elif profile == 'Extended':
                            codec += '58A0'
                        codec += hex(int(video.__dict__["level"]))[2:].upper()
                        codecs.append(codec)
                    else:
                        codecs.append(video.codec())
                if audio is not None:
                    if audio.codec() == 'aac':
                        codecs.append('mp4a.40.2')
                    else:
                        codecs.append(audio.codec())
                string += ', '.join(codecs)
                string += '"'
        return string

    def durationSeconds(self):
        """
        Returns the runtime duration of the file as a floating point number of seconds.
        Returns 0.0 if value not found
        """
        f = 0.0
        if 'duration' in self.__dict__:
            try:
                f = float(self.__dict__['duration'])
            except Exception as e:
                pass
        return f

    def bitrate(self):
        """
        Returns bitrate as an integer in bps
        """
        b = 0
        if 'bit_rate' in self.__dict__:
            try:
                b = int(self.__dict__['bit_rate'])
            except Exception as e:
                pass
        return b

class FFStream(object):
    """
    An object representation of an individual stream in a multimedia file.
    """
    def __init__(self, obj):
        for key in obj.keys():
            self.__dict__[key] = obj[key]

    def isData(self):
        """
        Is this stream labelled as an data stream?
        """
        val = False
        if 'codec_type' in self.__dict__:
            if str(self.__dict__['codec_type']) == 'data':
                val = True
        return val

    def isAudio(self):
        """
        Is this stream labelled as an audio stream?
        """
        val = False
        if 'codec_type' in self.__dict__:
            if str(self.__dict__['codec_type']) == 'audio':
                val = True
        return val

    def isVideo(self):
        """
        Is the stream labelled as a video stream.
        """
        val = False
        if 'codec_type' in self.__dict__:
            if self.codec_type == 'video':
                val = True
        return val

    def isSubtitle(self):
        """
        Is the stream labelled as a subtitle stream.
        """
        val = False
        if 'codec_type' in self.__dict__:
            if str(self.codec_type)=='subtitle':
                val = True
        return val

    def frameSize(self):
        """
        Returns the pixel frame size as an integer tuple (width,height) if the stream is a video stream.
        Returns None if it is not a video stream.
        """
        size = None
        if self.isVideo():
            if 'width' in self.__dict__ and 'height' in self.__dict__:
                try:
                    size = (int(self.__dict__['width']),int(self.__dict__['height']))
                except Exception as e:
                    pass
                    size = (0,0)
        return size

    def pixelFormat(self):
        """
        Returns a string representing the pixel format of the video stream. e.g. yuv420p.
        Returns none is it is not a video stream.
        """
        f = None
        if self.isVideo():
            if 'pix_fmt' in self.__dict__:
                f = self.__dict__['pix_fmt']
        return f

    def frames(self):
        """
        Returns the length of a video stream in frames. Returns 0 if not a video stream.
        """
        f = 0
        if self.isVideo() or self.isAudio():
            if 'nb_frames' in self.__dict__:
                try:
                    f = int(self.__dict__['nb_frames'])
                except Exception as e:
                    pass
        return f

    def durationSeconds(self):
        """
        Returns the runtime duration of the video stream as a floating point number of seconds.
        Returns 0.0 if not a video stream.
        """
        f = 0.0
        if self.isVideo() or self.isAudio():
            if 'duration' in self.__dict__:
                try:
                    f = float(self.__dict__['duration'])
                except Exception as e:
                    pass
        return f

    def language(self):
        """
        Returns language tag of stream. e.g. eng
        """
        lang = None
        if 'TAG:language' in self.__dict__:
            lang = self.__dict__['TAG:language']
        return lang

    def codec(self):
        """
        Returns a string representation of the stream codec.
        """
        codec_name = None
        if 'codec_name' in self.__dict__:
            codec_name = self.__dict__['codec_name']
        return codec_name

    def codecDescription(self):
        """
        Returns a long representation of the stream codec.
        """
        codec_d = None
        if 'codec_long_name' in self.__dict__:
            codec_d = self.__dict__['codec_long_name']
        return codec_d

    def codecTag(self):
        """
        Returns a short representative tag of the stream codec.
        """
        codec_t = None
        if 'codec_tag_string' in self.__dict__:
            codec_t = self.__dict__['codec_tag_string']
        return codec_t

    def bitrate(self):
        """
        Returns bitrate as an integer in bps
        """
        b = 0
        if 'bit_rate' in self.__dict__:
            try:
                b = int(self.__dict__['bit_rate'])
            except Exception as e:
                pass
        return b

    def frameRate(self):
        """
        Returns the framerate as an float in frames/second
        """
        f = 0.0
        if 'codec_type' in self.__dict__:
            if str(self.__dict__['codec_type']) == 'video':
                if 'nb_frames' in self.__dict__ and 'duration' in self.__dict__:
                    try:
                        f = int(self.__dict__['nb_frames']/self.__dict__['duration'])
                    except Exception as e:
                        pass
        return f

def printMeta(path):
    m = FFProbe(path)
    name = os.path.split(path)[1]
    stream_count = 1
    for s in m.streams:
        type = "Video" if s.isVideo else "Audio"
        print "[ %s - Stream #%s - %s ]" % (name, stream_count, type)
        stream_count += 1
        if s.isVideo():
            print "Framerate: %f" % s.frameRate()
            print "Frames: %i" % s.frames()
            print "Width: %i" % s.frameSize()[0]
            print "Height: %i" %  s.frameSize()[1]
        print "Duration: %f" % s.durationSeconds()
        print "Bitrate: %i" % s.bitrate()
        print ""

if __name__ == '__main__':
    if len(sys.argv) == 2:
        path = sys.argv[1]

        if os.path.isfile(path):
            printMeta(path)
        elif os.path.isdir(path):
            files = [ f for f in listdir(path) if isfile(join(path,f)) ]
            for file in files:
            	if not file.startswith("."):
                    printMeta(path + file)
        else:
            sys.exit(1)
    else:
        print "Usage: python ffprobe.py <file>|<directory>"
