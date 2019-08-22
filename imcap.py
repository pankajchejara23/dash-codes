import cv2

camera = cv2.VideoCapture(0)
ret, img = camera.read()
cv2.imshow('img',img)
del(camera)
