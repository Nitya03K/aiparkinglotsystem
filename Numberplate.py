import cv2
import numpy as np
import requests
from pprint import pprint

def numberplateRecognition():
    try:
        with open('img.jpg', 'rb') as fp:
            response = requests.post(
                'https://api.platerecognizer.com/v1/plate-reader/',
                files=dict(upload=fp),
                headers={'Authorization': 'Token 81dda232b51e3f7c7620f0830834a6d8c94e0120'})
        results = response.json()
        return results['results'][0]['plate']
    except:
        return False

def numberplateDetection():
    while True:
        video = cv2.VideoCapture(0)
        while True:
            ret,frame = video.read()
            if not ret:
                print('no source')
                break
            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                cv2.imwrite('img.jpg', frame)
                break

        video.release()
        cv2.destroyAllWindows()

        number = numberplateRecognition()
        if number:
            break
        else:
            print('numberplate not recognised')
    return number
