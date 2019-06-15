# timelapseBlur.py
```
usage: timelapseBlur.py [-h] -i IMGLIST [IMGLIST ...]
                        [--blur {binomial,constant}] [--degree DEGREE]
                        [--tempdir TEMPDIR] [--fps FPS] [--vcodec VCODEC]
                        [-o OUTPUT]

Combine images into a blurred timelapse. Stack together a moving window to
create each frame, then combine into a video output file. If blurring window
is reduced to a single frame, this will produce a standard timelapse without
blurring. As the blurring window increases in size (n), the resulting output
video, given (N) input frames, will be reduced to (N-n) output frames.

optional arguments:
  -h, --help            show this help message and exit
  -i IMGLIST [IMGLIST ...], --input IMGLIST [IMGLIST ...]
                        Input files.
  --blur {binomial,constant}
                        Frame blur type. Sets the frame weighting
                        distribution.
  --degree DEGREE, --deg DEGREE, -d DEGREE
                        Degree of coefficients for image blurring, n. Binomial
                        blurring window is n+1 frames wide. Constant blurring
                        window is n frames wide.
  --tempdir TEMPDIR     Working directory
  --fps FPS             output video frames per second
  --vcodec VCODEC       Video codec for FFMPEG.
  -o OUTPUT, --output OUTPUT
                        Output video filename. Defaults to "(blur type)_(blur
                        width)_(fps).mp4"
```

## Dependencies
Requires FFMPEG for video encoding
Python libraries: argparse, os, Pillow (PIL), numpy, scipy.comb, time
