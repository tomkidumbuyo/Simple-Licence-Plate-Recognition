#import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import re
import time
import signal
import sys
from builtins import range, len, sorted, str

from helpers import *
import cv2
import imutils
import numpy as np
import pytesseract
from db import *
import datetime
import os
from time import gmtime, strftime

from tkinterTable import Table

try:
    import Tkinter
    import tkFileDialog
except:
    import tkinter as Tkinter
    import tkinter.filedialog as tkFileDialog

import PIL
from PIL import Image 
from PIL import ImageTk
from scrolling_area import Scrolling_Area

import sqlite3
from sqlite3 import Error

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

""" create a database connection to a SQLite database """
try:
    conn = sqlite3.connect("main.db")
    print(sqlite3.version)

    sql_create_projects_table = """ CREATE TABLE IF NOT EXISTS vehicles (
                                            id integer PRIMARY KEY,
                                            number text NOT NULL,
                                            first_name text,
                                            last_name text,
                                            location text
                                        ); """

    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tickets (
                                        id integer PRIMARY KEY,
                                        vehicle_id integer,
                                        image text NOT NULL,
                                        date text NOT NULL,
                                        FOREIGN KEY (vehicle_id) REFERENCES vehicles (id)
                                    );"""
    create_table(conn, sql_create_projects_table)
    create_table(conn, sql_create_tasks_table)

except Error as e:
    print(e)
finally:
    conn.close()

def save_ticket(number,image):
    conn = sqlite3.connect("main.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM vehicles WHERE number=?", (number,))
    rows = cur.fetchall()
    conn.close()

    if len(rows) > 0:
        car = rows[0]
    else:
        conn = sqlite3.connect("main.db")
        sql = ''' INSERT INTO vehicles(number)
                      VALUES(?) '''
        cur = conn.cursor()
        cur.execute(sql, (number,))
        conn.commit()
        conn.close()

        conn = sqlite3.connect("main.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM vehicles WHERE id = ?",(cur.lastrowid,))
        rows = cur.fetchall()
        car = rows[0]
        conn.close()


    conn = sqlite3.connect("main.db")
    sql = ''' INSERT INTO tickets(image,date,vehicle_id)
                          VALUES(?,?,?) '''
    cur = conn.cursor()
    date_str = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    cur.execute(sql,(image,date_str,car[0],))
    conn.commit()

    print(cur.lastrowid)
    cur = conn.cursor()
    cur.execute("SELECT * FROM tickets WHERE id = ?", (cur.lastrowid,))
    rows = cur.fetchall()

    print(rows)

    ticket = ''
    conn.close()



    return (car,ticket)



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

numberImage = Tkinter.Label(panelB, image=None,height=10)
panelB.add(numberImage)

numberText = Tkinter.Label(panelB, text="Streaming")
panelB.add(numberText)

# tkinter table
conn = sqlite3.connect("main.db")
cur = conn.cursor()
cur.execute("SELECT * FROM vehicles")
rows = cur.fetchall()
conn.close()

table = Table(tk, ["Driver name", "", "Licence Plate Number", "Location"], column_minwidths=[200, 200, 200])


def refresh_table():
    userdata = []
    for row in rows:
        userdata.append([row[2],row[3],row[1],row[4]])

    #userdata = [['Thomas Kidumbuyo', 'KT340LCFU', "Kinondoni"], ['Alex Atanas', 'HRQBDA23301', "Kinondoni"] ]
    table.pack(expand=True, fill=Tkinter.X,padx=10, pady=10)

    if len(userdata)>0:
        table.set_data(userdata)

    #table.on_change_data(scrolling_area.update_viewport)
refresh_table()
def popupmsg(msg):
    popup = Tkinter.Tk()
    popup.wm_title("!")
    label = Tkinter.Label(popup, text=msg)
    label.pack(side="top", fill="x", pady=10)
    B1 = Tkinter.Button(popup, text="Okay", command = popup.destroy)
    B1.pack()
    popup.mainloop()


def loadImage():
   file = tkFileDialog.askopenfile(title='Choose a file')
   if file != None:
       print(file.name)
       detect_number(file.name)

#B = Tkinter.Button(panelB, text ="load image", command = loadImage,height=20)
B = Tkinter.Button(panelB, text ="Load Local image", command = loadImage,height=5)
panelB.add(B)

streaming = True
capture = False

def captureImage():
    global streaming,capture
    capture = True
    # else:
    #     streaming = True
    #     numberText.configure(text="Streaming")
    #     numberText.text = "Streaming"
    #     numberImage.configure(image=None)
    #     numberImage.image = None

C = Tkinter.Button(panelB, text ="Capture Image", command = captureImage,height=5)
panelB.add(C)



# Code to add widgets will go here...
#top.mainloop()

# GPIO.setwarnings(False) # Ignore warning for now
# GPIO.setmode(GPIO.BOARD) # Use physical pin numbering
#
# GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 8 to be an input pin and set initial value to be pulled low (off)
# GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
# GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 12 to be an input pin and set initial value to be pulled low (off)
#
# # trafic light junction 1
# GPIO.setup(29,GPIO.OUT) #GREEN
# GPIO.setup(31,GPIO.OUT) #YELLOW
# GPIO.setup(33,GPIO.OUT) #RED
#
# # trafic light junction 2
# GPIO.setup(35,GPIO.OUT) #GREEN
# GPIO.setup(37,GPIO.OUT) #YELLOW
# GPIO.setup(32,GPIO.OUT) #RED
#
# # trafic light junction 3
# GPIO.setup(36,GPIO.OUT) #GREEN
# GPIO.setup(38,GPIO.OUT) #YELLOW
# GPIO.setup(40,GPIO.OUT) #RED

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
detect_number_button = False
def detect_number():
    global streaming,userdata,detect_number_button
    detect_number_button = True

licence_code = re.compile(r"^T\d{3}[A-Z]{3}$")
livecam = cv2.VideoCapture(0)

while True: # Run forever

    ret,frame = livecam.read()

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)


    img = cv2.resize(img, (620, 480))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # convert to grey scale
    gray = cv2.bilateralFilter(gray, 11, 17, 17)  # Blur to reduce noise
    edged = cv2.Canny(gray, 30, 200)  # Perform Edge detection

    # find contours in the edged image, keep only the largest
    # ones, and initialize our screen contour
    cnts = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]
    screenCnt = None

    for c in cnts:
        # approximate the contour
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)

        # if our approximated contour has four points, then
        # we can assume that we have found our screen
        if len(approx) == 4:
            screenCnt = approx
            cv2.drawContours(img, [screenCnt], -1, (255, 0, 0), 1)

            mask = np.zeros(gray.shape, np.uint8)
            new_image = cv2.drawContours(mask, [screenCnt], 0, 255, -1, )
            new_image = cv2.bitwise_and(img, img, mask=mask)

            # Now crop
            (x, y) = np.where(mask == 255)
            (topx, topy) = (np.min(x), np.min(y))
            (bottomx, bottomy) = (np.max(x), np.max(y))
            Cropped = gray[topx:bottomx + 1, topy:bottomy + 1]

            # Read the number plate
            text = pytesseract.image_to_string(Cropped, config='--psm 11')
            text = re.sub(r'[^\w]', '', text)


            if licence_code.search(text):
                color = (0, 255, 0)
                if(detect_number_button == True):
                    print("Detected Number is:", text)
                    imc = Image.fromarray(Cropped)
                    imgctk = ImageTk.PhotoImage(image=imc)
                    numberImage.configure(image=imgctk)
                    numberImage.image = imgctk

                    numberText.configure(text=text)
                    numberText.text = text

                    car, ticket = save_ticket(text, imageName)
                    popupmsg("This vehicle with number " + car[1] + "")
                    refresh_table()
                    detect_number_button = False
            else:
                color = (0, 0, 255)

            x, y, w, h = cv2.boundingRect(screenCnt)
            cv2.rectangle(img, (x, y), (x + w, y + h), color , 2)
            cv2.putText(img, text, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 2)

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img2 = Image.fromarray(img)
    imagetk = ImageTk.PhotoImage(image=img2)
    mainImage.configure(image=imagetk)
    mainImage.image = imagetk

    if capture :
        capture = False
        imageName = r"files/" + strftime("%Y%m%d%H%M%S", gmtime()) + ".jpg"
        cv2.imwrite(imageName, img)  # save frame as JPEG file
        detect_number()


    #if not interval_started :
    # if GPIO.input(8) == GPIO.HIGH:
    #     if position_1 == False:
    #             print("car passed on junction 1")
    #             position_1 = True
    #             GPIO.output(31,GPIO.HIGH)
    # else:
    #     position_1 = False
    #
    # if GPIO.input(10) == GPIO.HIGH:
    #     if position_2 == False:
    #             print("car passed on junction 2")
    #             position_2 = True
    #             GPIO.output(37,GPIO.HIGH)
    # else:
    #     position_2 = False
    #
    # if GPIO.input(12) == GPIO.HIGH:
    #     if position_3 == False:
    #             print("car passed on junction 3")
    #             position_3 = True
    #             GPIO.output(38,GPIO.HIGH)
    # else:
    #     position_3 = False
    #
    # if green_trafic is 1:
    #
    #     GPIO.output(29,GPIO.HIGH)
    #     GPIO.output(31,GPIO.LOW)
    #     GPIO.output(33,GPIO.LOW)
    #
    #     GPIO.output(35,GPIO.LOW)
    #     GPIO.output(37,GPIO.LOW)
    #     GPIO.output(32,GPIO.HIGH)
    #
    #     GPIO.output(36,GPIO.LOW)
    #     GPIO.output(38,GPIO.LOW)
    #     GPIO.output(40,GPIO.HIGH)
    #
    # elif green_trafic is 2:
    #
    #     GPIO.output(29,GPIO.LOW)
    #     GPIO.output(31,GPIO.LOW)
    #     GPIO.output(33,GPIO.HIGH)
    #
    #     GPIO.output(35,GPIO.HIGH)
    #     GPIO.output(37,GPIO.LOW)
    #     GPIO.output(32,GPIO.LOW)
    #
    #     GPIO.output(36,GPIO.LOW)
    #     GPIO.output(38,GPIO.LOW)
    #     GPIO.output(40,GPIO.HIGH)
    #
    # elif green_trafic is 3:
    #
    #     GPIO.output(29,GPIO.LOW)
    #     GPIO.output(31,GPIO.LOW)
    #     GPIO.output(33,GPIO.HIGH)
    #
    #     GPIO.output(35,GPIO.LOW)
    #     GPIO.output(37,GPIO.LOW)
    #     GPIO.output(32,GPIO.HIGH)
    #
    #     GPIO.output(36,GPIO.HIGH)
    #     GPIO.output(38,GPIO.LOW)
    #     GPIO.output(40,GPIO.LOW)
    #
    # if yellow_trafic is 1:
    #     GPIO.output(29,GPIO.LOW)
    #     GPIO.output(31,GPIO.HIGH)
    #     GPIO.output(33,GPIO.LOW)
    # elif yellow_trafic is 2:
    #     GPIO.output(35,GPIO.LOW)
    #     GPIO.output(37,GPIO.HIGH)
    #     GPIO.output(32,GPIO.LOW)
    # elif yellow_trafic is 3:
    #     GPIO.output(36,GPIO.LOW)
    #     GPIO.output(38,GPIO.HIGH)
    #     GPIO.output(40,GPIO.LOW)

    if not taking_picture and ((position_1 and green_trafic is not 1) or (position_2 and green_trafic is not 2) or (position_3 and green_trafic is not 3)):
        captureImage()
            
    tk.update_idletasks()
    tk.update()
            


    

