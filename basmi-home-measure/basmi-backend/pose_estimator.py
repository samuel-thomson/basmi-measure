import os
import math

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import mediapipe as mp
from mediapipe.tasks import python
from mediapipe import solutions
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

from mmpose.apis import MMPoseInferencer

import cv2
import numpy as np


def distance_between_points(point_one, point_two):
    return math.sqrt((point_one[0] - point_two[0]) ** 2 + (point_one[1] - point_two[1]) ** 2)

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

class PoseEstimator:
    def __init__(self):
        self.model_path = 'pose_landmarker_full.task'
        self.base_options = python.BaseOptions(model_asset_path=self.model_path)
        self.options = vision.PoseLandmarkerOptions(
            base_options=self.base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(self.options)

        self.inferencer_2d = MMPoseInferencer('wholebody')
        self.inferencer_3d = MMPoseInferencer(pose3d='human3d')

    def media_pipe_inference(self, input_path):
        image = mp.Image.create_from_file(input_path)
        detection_result = self.detector.detect(image)

        pose_landmarks_list = detection_result.pose_landmarks
        pose_world_landmarks_list  = detection_result.pose_world_landmarks

        landmarks_data = []
        world_landmarks_data = []

        if pose_landmarks_list:
            for idx in range(len(pose_landmarks_list)):
                for i, lm in enumerate(pose_landmarks_list[idx]):
                    landmarks_data.append({
                        "id": i,
                        "x": lm.x,
                        "y": lm.y,
                        "z": lm.z
                    })


            if pose_world_landmarks_list:
                for idx in range(len(pose_world_landmarks_list)):
                    for i, lm in enumerate(pose_world_landmarks_list[idx]):
                        world_landmarks_data.append({
                            "id": i,
                            "x": lm.x,
                            "y": lm.y,
                            "z": lm.z
                        })

        return landmarks_data, world_landmarks_data

    def wholebody_inference(self, input_path):
        result_generator = self.inferencer_2d(input_path, draw_bbox=True)
        result = next(result_generator)

        keypoints = result['predictions'][0][0]['keypoints']

        return keypoints

    def human3d_inference(self, input_path):
        result_generator = self.inferencer_3d(input_path, draw_bbox=True) #change to vis_out_dir='MMPose/human3d-results/'
        result = next(result_generator)

        keypoints = result['predictions'][0][0]['keypoints']
        return keypoints

    def tragus_to_wall_left(self, input_path): #human3d
        predictions = self.human3d_inference(input_path)
        result = abs(predictions[10][2]-predictions[8][2])

        return round(result * 100, 1)

    def tragus_to_wall_right(self, input_path): #human3d
        predictions = self.human3d_inference(input_path)
        result = abs(predictions[10][2]-predictions[8][2])

        return round(result * 100, 1)

    def side_helper_calibration(self, image_shape, landmarks_data, world_landmarks_data):
        shoulder = landmarks_data[11]
        toe = landmarks_data[31]
        h, w = image_shape
        shoulder_coord = [int(shoulder["x"] * w), int(shoulder["y"] * h)]
        toe_coord = [int(toe["x"] * w), int(toe["y"] * h)]
        pixel_distance = math.dist(shoulder_coord, toe_coord)

        shoulder_world = world_landmarks_data[11]
        toe_world = world_landmarks_data[31]
        shoulder_point = [shoulder_world["x"], shoulder_world["y"], shoulder_world["z"]]
        toe_point = [toe_world["x"], toe_world["y"], toe_world["z"]]
        world_distance = euclidean_distance(shoulder_point, toe_point)

        return world_distance / pixel_distance

    def side_flexion_left(self, before_input_path, after_input_path): #MediaPipe
        before_landmarks_data, before_world_landmarks_data = self.media_pipe_inference(before_input_path)
        after_landmarks_data, after_world_landmarks_data = self.media_pipe_inference(after_input_path)

        h_before = before_landmarks_data[17]
        f_before = before_landmarks_data[31]
        image = cv2.imread(before_input_path)
        h, w, _ = image.shape
        h_y = int(h_before["y"] * h)
        f_y = int(f_before["y"] * h)
        pixel_distance = abs(h_y - f_y)
        pixel_size = self.side_helper_calibration((h, w), before_landmarks_data, before_world_landmarks_data)
        before = pixel_distance * pixel_size

        h_after = after_landmarks_data[17]
        f_after = after_landmarks_data[31]
        image = cv2.imread(after_input_path)
        h, w, _ = image.shape
        h_y = int(h_after["y"] * h)
        f_y = int(f_after["y"] * h)
        pixel_distance = abs(h_y - f_y)
        pixel_size = self.side_helper_calibration((h, w), after_landmarks_data, after_world_landmarks_data)
        after = pixel_distance * pixel_size

        result = before - after

        return abs(round(result*100, 1))

    def side_flexion_right(self, before_input_path, after_input_path): #MediaPipe
        before_landmarks_data, before_world_landmarks_data = self.media_pipe_inference(before_input_path)
        after_landmarks_data, after_world_landmarks_data = self.media_pipe_inference(after_input_path)

        h_before = before_landmarks_data[18]
        f_before = before_landmarks_data[32]
        image = cv2.imread(before_input_path)
        h, w, _ = image.shape
        h_y = int(h_before["y"] * h)
        f_y = int(f_before["y"] * h)
        pixel_distance = abs(h_y - f_y)
        pixel_size = self.side_helper_calibration((h, w), before_landmarks_data, before_world_landmarks_data)
        before = pixel_distance * pixel_size

        h_after = after_landmarks_data[18]
        f_after = after_landmarks_data[32]
        image = cv2.imread(after_input_path)
        h, w, _ = image.shape
        h_y = int(h_after["y"] * h)
        f_y = int(f_after["y"] * h)
        pixel_distance = abs(h_y - f_y)
        pixel_size = self.side_helper_calibration((h, w), after_landmarks_data, after_world_landmarks_data)
        after = pixel_distance * pixel_size

        result = before - after

        return abs(round(result*100, 1))

    def lumbar_helper_calibration(self, predictions, shin_length):
        model_shin = distance_between_points(predictions[14], predictions[16])
        ratio = model_shin / shin_length

        return ratio

    def lumbar_flexion(self, before_input_path, after_input_path): #wholebody
        #Estimate shin length with MediaPipe
        _, world_landmark_data = self.media_pipe_inference(before_input_path)
        kneecap = world_landmark_data[25]
        ankle = world_landmark_data[27]
        kneecap_point = [kneecap["x"], kneecap["y"], kneecap["z"]]
        ankle_point = [ankle["x"], ankle["y"], ankle["z"]]
        shin_length = euclidean_distance(kneecap_point, ankle_point)
        shin_length = shin_length * 100

        before_predictions = self.wholebody_inference(before_input_path)
        after_predictions = self.wholebody_inference(after_input_path)

        lh_before = before_predictions[104]
        lf_before = before_predictions[18]

        lh_after = after_predictions[104]
        lf_after = after_predictions[18]

        rh_before = before_predictions[125]
        rf_before = before_predictions[21]

        rh_after = after_predictions[125]
        rf_after = after_predictions[21]

        left_distance_before = lf_before[1] - lh_before[1]
        right_distance_before = rf_before[1] - rh_before[1]
        before_ratio = self.lumbar_helper_calibration(before_predictions, shin_length)
        left_before = left_distance_before / before_ratio
        right_before = right_distance_before / before_ratio

        left_distance_after = lf_after[1] - lh_after[1]
        right_distance_after = rf_after[1] - rh_after[1]
        after_ratio = self.lumbar_helper_calibration(after_predictions, shin_length)
        left_after = left_distance_after / after_ratio
        right_after = right_distance_after / after_ratio

        left = left_before - left_after
        right = right_before - right_after

        return abs(round(left, 1)), abs(round(right,1))

    def cervical_helper(self, before_input_path, after_input_path): #MediaPipe
        _, before_world_landmark_data = self.media_pipe_inference(before_input_path)
        _, after_world_landmark_data = self.media_pipe_inference(after_input_path)
        left_shoulder_before = before_world_landmark_data[11]
        right_shoulder_before = before_world_landmark_data[12]
        shoulder_midpoint_before = [
            (left_shoulder_before["x"] + right_shoulder_before['x'])/2,
            (left_shoulder_before["y"] + right_shoulder_before['y'])/2,
            (left_shoulder_before["z"] + right_shoulder_before['z'])/2
        ]

        nose_before = before_world_landmark_data[0]
        translated_nose_before = [
            nose_before["x"] - shoulder_midpoint_before[0],
            nose_before["y"] - shoulder_midpoint_before[1],
            nose_before["z"] - shoulder_midpoint_before[2]
        ]

        left_shoulder_after = after_world_landmark_data[11]
        right_shoulder_after = after_world_landmark_data[12]
        shoulder_midpoint_after = [
            (left_shoulder_after["x"] + right_shoulder_after['x'])/2,
            (left_shoulder_after["y"] + right_shoulder_after['y'])/2,
            (left_shoulder_after["z"] + right_shoulder_after['z'])/2
        ]

        nose_after = after_world_landmark_data[0]
        translated_nose_after = [
            nose_after["x"] - shoulder_midpoint_after[0],
            nose_after["y"] - shoulder_midpoint_after[1],
            nose_after["z"] - shoulder_midpoint_after[2]
        ]

        dot_product = translated_nose_before[0] * translated_nose_after[0] + translated_nose_before[2] * translated_nose_after[2]
        magnitude_before = math.sqrt(translated_nose_before[0] ** 2 + translated_nose_before[2] ** 2)
        magnitude_after = math.sqrt(translated_nose_after[0] ** 2 + translated_nose_after[2] ** 2)
        rad_angle = math.acos(dot_product/(magnitude_before*magnitude_after))

        angle = math.degrees(rad_angle)

        return abs(round(angle,1))

    def cervical_rotation_left(self, before_input_path, after_input_path): #MediaPipe
        result = self.cervical_helper(before_input_path, after_input_path)
        return result

    def cervical_rotation_right(self, before_input_path, after_input_path): #MediaPipe
        result = self.cervical_helper(before_input_path, after_input_path)
        return result

    def intermalleolar_distance(self, input_path): #MediaPipe
        _, world_landmark_data = self.media_pipe_inference(input_path)
        left_ankle = world_landmark_data[29]
        right_ankle = world_landmark_data[30]
        left_point = [left_ankle["x"], left_ankle["y"], left_ankle["z"]]
        right_point = [right_ankle["x"], right_ankle["y"], right_ankle["z"]]
        result = euclidean_distance(left_point, right_point)
        return abs(round(result * 100, 1))
