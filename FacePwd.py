from face_lib import face_lib
import cv2

FL = face_lib()

##img_to_verfiy = cv2.imread("") #image that contain face you want verify
##gt_img = cv2.imread("") #image of the face to compare with
##
##face_exist, no_faces_detected = FL.recognition_pipeline(img_to_verfiy, gt_image)
##




from random_word import RandomWords
r = RandomWords()

# Return a single random word
print(r.get_random_word())
# Return list of Random words
print(r.get_random_words())
# Return Word of the day
print(r.word_of_the_day())













