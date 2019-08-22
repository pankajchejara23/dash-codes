import cv2

cap = cv2.VideoCapture(0)
print('loading....')
face_cascade = cv2.CascadeClassifier('/Users/panche/Desktop/cv/haarcascade_frontalface_default.xml')
print('\n complete')
while True:
    ret, img = cap.read()
    print ('\n reading frame')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imshow('img',img)
    print('\n Applying classifier..')
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
    print('\n classification done...')
    print ('\n faces found: ',len(faces))
    for (x,y,w,h) in faces:
        cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = img[y:y+h, x:x+w]

    cv2.imshow('img',img)


cap.release()
out.release()
cv2.destroyAllWindows()
