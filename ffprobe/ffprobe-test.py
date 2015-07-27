#!/usr/bin/python

from ffprobe import FFProbe
import unittest
import urllib
import os
from os import listdir
from os.path import isfile, join

class TestFFProbe(unittest.TestCase):
	def setUp(self):
		self.tmp_dir = "test_samples"
		self.test_sample_urls = [
			"http://techslides.com/demos/sample-videos/small.mp4",
			"http://techslides.com/demos/sample-videos/small.webm",
			"http://techslides.com/demos/sample-videos/small.ogv",
			"http://techslides.com/demos/sample-videos/small.3gp",
			"http://techslides.com/demos/sample-videos/small.flv"
		]

		if not os.path.exists(self.tmp_dir):
			os.makedirs(self.tmp_dir)
			print "Downloading samples"
			for url in self.test_sample_urls:
				try:
					print "Downloading " + url
					sample = urllib.URLopener()
					sample.retrieve(url, self.tmp_dir + "/" + url.split('/')[-1])
				except:
					pass

	def tearDown(self):
		pass

	def test_sample_media(self):
		samples = [ f for f in listdir(self.tmp_dir) if isfile(join(self.tmp_dir,f)) ]
		for sample in samples:
			print "Probing " + sample
			metadata = FFProbe(self.tmp_dir + "/" + sample)
			self.assertNotEqual(metadata.durationSeconds(), 0.0)
			self.assertNotEqual(metadata.bitrate(), 0.0)
			for stream in metadata.streams:
				if stream.isAudio() or stream.isVideo():
					self.assertNotEqual(stream.durationSeconds(), 0.0)
					#self.assertNotEqual(stream.bitrate(), 0.0)

				if stream.isVideo():
					self.assertNotEqual(stream.frameSize(), (0,0))

if __name__ == '__main__':
    unittest.main()
