import cv2
import os
import time
import numpy as np
import pandas as pd
from PIL import Image
import csv

def getid():
   if not os.path.exists('StudentDetails.csv'):
      return 1
   else:
      df = pd.read_csv('StudentDetails.csv')
      names1 = df['Id'].values
      names1 = list(set(names1))
      return int(names1[-1])+1
    
def faceTraining():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

    def getImagesAndLabels(path):
        imagePaths = [os.path.join(path,f) for f in os.listdir(path)] 
        faceSamples=[]
        ids = []
        ids_names = []
        for imagePath in imagePaths:
            PIL_img = Image.open(imagePath).convert('L')
            img_numpy = np.array(PIL_img,'uint8')
            name = os.path.split(imagePath)[-1].split(".")[0]
            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faceSamples.append(img_numpy)
            ids.append(id)

            ids_names.append([id, name])

        return faceSamples,ids,ids_names

    faces,ids,ids_names = getImagesAndLabels('dataset')
    recognizer.train(faces, np.array(ids))
    recognizer.write('trainer/trainer.yml')

    f = open("names.csv", 'w', newline="")
    writer = csv.writer(f)
    writer.writerow(["id", "name"])
    writer.writerows(ids_names)
    f.close()

    df=pd.read_csv('names.csv')
    df.drop_duplicates(subset=['id', 'name'], inplace=True)
    df.to_csv('names.csv',index=False)

def faceDataset(name):
    vid_cam = cv2.VideoCapture(0)
    face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

    face_id = getid()
    count = 0

    while(True):
        _, image_frame = vid_cam.read()
        gray = cv2.cvtColor(image_frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        
        for (x,y,w,h) in faces:
            cv2.rectangle(image_frame, (x,y), (x+w,y+h), (255,0,0), 2)
            count += 1
            cv2.imwrite("dataset/"+name+"." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])

        cv2.imshow('frame', image_frame)
        if cv2.waitKey(100) & 0xFF == ord('q'):
            break
        elif count>100:
            break

    vid_cam.release()
    cv2.destroyAllWindows()
    faceTraining()

    return "face data added successfully"

def faceRecognition():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('trainer/trainer.yml')
    cascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)

    font = cv2.FONT_HERSHEY_SIMPLEX
    cam = cv2.VideoCapture(0)
    df=pd.read_csv('names.csv')
    names = []
    counts = 0
    while True:
            ret, im =cam.read()
            gray = cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray, 1.2,5)

            for(x,y,w,h) in faces:
                counts += 1
                cv2.rectangle(im, (x,y), (x+w,y+h), (0,255,0), 4)
                Id,i = recognizer.predict(gray[y:y+h,x:x+w])

                if i < 60:
                    name=df.loc[(df['id']==Id)]['name'].values[0]
                    cv2.putText(im, name, (x,y-40), font, 2, (255,255,255), 3)
                    names.append(name)
                else:
                    cv2.putText(im, "unknown", (x,y-40), font, 2, (255,255,255), 3)
                    names.append("unknown")

            cv2.imshow('im',im)
            if cv2.waitKey(100) & 0xFF == ord('q'): 
                break
            if counts > 9:
                break

    cam.release()
    cv2.destroyAllWindows()

    counter = 0
    name = names[0]
    for i in names:
        curr_frequency = names.count(i)
        if(curr_frequency> counter):
            counter = curr_frequency
            name = i
    
    return name
