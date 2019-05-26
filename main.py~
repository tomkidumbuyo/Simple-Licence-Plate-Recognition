import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
import signal
import sys
from helpers import *
import cv2
import imutils
import numpy as np
import pytesseract
from db import *
import datetime
import os
from time import gmtime, strftime
import Tkinter
import tkFileDialog
import PIL
from PIL import Image 
from PIL import ImageTk



 
# create a database connection
conn = create_connection("lpr.sqlite3")

tk = Tkinter.Tk()
tk.title("Traffic Application")

w = Tkinter.Message(tk, text="Licence Number Detection.",width=200)
w.pack()

mainPanel = Tkinter.PanedWindow(tk)
mainPanel.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=Tkinter.Y)

panelA = Tkinter.PanedWindow(mainPanel,height=480,width=620)
mainPanel.add(panelA)

panelB = Tkinter.PanedWindow(mainPanel,height=480,width=200,orient = Tkinter.VERTICAL)
mainPanel.add(panelB)

mainImage = Tkinter.Label(panelA, image=None)
panelA.add(mainImage)

numberImage = Tkinter.Label(panelB, image=None,height=70)
panelB.add(numberImage)

numberText = Tkinter.Label(panelB, text="No number selected")
panelB.add(numberText)


def loadImage():
   file = tkFileDialog.askopenfile(title='Choose a file')
   if file != None:
       print(file.name)
       detect_number(file.name)

#B = Tkinter.Button(panelB, text ="load image", command = loadImage,height=20)
B = Tkinter.Button(panelB, text ="load image", command = loadImage)
panelB.add(B)



# Code to add widgets will go here...
#top.mainloop()

GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 8 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 12 to be an input pin and set initial value to be pulled low (off)

# trafic light junction 1
GPIO.setup(29,GPIO.OUT) #GREEN
GPIO.setup(31,GPIO.OUT) #YELLOW
GPIO.setup(33,GPIO.OUT) #RED

# trafic light junction 2
GPIO.setup(35,GPIO.OUT) #GREEN
GPIO.setup(37,GPIO.OUT) #YELLOW
GPIO.setup(32,GPIO.OUT) #RED

# trafic light junction 3
GPIO.setup(36,GPIO.OUT) #GREEN
GPIO.setup(38,GPIO.OUT) #YELLOW
GPIO.setup(40,GPIO.OUT) #RED

green_trafic = 1
yellow_trafic = 0


position_1  = False
position_2  = False
position_3  = False

taking_picture = False




# delay 5 seconds to start the green after the yellow light
@delay(5)
def switch_road():
    global yellow_trafic 
    global green_trafic 
    print("switching finished")
    green_trafic = green_trafic + 1
    yellow_trafic = 0
    prepare_switching()
    
# delay 55 seconds to start the yellow preparation light
@delay(55)
def prepare_switching():
    global yellow_trafic 
    global green_trafic 
    print("switching started")

    if green_trafic is not 3:
        yellow_trafic = green_trafic + 1
    else:
        yellow_trafic = 1
    switch_road()
    
prepare_switching()

def take_pictures():
    
    run_id = create_run(conn, [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    print("run_id = "+str(run_id))
    
    count = 0
    pictures = []
    while  count < 5:
        print("taking a picture")
        imageName = "files/"+strftime("%Y-%m-%d,%H:%M:%S", gmtime())+"-"+str((count+1))+".jpg"
        print(imageName)
        os.system('fswebcam -r 1080x720 -S 5 --jpeg 50 --save '+imageName ) # uses Fswebcam to take picture
        print("picture taken")
        
        picture = {
            'location':imageName,
            'number': None
        }
        pictures.append(picture)
        count = count + 1
        
    for picture in pictures:
        
        print("location : "+picture['location'])
        
        picture['number'] = detect_number(picture['location'])
        if picture['number'] is not None:
            scan_id = create_scan(conn,[picture['location'],picture['number'],run_id])
            print("scan id : "+str(scan_id))
            print("number : "+picture['number'])
        

    

def detect_number(imageName):
    img = cv2.imread(imageName,cv2.IMREAD_COLOR)

    img = cv2.resize(img, (620,480) )

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) #convert to grey scale
    gray = cv2.bilateralFilter(gray, 11, 17, 17) #Blur to reduce noise
    edged = cv2.Canny(gray, 30, 200) #Perform Edge detection

    # find contours in the edged image, keep only the largest
    # ones, and initialize our screen contour
    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:10]
    screenCnt = None

    # loop over our contours
    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)

        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            break

    if screenCnt is None:
        detected = 0
        print("No contour detected")
        numberText.configure(text="number not detected")
        numberText.text = "number not detected"
        numberImage.configure(image=imgctk)
        numberImage.image = imgctk
    else:
        detected = 1

        cv2.drawContours(img, [screenCnt], -1, (0, 255, 0), 3)

        # Masking the part other than the number plate
        mask = np.zeros(gray.shape,np.uint8)
        new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)

        new_image = cv2.bitwise_and(img,img,mask=mask)

        # Now crop
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        Cropped = gray[topx:bottomx+1, topy:bottomy+1]
			
        img2 = Cropped

        ### After apply dilation using 3X3 kernal. The recognition results are improved.##
        kernel = np.ones((2, 2), np.uint8)
        img2 = cv2.dilate(img2, kernel, iterations=1)

        cv2.imwrite("output_i_dilate.png", img2)
        tessdata_dir_config = '--tessdata-dir "D:\Program Files\Tesseract-ocr\" --psm 10'
    
        result = pytesseract.image_to_string(Image.fromarray(img2), config='--psm 10')
        print(result)
        
        #Read the number plate
        text = pytesseract.image_to_string(Cropped, config='--psm 11')
        print("Detected Number is:",text)

        #cv2.imshow('image',img)
        #cv2.imshow('Cropped',Cropped)
        
        
        imc = Image.fromarray(Cropped)
        imgctk = ImageTk.PhotoImage(image=imc) 
        numberImage.configure(image=imgctk)
        numberImage.image = imgctk
        
        numberText.configure(text=text)
        numberText.text = text

        #cv2.waitKey(25)
        #cv2.destroyAllWindows()
        print("Detected Number is:",text)
    
        
    #cv2.imshow('new image',img)
    # Convert the Image object into a TkPhoto object
    im = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=im)
    mainImage.configure(image=imgtk)
    mainImage.image = imgtk
    
    if detected == 1:
    	return text 
    else:
    	return None


loadImage()

while True: # Run forever
    #if not interval_started :
    if GPIO.input(8) == GPIO.HIGH:
        if position_1 == False:
                print("car passed on junction 1")
                position_1 = True
                GPIO.output(31,GPIO.HIGH)
    else:
        position_1 = False
        
    if GPIO.input(10) == GPIO.HIGH:
        if position_2 == False:
                print("car passed on junction 2")
                position_2 = True
                GPIO.output(37,GPIO.HIGH)
    else:
        position_2 = False
        
    if GPIO.input(12) == GPIO.HIGH:
        if position_3 == False:
                print("car passed on junction 3")
                position_3 = True
                GPIO.output(38,GPIO.HIGH)
    else:
        position_3 = False
        
    if green_trafic is 1:
        
        GPIO.output(29,GPIO.HIGH)
        GPIO.output(31,GPIO.LOW)
        GPIO.output(33,GPIO.LOW)
        
        GPIO.output(35,GPIO.LOW)
        GPIO.output(37,GPIO.LOW)
        GPIO.output(32,GPIO.HIGH)
        
        GPIO.output(36,GPIO.LOW)
        GPIO.output(38,GPIO.LOW)
        GPIO.output(40,GPIO.HIGH)
        
    elif green_trafic is 2:
        
        GPIO.output(29,GPIO.LOW)
        GPIO.output(31,GPIO.LOW)
        GPIO.output(33,GPIO.HIGH)
        
        GPIO.output(35,GPIO.HIGH)
        GPIO.output(37,GPIO.LOW)
        GPIO.output(32,GPIO.LOW)
        
        GPIO.output(36,GPIO.LOW)
        GPIO.output(38,GPIO.LOW)
        GPIO.output(40,GPIO.HIGH)
        
    elif green_trafic is 3:
        
        GPIO.output(29,GPIO.LOW)
        GPIO.output(31,GPIO.LOW)
        GPIO.output(33,GPIO.HIGH)
        
        GPIO.output(35,GPIO.LOW)
        GPIO.output(37,GPIO.LOW)
        GPIO.output(32,GPIO.HIGH)
        
        GPIO.output(36,GPIO.HIGH)
        GPIO.output(38,GPIO.LOW)
        GPIO.output(40,GPIO.LOW)
        
    if yellow_trafic is 1:
        GPIO.output(29,GPIO.LOW)
        GPIO.output(31,GPIO.HIGH)
        GPIO.output(33,GPIO.LOW)
    elif yellow_trafic is 2:    
        GPIO.output(35,GPIO.LOW)
        GPIO.output(37,GPIO.HIGH)
        GPIO.output(32,GPIO.LOW)
    elif yellow_trafic is 3:    
        GPIO.output(36,GPIO.LOW)
        GPIO.output(38,GPIO.HIGH)
        GPIO.output(40,GPIO.LOW)

    if not taking_picture and ((position_1 and green_trafic is not 1) or (position_2 and green_trafic is not 2) or (position_3 and green_trafic is not 3)):
            taking_picture = True
            pictures = take_pictures()
            taking_picture = False
            
    tk.update_idletasks()
    tk.update()
            


    

