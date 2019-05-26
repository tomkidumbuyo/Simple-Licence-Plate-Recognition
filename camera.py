import picamera
import os
from time import gmtime, strftime


print("about to take a picture")

imageName = "files/"+strftime("%Y-%m-%d,%H:%M:%S", gmtime())+".jpg"
print(imageName)
#setup the camera to close when not in use
os.system('fswebcam -r 1080x720 -S 5 --jpeg 50 --save '+imageName ) # uses Fswebcam to take picture
print("picture taken")
