#!/usr/local/bin/python3
import argparse
import os
from PIL import Image
import glob
import numpy as np
import pylab
from scipy.special import comb
import time

global t0
t0 = time.time()

def printStatus(level,text):
	""" 
	Take a bit of text and prepend -'s and a > based off the depth.
	Used for status messages, with depth denoting a heirarchical relationship.
	"""
	global t0
	pre = "[{0:>7.2f}] ".format(time.time()-t0)
	for x in range(0,level):
		pre += "-"
	pre += "> "
	print(pre+text)

def sumImages(frames,weights):
	""" 
	Takes an nd array 'frames' size (wxHxWx3) and a 1d array 'weights' (w)
	Compute the weighted averages of the w HxWx3 frames utilizing the w weights
	"""
	sumImage=np.zeros(frames[0].shape)
	for i in range(0,len(weights)):
		sumImage += frames[i]*weights[i]
	return sumImage


parser = argparse.ArgumentParser(description='Combine images into a blurred timelapse. Stack together a moving window to create each frame, then combine into a video output file. If blurring window is reduced to a single frame, this will produce a standard timelapse without blurring. As the blurring window increases in size (n), the resulting output video, given (N) input frames, will be reduced to (N-n) output frames.')
parser.add_argument('--input','-i',help="Input files.",required=True,dest='imgList',nargs='+',type=str)
parser.add_argument('--blur','-b',help="Frame blur type. Sets the frame weighting distribution.",choices=['binomial','constant'],default='binomial',type=str)
parser.add_argument('--degree','--deg','-d',help="Degree of coefficients for image blurring, n. Binomial blurring window is n+1 frames wide. Constant blurring window is n frames wide.",default=5,type=int)
parser.add_argument('--tempdir',help="Working directory",default='temp',type=str)
parser.add_argument('--fps',help="output video frames per second",default=30,type=str)
parser.add_argument('--vcodec',help='Video codec for FFMPEG.',default='libx264',type=str)
parser.add_argument('-o','--output',help='Output video filename. Defaults to "(blur type)_(blur width)_(fps).mp4"',default='')

args=parser.parse_args()
# imgList = glob.glob('./*.jpg')
imgList=args.imgList
blur=args.blur
degree=args.degree
tempdir=args.tempdir
fps=args.fps
vcodec=args.vcodec
output=str(args.output)

print(imgList,blur,degree,tempdir,fps,vcodec,output)

printStatus(1,"Computing weights...")
if blur=='binomial':
	# Binomial degree 0 has 1 element, which is why the +1 is required.
	w = degree+1
	X = pylab.array(range(0,w))
	Y = comb(degree,X,exact=False)
	Y = Y/sum(Y)
	printStatus(1,"Weights: "+str(Y))
elif blur=='constant':
	w = degree
	Y = np.ones(w)/w
	printStatus(1,"Weights: "+str(Y))

printStatus(2,"Done")

frame = np.asarray(Image.open(imgList[0]));
temp = np.zeros(frame.shape)	
sumImage = np.zeros(frame.shape)
N = len(imgList)
N = min(N,len(imgList)-w)
frames = np.zeros((w,frame.shape[0],frame.shape[1],frame.shape[2]))

printStatus(1,str(frames.shape))

tempdir = tempdir
tempname = "temp_"+blur+"_"+str(w)+"_"
tempext = ".jpg"

nzeros = int(np.ceil(np.log10(N)))

if not os.path.exists(tempdir):
	printStatus(1,"Creating directory "+tempdir)
	os.makedirs(tempdir)

if True:
	nameImage = ()
	for i in range(0,N):
		# Add the actual image to the frames ndarray
		printStatus(1,"Loading "+imgList[i]+"...")
		frames[i%w] = np.asarray(Image.open(imgList[i])).astype('uint32')
		printStatus(2,"Done")
		# Add the img name to the nameImage tuple. Used diagnostically to see if the images
		# still ine buffer line up with the rolling weights
		nameImage = nameImage[:i%w] + (imgList[i],) + nameImage[i%w+1:]
		if i>=w-1:
			filename=tempdir+"/"+tempname+str(i).zfill(nzeros)+tempext
			printStatus(1,"Blurring stack: " + nameImage[(i+1)%w] + " -> " + nameImage[i%w])
			sumImage = sumImages(frames,np.roll(Y,i+1))
			printStatus(2,"Done")
			printStatus(1,"Saving stack...")
			Image.fromarray(sumImage.astype('uint8')).save(filename)
			printStatus(2,"Done")
else:
	printStatus(1,"Seeding frame buffer...")
	for i in range(0,w):
			printStatus(2,"Opening "+imgList[i])
			frames[i] = np.asarray(Image.open(imgList[i])).astype('uint32')
			printStatus(3,"Loaded")
			sumImage = sumImages(frames,Y)
	printStatus(2,"Initial frame buffer loaded")

	filename=tempdir+"/"+tempname+str(0).zfill(nzeros)+tempext
	sumImage = Image.fromarray(sumImage.astype('uint8'))
	printStatus(2,"Saving stack: "+filename)
	sumImage.save(filename)
	printStatus(3,"Saved")

	printStatus(1,"Creating intermediate frames...")
	for i in range(1,N):
		sumImage=np.zeros(frame.shape)
		filename=tempdir+"/"+tempname+str(i).zfill(nzeros)+tempext
		frames=np.roll(frames,-1,axis=0)
		printStatus(2,"Opening "+imgList[i+w-1])
		frames[-1] = np.asarray(Image.open(imgList[i+w-1])).astype('uint32')
		printStatus(3,"Loaded")
		printStatus(2,"Blurring frames...")
		for j in range(0,w):
			sumImage = sumImage + frames[j]*Y[j]
		printStatus(3,"Done")
		sumImage = Image.fromarray(sumImage.astype('uint8'))
		printStatus(2,"Saving stack: "+filename)
		sumImage.save(filename)
		printStatus(3,"Saved")

# for i in range(0,N):
# 	sumImage=np.zeros(frame.shape)
# 	filename=tempdir+"/"+tempname+str(i).zfill(nzeros)+tempext
# 	if not os.path.exists(filename):
# 		for j in range(0,w):
# 			printStatus(2,"Opening "+imgList[i+j])
# 			temp = np.asarray(Image.open(imgList[i+j]))
# 			temp = temp.astype('uint32')
# 			printStatus(3,"Loaded")
# 			sumImage = sumImage + temp*Y[j]
# 		sumImage = Image.fromarray(sumImage.astype('uint8'))
# 		printStatus(2,"Saving stack: "+filename)
# 		sumImage.save(filename)

if output == '':
	output=blur+"_"+str(w)+"_"+str(fps)+".mp4"

infiles=tempdir+"/"+tempname+"%0"+str(nzeros)+"d"+tempext

printStatus(1,"Creating output file: "+output+" using inputs: "+infiles)
os.system("ffmpeg -r "+str(fps)+" -i "+infiles+" -r "+str(fps)+" -vcodec "+vcodec+" "+output)
