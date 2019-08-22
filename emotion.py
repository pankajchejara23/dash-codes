
import requests
import cv2
import sys
import time
from _thread import start_new_thread

headers=dict()



headers = { 'Ocp-Apim-Subscription-Key': "399da93bc8ad4712b41ddbc6bd37c17f",'Content-Type':'application/octet-stream' }

params = {
    'returnFaceId': 'true',
    'returnFaceLandmarks': 'false',
    'returnFaceAttributes': 'emotion',
}

face_api_url="https://westcentralus.api.cognitive.microsoft.com/face/v1.0/detect"

def emotion_detection(image):
	with open(image, 'rb') as f:
		response = requests.post(face_api_url, params=params, headers=headers, data=f)
		faces = response.json()
		print(faces)
		print("\n---------------------")
		print("\n"+f.name+":")
		print("\n---------------------")
		face_emotion=faces[0]
		for k,v in face_emotion['faceAttributes']['emotion'].items():
			print (" ",k,":",v)
		print("\n---------------------")

# Capture web-cam image and print detected emotion using microsoft azure services

cap=cv2.VideoCapture(0)
for i in range(1):
	time.sleep(0.5)
	return_value,image=cap.read()
	cv2.imwrite("pankaj_"+str(i)+".png",image)
	start_new_thread(emotion_detection,("pankaj_"+str(i)+".png",))
	time.sleep(5)
del(cap)
