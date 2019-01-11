from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
from PIL import Image
import base64,os
from io import BytesIO


BASE = os.path.dirname(os.path.abspath(__file__))
# Specify the paths for the model files 
protoFile = BASE+'/colorization_deploy_v2.prototxt'
weightsFile =BASE+'/colorization_release_v2.caffemodel'
#weightsFile = "./models/colorization_release_v2_norebal.caffemodel";
print("[INFO] loading colorization model...")
net = cv2.dnn.readNetFromCaffe(protoFile, weightsFile)      
print("[INFO] loading colorization model finish...")
 
def BW2Color(base64_image_string):
	try:
		# Read the input image
		image = Image.open(BytesIO(base64.b64decode(base64_image_string)))
		frame = np.array(image)
		# frame = cv2.imread(BASE+"/IMG_20190102_191819099_HDR-ConvertImage_RESIZED.jpg")
		 
		W_in = 224
		H_in = 224
		 
		# Read the network into Memory 
		
		# Load the bin centers
		pts_in_hull = np.load(BASE+'/pts_in_hull.npy')
		 
		# populate cluster centers as 1x1 convolution kernel
		pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
		net.getLayer(net.getLayerId('class8_ab')).blobs = [pts_in_hull.astype(np.float32)]
		net.getLayer(net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, np.float32)]


		#Convert the rgb values of the input image to the range of 0 to 1
		img_rgb = (frame[:,:,[2, 1, 0]] * 1.0 / 255).astype(np.float32)
		img_lab = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2Lab)
		img_l = img_lab[:,:,0] # pull out L channel

		# resize the lightness channel to network input size 
		img_l_rs = cv2.resize(img_l, (W_in, H_in)) # resize image to network input size
		img_l_rs -= 50 # subtract 50 for mean-centering


		net.setInput(cv2.dnn.blobFromImage(img_l_rs))
		ab_dec = net.forward()[0,:,:,:].transpose((1,2,0)) # this is our result
		 
		(H_orig,W_orig) = img_rgb.shape[:2] # original image size
		ab_dec_us = cv2.resize(ab_dec, (W_orig, H_orig))
		img_lab_out = np.concatenate((img_l[:,:,np.newaxis],ab_dec_us),axis=2) # concatenate with original image L
		img_bgr_out = np.clip(cv2.cvtColor(img_lab_out, cv2.COLOR_Lab2BGR), 0, 1)
		
		new_img = cv2.resize(img_bgr_out*255, (500, 500))
		s = base64.b64encode(new_img)

		return s
		# cv2.imwrite('1_colorized.png', img_bgr_out*255)
	except Exception as e:
		print(e)
		return str(e)
	
	
