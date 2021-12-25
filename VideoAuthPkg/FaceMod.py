import os
from tkinter.constants import E
import cv2
from .face_recognition.api import face_distance 
import numpy as np
from . import face_recognition

from scipy.spatial import distance as dist
from imutils import face_utils
#import imutils
import dlib
import getpass
import time

from cryptography.fernet import Fernet
from ZeroVOperations import getZeroVDevice

eKey = b'AqYASHHw6ZiTQmtzFeu8iOTpG6KXLgoSGjBp4lh7_GQ='
fernet = Fernet(eKey)

default_path = "/.config/.eth-wallet"

EYE_AR_THRESH = 0.3
EYE_AR_CONSEC_FRAMES = 3


class VideoAuth:

    def __init__(self):
        try:
            self.face_cascade = cv2.CascadeClassifier('/home/{}/.config/NV/models/haar.xml'.format(getpass.getuser()))
            self.CONFIG_DIR = getZeroVDevice()['devicePath'] + default_path + '/profiles'
            self.path = self.CONFIG_DIR
            self.images = []
            self.class_names = []
            self.mylist = os.listdir(self.path)
            self.valid_once = False
            
            # Attributes for Liveliness Detection
            self.COUNTER = 0
            self.TOTAL = 0
            self.detector = dlib.get_frontal_face_detector()
            self.predictor = dlib.shape_predictor(face_recognition.api.predictor_68_point_model)

            (self.lStart, self.lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
            (self.rStart, self.rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

            for cls in self.mylist:
                file = open(f'{self.path}/{cls}', 'rb')
                raw_img = fernet.decrypt(file.read())
                file.close()
                nparr = np.frombuffer(raw_img, dtype=np.uint8)
                img_np = cv2.imdecode(nparr, flags = 1)
                #curImg = cv2.imread(f'{self.path}/{cls}') # cls is the name of the image. 
                curImg = img_np
                self.images.append(curImg)
                self.class_names.append(os.path.splitext(cls)[0]) # splittext is used to get name of image without it's extension
            
        except Exception:
            pass
        
        try:
            self.encodelistknown = self.__findEncodings(self.images) # will create the list of images in encoded manner
        except Exception:
            pass

        self.__decideCamera()

        self.cap = cv2.VideoCapture(self.camera)
        print("Camera Started", self.camera)

    def __findEncodings(self, images):
        self.encodelist = []
        for img in images:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encode = face_recognition.face_encodings(img)[0]
            self.encodelist.append(encode)
        return self.encodelist

    def __decideCamera(self):
        for i in range(10):
            try:
                cap = cv2.VideoCapture(i)
                _, img = cap.read()
                cv2.resize(img, (0,0),None,0.25,0.25)
                print("Captured Camera", i)
                cap.release()
                break
            except Exception as e:
                print(e)
                print("Failed Camera", i)

        self.camera = i


    def get_blank_feed_with_faces(self):
        _, self.frame = self.cap.read()
        self.frame = cv2.flip(self.frame, 1)
        self.img = self.frame        
        gray = cv2.cvtColor(self.img,cv2.COLOR_BGR2GRAY)
        self.faces = self.face_cascade.detectMultiScale(gray, scaleFactor = 1.3, minNeighbors = 5)
        for (x,y,w,h) in self.faces:
            cv2.rectangle(self.img,(x,y),(x+w,y+h),(0,0,225),2)
        return self.img, len(self.faces)

    def get_identity_feed(self):
        self.name = None
        imgs = cv2.resize(self.img, (0,0),None,0.25,0.25) # to reduce size to fasten the process
        imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)
        
        facecurframe = face_recognition.face_locations(imgs) # to locate faces in live-frame
        encodecurframe = face_recognition.face_encodings(imgs,facecurframe)
        
        for encodeface,faceloc in zip(encodecurframe,facecurframe):
            matches = face_recognition.compare_faces(self.encodelistknown,encodeface) # compare the images in folder with live stream faces
            facedis = face_recognition.face_distance(self.encodelistknown,encodeface) # gives the list of distance between the images in folder with live stream faces
            print(facedis)
            matchindex = np.argmin(facedis) # we have to select the lowest distance between list, which will be the match image
            
            if min(facedis) < 0.45:
                if matches[matchindex]:
                    self.name = self.class_names[matchindex].upper()
                    #print(self.name)
                    self.valid_once = True
                
                    y1,x2,y2,x1 = faceloc
                    y1,x2,y2,x1 = y1*4,x2*4,y2*4,x1*4
                    cv2.rectangle(self.img,(x1,y1),(x2,y2),(0,255,0),2)
                    cv2.rectangle(self.img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
                    cv2.putText(self.img, self.name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
                    
                    if self.valid_once:
                        self.detectAlive()

        return self.img, self.name, self.TOTAL

    def detectAlive(self):
        self.alive = False
        #self.frame_reduced = imutils.resize(self.frame, width=450)
        self.frame_reduced = self.frame
        gray = cv2.cvtColor(self.frame_reduced, cv2.COLOR_BGR2GRAY)

        # detect faces in the grayscale frame
        rects = self.detector(gray, 0)

        # loop over the face detections
        for rect in rects:
            # determine the facial landmarks for the face region, then
            # convert the facial landmark (x, y)-coordinates to a NumPy
            # array
            shape = self.predictor(gray, rect)
            shape = face_utils.shape_to_np(shape)

            # extract the left and right eye coordinates, then use the
            # coordinates to compute the eye aspect ratio for both eyes
            leftEye = shape[self.lStart:self.lEnd]
            rightEye = shape[self.rStart:self.rEnd]
            leftEAR = self.eye_aspect_ratio(leftEye)
            rightEAR = self.eye_aspect_ratio(rightEye)

            # average the eye aspect ratio together for both eyes
            ear = (leftEAR + rightEAR) / 2.0

            # compute the convex hull for the left and right eye, then
            # visualize each of the eyes
            leftEyeHull = cv2.convexHull(leftEye)
            rightEyeHull = cv2.convexHull(rightEye)
            cv2.drawContours(self.img, [leftEyeHull], -1, (0, 255, 0), 1)
            cv2.drawContours(self.img, [rightEyeHull], -1, (0, 255, 0), 1)

            # check to see if the eye aspect ratio is below the blink
            # threshold, and if so, increment the blink frame counter
            if ear < EYE_AR_THRESH:
                self.COUNTER += 1

            # otherwise, the eye aspect ratio is not below the blink
            # threshold
            else:
                # if the eyes were closed for a sufficient number of
                # then increment the total number of blinks
                if self.COUNTER >= EYE_AR_CONSEC_FRAMES:
                    self.TOTAL += 1

                # reset the eye frame counter
                self.COUNTER = 0

            # draw the total number of blinks on the frame along with
            # the computed eye aspect ratio for the frame
            cv2.putText(self.img, "Blinks: {}".format(self.TOTAL), (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            #cv2.putText(self.frame_reduced, "EAR: {:.2f}".format(ear), (300, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        return

    def grab_photo(self):
        self.photo = self.frame
        return self.photo
	



    @staticmethod
    def eye_aspect_ratio(eye):
            # compute the euclidean distances between the two sets of
        # vertical eye landmarks (x, y)-coordinates
        A = dist.euclidean(eye[1], eye[5])
        B = dist.euclidean(eye[2], eye[4])

        # compute the euclidean distance between the horizontal
        # eye landmark (x, y)-coordinates
        C = dist.euclidean(eye[0], eye[3])

        # compute the eye aspect ratio
        ear = (A + B) / (2.0 * C)

        # return the eye aspect ratio
        return ear



    def __del__(self):
        self.cap.release()
        print("Camera Released", self.camera)






if __name__ == '__main__':
    A = VideoAuth()
    print("Doing Something")

    try:
        while True:
            #time.sleep(0.1)
            img, n = A.get_blank_feed_with_faces()
            print(n)
            if n == 1:
                img, name, total = A.get_identity_feed()
                print(name)
                if total >= 5:
                    break
            
            cv2.imshow('sample', img)
            k = cv2.waitKey(1)
            if k == 113:
                break
    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    del A
