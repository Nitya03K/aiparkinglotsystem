import serial
import time
from Numberplate import numberplateDetection
from face_recognition import faceDataset, faceRecognition
import datetime
import os
import csv
import pandas as pd
from difflib import SequenceMatcher
import sqlite3

data = serial.Serial(
                  'COM14',
                  baudrate = 9600,
                  parity=serial.PARITY_NONE,
                  stopbits=serial.STOPBITS_ONE,
                  bytesize=serial.EIGHTBITS,                  
                  timeout=1
                  )
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

print('waiting for vehicle....')
while True:
    d = data.readline()
    d = d.decode('utf-8', 'ignore')

    if d:
        print(d)
        if d == 'ENTRY':
            number = numberplateDetection().upper()
            print(number)

            name = input("Enter your name")
            res = faceDataset(name)
            print(res)
            
            data.write(str.encode(number))

            while True:
                slot = data.readline()
                slot = slot.decode('utf-8', 'ignore')
                if slot:
                    print(slot)
                    break

            cursor.execute('create table if not exists records(name TEXT, number TEXT, slot TEXT, date TEXT, entry TEXT, exit TEXT)')
            
            Date = datetime.date.today().strftime('%Y-%m-%d')
            Time = datetime.datetime.now().time().strftime('%H:%M:%S')

            row = [name, number, slot, Date, Time]
            print(row)

            cursor.execute('insert into records(name, number, slot, date, entry) values(?,?,?,?,?)', row)
            connection.commit()
            
            print("{} ENTERED AT {}".format(number, Time))

        if d == 'EXIT':
            number = numberplateDetection().upper()
            name = faceRecognition()
            cursor.execute("select * from records where number = '"+number+"' and name = '"+name+"'")
            result = cursor.fetchone()

            if result:
                Time = datetime.datetime.now().time().strftime('%H:%M:%S')

                cursor.execute("update records set exit = '"+Time+"' where number = '"+number+"'")
                connection.commit()

                cursor.execute("select * from records where number = '"+number+"' and name = '"+name+"'")
                result = cursor.fetchone()

                from datetime import datetime 

                start = datetime.strptime(result[4], "%H:%M:%S") 
                end = datetime.strptime(result[5], "%H:%M:%S") 

                difference = end - start 

                seconds = difference.total_seconds() 
                print('difference in seconds is:', seconds)

                ammount = int(seconds)*2

                print("{} EXIT AT {} total amount is {}".format(number, Time, ammount))
                break
            else:
                print("NOT YOUR VEHICLE")
                data.write(str.encode("NOT YOUR VEHICLE"))
        print('waiting for vehicle....')

         
