import cv2

cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
while True:
    ret, img = cap.read()
    cv2.imshow('img',img)


cap.release()
out.release()
cv2.destroyAllWindows()
