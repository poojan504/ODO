from keras.preprocessing.image import img_to_array
import cv2
from keras.models import load_model
from keras.utils.data_utils import get_file
from models.face_recognition.wide_resnet import WideResNet
import numpy as np
from pathlib import Path
#import dlib

class Face_Recognizer:
    def __init__(self,show_camera_feed):
        self.camera_ids = [0,1,2,3,4,5]
        # parameters for loading data and images
        detection_model_path = 'models/face_recognition/trained_models/haarcascade_frontalface_default.xml'
        emotion_model_path = 'models/face_recognition/trained_models/_mini_XCEPTION.48-0.62.hdf5'
        #gender_age_model_path = 'models/trained_models/face_recognition/weights.28-3.73.hdf5'
        self.modhash = 'fbe63257a054c1c5466cfd7bf14646d6'
        print('creating face rcognizer')
        # hyper-parameters for bounding boxes shape
        # loading models
        self.face_detection = cv2.CascadeClassifier(detection_model_path)
        self.emotion_classifier = load_model(emotion_model_path, compile=False)
        self.camera = [None]*(len(self.camera_ids)+1);#Adding 1 for MIPI camera

        #weight_file = get_file("weights.28-3.73.hdf5", gender_age_model_path, cache_subdir="pretrained_models",
        #                       file_hash=self.modhash, cache_dir=str(Path(__file__).resolve().parent))

        img_size = 64
        width = 8
        depth = 16
        #self.gender_age_classifier = WideResNet(img_size, depth=depth, k=width)()
        #self.gender_age_classifier.load_weights(weight_file)
        print('loaded models')
        self.emotions = ["angry" ,"disgust","scared", "happy", "sad", "surprised", "neutral"]
        # 0 for laptop camera. 1 for usb camera.
        #self.camera = cv2.VideoCapture(0)
        self.total_cameras = 0
        self.mipi_camera = False

        #Check for MIPI camera
        print("Trying to detect MIPI camera")
        try:
            self.camera[len(self.camera_ids)] = cv2.VideoCapture(gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
            if self.camera[len(self.camera_ids)] is None:
                print("MIPI camera not found")
            elif self.camera[len(self.camera_ids)].isOpened():
                self.mipi_camera = True
                self.camera_id = len(self.camera_ids)
                print("MIPI Camera detected with id:"+str(self.camera_id))
            else:
                print("MIPI camera not found")
        except:
            print("MIPI camera not found")

        if self.mipi_camera is False:
            for i in self.camera_ids:
                print("Trying to detect USB camera")
                try:
                    self.camera[i] = cv2.VideoCapture(i)
                    if(self.camera[i].isOpened()):
                        self.camera_id = i
                        print("USB Camera detected with id:"+str(self.camera_id))
                        self.total_cameras += 1
                        break
                except cv2.error as e:
                    print("Error in camera "+str(i))

        self.total_faces = 0
        self.preds = None
        self.gender = None
        self.age = None
        self.age_gender = None
        self.emotion_probability = None
        self.current_emotion = None
        self.show_camera_feed = show_camera_feed
        if self.show_camera_feed:
            # starting video streaming
            cv2.namedWindow('your_face')
        if self.total_cameras > 0:
            print('created face recognizer')

    #For MIPI camera
    def gstreamer_pipeline(
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=60,
        flip_method=0,
    ):
        return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
        )

    def detect_emotion(self, faces, gray):
        fX, fY, fW, fH = None, None, None, None
        if len(faces) > 0:
            faces = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
                        # Extract the ROI of the face from the grayscale image, resize it to a fixed 48x48 pixels, and then prepare
                # the ROI for classification via the CNN
            roi = gray[fY:fY + fH, fX:fX + fW]
            roi = cv2.resize(roi, (48, 48))
            roi = roi.astype("float") / 255.0
            roi = img_to_array(roi)
            roi = np.expand_dims(roi, axis=0)
            
            self.current_emotion = [None]*len(faces);

            self.preds = self.emotion_classifier.predict(roi)[0]
            self.emotion_probability = np.max(self.preds)
            self.current_emotion = self.emotions[self.preds.argmax()]

    #Currently not in use
    def detect_gender_age(self, frame):
        detector = dlib.get_frontal_face_detector()
        detected = detector(frame, 1)
        img_h, img_w, _ = np.shape(frame)
        faces1 = np.empty((len(detected), img_size, img_size, 3))
        #roi = cv2.resize(roi, (64, 64))
        if len(detected) > 0:
            for i, d in enumerate(detected):
                    x1, y1, x2, y2, w, h = d.left(), d.top(), d.right() + 1, d.bottom() + 1, d.width(), d.height()
                    xw1 = max(int(x1 - margin * w), 0)
                    yw1 = max(int(y1 - margin * h), 0)
                    xw2 = min(int(x2 + margin * w), img_w - 1)
                    yw2 = min(int(y2 + margin * h), img_h - 1)
                    cv2.rectangle(frame1, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    # cv2.rectangle(img, (xw1, yw1), (xw2, yw2), (255, 0, 0), 2)
                    faces1[i, :, :, :] = cv2.resize(frame1[yw1:yw2 + 1, xw1:xw2 + 1, :], (img_size, img_size))

            results = self.gender_age_classifier.predict(faces1)
            predicted_genders = results[0]
            ages = np.arange(0, 101).reshape(101, 1)
            predicted_ages = results[1].dot(ages).flatten()
            for i, d in enumerate(detected):
                self.age_gender = "{}, {}".format(int(predicted_ages[i]),
                                        "M" if predicted_genders[i][0] < 0.5 else "F")


    def display_camera(self, frame, faces):
        if len(faces) > 0:
            faces = sorted(faces, reverse=True, key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
            (fX, fY, fW, fH) = faces
        else:
            fX, fY, fW, fH = 0,0,0,0
        for (i, (emotion, prob)) in enumerate(zip(self.emotions, self.preds)):
            # construct the current emotion text
            text = "{}: {:.2f}%".format(emotion, prob * 100)
            w = int(prob * 300)
            cv2.putText(frame, self.current_emotion, (fX, fY - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
            cv2.rectangle(frame, (fX, fY), (fX + fW, fY + fH),(0, 0, 255), 2)
        cv2.imshow('your_face', frame)

    def start_detection(self):
        #for i in self.camera_ids:
        frame = self.camera[self.camera_id].read()[1]
        #reading the frame
        height , width , layers =  frame.shape
        frame = cv2.resize(frame, (800, height)) 
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_detection.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        self.total_faces = len(faces)
        self.detect_emotion(faces, gray)
        print(self.current_emotion)
        #self.detect_gender_age(frame1)
        if self.show_camera_feed:
            cv2.imshow('your_face', frame)
            self.display_camera(frame, faces)

    def stop_detection(self):
        self.show_camera_feed = False
        self.camera[self.camera_id].release()
        cv2.destroyAllWindows()
