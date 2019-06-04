#!/usr/local/bin/python3
import argparse
import os
from PIL import Image
import glob
import numpy as np
import pylab
from scipy.special import comb

parser = argparse.ArgumentParser(description='Combine images into a blurred timelapse. Stack together a moving window to create each frame, then combine into a video output file. If blurring window is reduced to a single frame, this will produce a standard timelapse without blurring. As the blurring window increases in size (n), the resulting output video, given (N) input frames, will be reduced to (N-n) output frames.')
parser.add_argument('-i','--input',help="Input files.",required=True,dest='imgList',nargs='+',type=str)
parser.add_argument('--blur',help="Frame blur type. Sets the frame weighting distribution.",choices=['binomial','constant'],default='binomial',type=str)
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

if blur=='binomial':
	# Binomial degree 0 has 1 element, which is why the +1 is required.
	w = degree+1
	X = pylab.array(range(0,w))
	Y = comb(degree,X,exact=False)
	Y = Y/sum(Y)
	print("Weights: ",Y)
elif blur=='constant':
	w = degree
	Y = np.ones(w)/w
	print("Weights: ",Y)

frame = np.asarray(Image.open(imgList[0]));
temp = np.zeros(frame.shape)
sumImage = np.zeros(frame.shape)
N = len(imgList)
N = min(N,len(imgList)-w)
frames = np.zeros((N,frame.shape[0],frame.shape[1],frame.shape[2]))

tempdir = tempdir
tempname = "temp_"+blur+"_"+str(w)+"_"
tempext = ".png"

nzeros = int(np.ceil(np.log10(N)))

if not os.path.exists(tempdir):
	os.makedirs(tempdir)

for i in range(0,N):
	sumImage=np.zeros(frame.shape)
	filename=tempdir+"/"+tempname+str(i).zfill(nzeros)+tempext
	if not os.path.exists(filename):
		for j in range(0,w):
			temp = np.asarray(Image.open(imgList[i+j]))
			temp = temp.astype('uint32')
			sumImage = sumImage + temp*Y[j]
		sumImage = Image.fromarray(sumImage.astype('uint8'))
		sumImage.save(filename)
	print(filename)

if output == '':
	output=blur+"_"+str(w)+"_"+str(fps)+".mp4"

infiles=tempdir+"/"+tempname+"%0"+str(nzeros)+"d"+tempext
os.system("ffmpeg -r "+str(fps)+" -i "+infiles+" -r "+str(fps)+" -vcodec "+vcodec+" "+output)