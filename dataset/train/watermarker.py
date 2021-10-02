from PIL import Image, ImageDraw, ImageFont
import sys

class WaterMarker():
	def __init__(self):
		self.currentImage = None
		self.currentImageName = None
		self.currentDrawObj = None
		self.watermarkText = "Test Watermark"
		self.watermarkFont = ImageFont.truetype('/usr/share/fonts/gnu-free/FreeSans.otf', 82)

	def drawMark(self, arg):
		
		# open image
		self.currentImage = Image.open(r'./' + arg)
		self.currentImageName = arg

		# create draw object
		self.currentDrawObj = ImageDraw.Draw(self.currentImage)
		
		# position text
		textWidth, textHeight = self.currentDrawObj.textsize(self.watermarkText,
															 self.watermarkFont)
		width, height = self.currentImage.size
		x = width/2-textWidth/2
		y = height-textHeight-300

		# draw watermark
		self.currentDrawObj.text((x, y), self.watermarkText,
								 font=self.watermarkFont)

		# save image
		self.currentImage.save(r'./marked/' + self.currentImageName)
		self.currentImage = None
		self.currentImageName = None


if __name__ == '__main__':
	wm = WaterMarker()

	# the first arg is the script name so we won't use that one
	for count in range(1, len(sys.argv)):
		wm.drawMark(sys.argv[count])
