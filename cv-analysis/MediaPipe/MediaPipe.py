import mediapipe as mp
from mediapipe.tasks import python
from mediapipe import solutions
from mediapipe.tasks.python import vision
from mediapipe.framework.formats import landmark_pb2

import cv2
import numpy as np
import math

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

class MediaPipe:
    def __init__(self):
        self.model_path = 'MediaPipe/pose_landmarker_full.task'
        self.base_options = python.BaseOptions(model_asset_path=self.model_path)
        self.options = vision.PoseLandmarkerOptions(
            base_options=self.base_options,
            output_segmentation_masks=True)
        self.detector = vision.PoseLandmarker.create_from_options(self.options)

    def produce_annotated_image(self, input_path, output_path):
        image = mp.Image.create_from_file(input_path)
        detection_result = self.detector.detect(image)

        pose_landmarks_list = detection_result.pose_landmarks
        pose_world_landmarks_list  = detection_result.pose_world_landmarks

        annotated_image = image.numpy_view().copy()
        if len(annotated_image.shape) == 3 and annotated_image.shape[2] == 4:
            annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_RGBA2RGB)

        # Loop through the detected poses to visualize.
        if pose_landmarks_list:
            for idx in range(len(pose_landmarks_list)):
                pose_landmarks = pose_landmarks_list[idx]

                # Draw the pose landmarks.
                pose_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
                pose_landmarks_proto.landmark.extend([
                    landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in pose_landmarks
                ])
                solutions.drawing_utils.draw_landmarks(
                    annotated_image,
                    pose_landmarks_proto,
                    solutions.pose.POSE_CONNECTIONS,
                    solutions.drawing_styles.get_default_pose_landmarks_style())

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

        cv2.imwrite(output_path, cv2.cvtColor(annotated_image, cv2.COLOR_RGB2BGR))

        return landmarks_data, world_landmarks_data

    def edge_detection(self, image_path,output_path):
        img = cv2.imread(image_path)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        mp_image_segmentation = mp.solutions.selfie_segmentation
        with mp_image_segmentation.SelfieSegmentation(model_selection=1) as selfie_seg:
            result = selfie_seg.process(img_rgb)
            mask = result.segmentation_mask > 0.5

        mask_uint8 = (mask * 255).astype(np.uint8)
        edges = cv2.Canny(mask_uint8, 100, 200)
        _, x_coords = np.where(edges == 255)

        person_boundary = cv2.bitwise_and(img, img, mask=edges)
        cv2.imwrite(output_path, person_boundary)

        return np.max(x_coords)

    def calibrate(self, image_shape, landmarks_data, world_landmarks_data):
        shoulder = landmarks_data[11]
        toe = landmarks_data[31]
        h, w = image_shape
        shoulder_coord = int(shoulder["x"] * w), int(shoulder["y"] * h)
        toe_coord = int(toe["x"] * w), int(toe["y"] * h)
        pixel_distance = math.dist(shoulder_coord, toe_coord)

        shoulder_world = world_landmarks_data[11]
        toe_world = world_landmarks_data[31]
        shoulder_point = [shoulder_world["x"], shoulder_world["y"], shoulder_world["z"]]
        toe_point = [toe_world["x"], toe_world["y"], toe_world["z"]]
        world_distance = euclidean_distance(shoulder_point, toe_point)

        return world_distance / pixel_distance

    def tragus_to_wall(self, image_path, landmark_data, world_landmark_data, wall_line):
        ear = landmark_data[7]
        image = cv2.imread(image_path)
        h, w, _ = image.shape
        ear_x = int(ear["x"] * w)
        pixel_distance = abs(ear_x - wall_line)
        pixel_size = self.calibrate((h,w), landmark_data, world_landmark_data)
        return pixel_distance * pixel_size

    def side_flexion(self, lb_image, lb_landmarks, lb_world_landmarks, la_image, la_landmarks, la_world_landmarks, rb_image, rb_landmarks, rb_world_landmarks, ra_image, ra_landmarks, ra_world_landmarks):
        lh_before = lb_landmarks[17]
        lf_before = lb_landmarks[31]
        image = cv2.imread(lb_image)
        h, w, _ = image.shape
        lh_y = int(lh_before["y"] * h)
        lf_y = int(lf_before["y"] * h)
        pixel_distance = abs(lh_y - lf_y)
        pixel_size = self.calibrate((h, w), lb_landmarks, lb_world_landmarks)
        left_before = pixel_distance * pixel_size

        lh_after = la_landmarks[17]
        lf_after = la_landmarks[31]
        image = cv2.imread(la_image)
        h, w, _ = image.shape
        lh_y = int(lh_after["y"] * h)
        lf_y = int(lf_after["y"] * h)
        pixel_distance = abs(lh_y - lf_y)
        pixel_size = self.calibrate((h, w), la_landmarks, la_world_landmarks)
        left_after = pixel_distance * pixel_size

        rh_before = rb_landmarks[18]
        rf_before = rb_landmarks[32]
        image = cv2.imread(rb_image)
        h, w, _ = image.shape
        rh_y = int(rh_before["y"] * h)
        rf_y = int(rf_before["y"] * h)
        pixel_distance = abs(rh_y - rf_y)
        pixel_size = self.calibrate((h, w), rb_landmarks, rb_world_landmarks)
        right_before = pixel_distance * pixel_size

        rh_after = ra_landmarks[18]
        rf_after = ra_landmarks[32]
        image = cv2.imread(ra_image)
        h, w, _ = image.shape
        rh_y = int(rh_after["y"] * h)
        rf_y = int(rf_after["y"] * h)
        pixel_distance = abs(rh_y - rf_y)
        pixel_size = self.calibrate((h, w), ra_landmarks, ra_world_landmarks)
        right_after = pixel_distance * pixel_size

        left = left_before - left_after
        right = right_before - right_after

        return left, right

    def lumbar_flexion(self, before_image_path, before_landmarks, before_world_landmarks, after_image_path, after_landmarks, after_world_landmarks):
        lh_before = before_landmarks[17]
        rh_before = before_landmarks[18]

        lf = before_landmarks[31]
        rf = before_landmarks[32]

        lh_after = after_landmarks[17]
        rh_after = after_landmarks[18]

        before_image = cv2.imread(before_image_path)
        after_image = cv2.imread(after_image_path)

        bh, bw, _ = before_image.shape
        ah, aw, _ = after_image.shape

        lhb_y = int(lh_before["y"] * bh)
        rhb_y = int(rh_before["y"] * bh)

        lf_y = int(lf["y"] * bh)
        rf_y = int(rf["y"] * bh)

        lha_y = int(lh_after["y"] * bh)
        rha_y = int(rh_after["y"] * bh)

        lb_pixel_distance = abs(lhb_y-lf_y)
        la_pixel_distance = abs(lha_y - lf_y)

        rb_pixel_distance = abs(rhb_y - rf_y)
        ra_pixel_distance = abs(rha_y - rf_y)

        before_pixel_size = self.calibrate((bh, bw), before_landmarks, before_world_landmarks)
        after_pixel_size = self.calibrate((ah, aw), after_landmarks, after_world_landmarks)

        left_before = lb_pixel_distance * before_pixel_size
        left_after = la_pixel_distance * after_pixel_size
        left = left_before - left_after

        right_before = rb_pixel_distance * before_pixel_size
        right_after = ra_pixel_distance * after_pixel_size
        right = right_before - right_after

        return left, right


    def intermalleolar_distance(self, landmark_data):
        left_ankle = landmark_data[29]
        right_ankle = landmark_data[30]
        left_point = [left_ankle["x"], left_ankle["y"], left_ankle["z"]]
        right_point = [right_ankle["x"], right_ankle["y"], right_ankle["z"]]
        return euclidean_distance(left_point, right_point)

    def cervical_rotation(self, left_before_world_landmarks, left_after_world_landmarks, right_before_world_landmarks, right_after_world_landmarks):
        #left
        left_shoulder_before = left_before_world_landmarks[11]
        right_shoulder_before = left_before_world_landmarks[12]
        shoulder_midpoint_before = [
            (left_shoulder_before["x"] + right_shoulder_before['x'])/2,
            (left_shoulder_before["y"] + right_shoulder_before['y'])/2,
            (left_shoulder_before["z"] + right_shoulder_before['z'])/2
        ]

        nose_before = left_before_world_landmarks[0]
        translated_nose_before = [
            nose_before["x"] - shoulder_midpoint_before[0],
            nose_before["y"] - shoulder_midpoint_before[1],
            nose_before["z"] - shoulder_midpoint_before[2]
        ]

        left_shoulder_after = left_after_world_landmarks[11]
        right_shoulder_after = left_after_world_landmarks[12]
        shoulder_midpoint_after = [
            (left_shoulder_after["x"] + right_shoulder_after['x'])/2,
            (left_shoulder_after["y"] + right_shoulder_after['y'])/2,
            (left_shoulder_after["z"] + right_shoulder_after['z'])/2
        ]

        nose_after = left_after_world_landmarks[0]
        translated_nose_after = [
            nose_after["x"] - shoulder_midpoint_after[0],
            nose_after["y"] - shoulder_midpoint_after[1],
            nose_after["z"] - shoulder_midpoint_after[2]
        ]

        dot_product = translated_nose_before[0] * translated_nose_after[0] + translated_nose_before[2] * translated_nose_after[2]
        magnitude_before = math.sqrt(translated_nose_before[0] ** 2 + translated_nose_before[2] ** 2)
        magnitude_after = math.sqrt(translated_nose_after[0] ** 2 + translated_nose_after[2] ** 2)
        rad_angle = math.acos(dot_product/(magnitude_before*magnitude_after))

        left = math.degrees(rad_angle)

        # right
        left_shoulder_before = right_before_world_landmarks[11]
        right_shoulder_before = right_before_world_landmarks[12]
        shoulder_midpoint_before = [
            (left_shoulder_before["x"] + right_shoulder_before['x']) / 2,
            (left_shoulder_before["y"] + right_shoulder_before['y']) / 2,
            (left_shoulder_before["z"] + right_shoulder_before['z']) / 2
        ]

        nose_before = right_before_world_landmarks[0]
        translated_nose_before = [
            nose_before["x"] - shoulder_midpoint_before[0],
            nose_before["y"] - shoulder_midpoint_before[1],
            nose_before["z"] - shoulder_midpoint_before[2]
        ]

        left_shoulder_after = right_after_world_landmarks[11]
        right_shoulder_after = right_after_world_landmarks[12]
        shoulder_midpoint_after = [
            (left_shoulder_after["x"] + right_shoulder_after['x']) / 2,
            (left_shoulder_after["y"] + right_shoulder_after['y']) / 2,
            (left_shoulder_after["z"] + right_shoulder_after['z']) / 2
        ]

        nose_after = right_after_world_landmarks[0]
        translated_nose_after = [
            nose_after["x"] - shoulder_midpoint_after[0],
            nose_after["y"] - shoulder_midpoint_after[1],
            nose_after["z"] - shoulder_midpoint_after[2]
        ]

        dot_product = translated_nose_before[0] * translated_nose_after[0] + translated_nose_before[2] * translated_nose_after[2]
        magnitude_before = math.sqrt(translated_nose_before[0] ** 2 + translated_nose_before[2] ** 2)
        magnitude_after = math.sqrt(translated_nose_after[0] ** 2 + translated_nose_after[2] ** 2)
        rad_angle = math.acos(dot_product / (magnitude_before * magnitude_after))

        right = math.degrees(rad_angle)

        return left, right

#Testing and development (uncomment to change development)
#cv = MediaPipe()


#tragus_image_path = "MediaPipe\\test-images\\4A.png"
#tragus_result_path = "MediaPipe\\test-images\\4A-result.png"
#tragus_wall_path = "MediaPipe\\openCV-images\\4A-person-wall-edge.png"

#wall = cv.edge_detection(tragus_image_path, tragus_wall_path)
#tragus_landmarks, tragus_world_landmarks = cv.produce_annotated_image(tragus_image_path, tragus_result_path)
#print(cv.tragus_to_wall(tragus_image_path, tragus_landmarks, tragus_world_landmarks, wall))


#lb_image_path = "MediaPipe\\test-images\\4BLB.png"
#la_image_path = "MediaPipe\\test-images\\4BLA.png"
#rb_image_path = "MediaPipe\\test-images\\4BRB.jpg"
#ra_image_path = "MediaPipe\\test-images\\4BRA.jpg"
#lb_result_path = "MediaPipe\\test-images\\4BLB-result.png"
#la_result_path = "MediaPipe\\test-images\\4BLA-result.png"
#rb_result_path = "MediaPipe\\test-images\\4BRB-result.png"
#ra_result_path = "MediaPipe\\test-images\\4BRA-result.png"

#lb_landmarks, lb_world_landmarks = cv.produce_annotated_image(lb_image_path, lb_result_path)
#la_landmarks, la_world_landmarks = cv.produce_annotated_image(la_image_path, la_result_path)
#rb_landmarks, rb_world_landmarks = cv.produce_annotated_image(rb_image_path, rb_result_path)
#ra_landmarks, ra_world_landmarks = cv.produce_annotated_image(ra_image_path, ra_result_path)
#print(cv.side_flexion(lb_image_path, lb_landmarks, lb_world_landmarks,
#                          la_image_path, la_landmarks, la_world_landmarks,
#                          rb_image_path, rb_landmarks, rb_world_landmarks,
#                          ra_image_path, ra_landmarks, ra_world_landmarks))


#before_image_path = "MediaPipe\\test-images\\4CB.png"
#before_result_path = "MediaPipe\\test-images\\4CB-result.png"
#after_image_path = "MediaPipe\\test-images\\4CA.png"
#after_result_path = "MediaPipe\\test-images\\4CA-result.png"
#before_landmarks, before_world_landmarks = cv.produce_annotated_image(before_image_path, before_result_path)
#after_landmarks, after_world_landmarks = cv.produce_annotated_image(after_image_path, after_result_path)
#print(cv.lumbar_flexion(before_image_path, before_landmarks, before_world_landmarks,
#                        after_image_path, after_landmarks, after_world_landmarks))


#ankle_image_path = "MediaPipe\\test-images\\4D.jpg"
#ankle_result_path = "MediaPipe\\test-images\\4D-result.png"
#_, intermalleolar_world_landmarks = cv.produce_annotated_image(ankle_image_path, ankle_result_path)
#print(cv.intermalleolar_distance(intermalleolar_world_landmarks))

#cervical rotation cannot be calculated using MediaPipe from the images collected as it does not recognise topdown views of humans
#cervical_left_before_path = "MediaPipe\\test-images\\0ELB.jpg"
#cervical_left_after_path = "MediaPipe\\test-images\\0ELA.jpg"
#cervical_right_before_path = "MediaPipe\\test-images\\0ERB.png"
#cervical_right_after_path = "MediaPipe\\test-images\\0ERA.png"
#clb_result_path = "MediaPipe\\test-images\\0ELB-result.png"
#cla_result_path = "MediaPipe\\test-images\\0ELA-result.png"
#crb_result_path = "MediaPipe\\test-images\\0ERB-result.png"
#cra_result_path = "MediaPipe\\test-images\\0ERA-result.png"
#_, left_before_world_landmarks = cv.produce_annotated_image(cervical_left_before_path, clb_result_path)
#_, left_after_world_landmarks = cv.produce_annotated_image(cervical_left_after_path, cla_result_path)
#_, right_before_world_landmarks = cv.produce_annotated_image(cervical_right_before_path, crb_result_path)
#_, right_after_world_landmarks = cv.produce_annotated_image(cervical_right_after_path, cra_result_path)
#print(cv.cervical_rotation(left_before_world_landmarks, left_after_world_landmarks, right_before_world_landmarks, right_after_world_landmarks))

#Evaluation
tragus_to_wall_paths = [
    'eval-images/tragus-to-wall/1.PNG', 'eval-images/tragus-to-wall/2.PNG', 'eval-images/tragus-to-wall/3.PNG',
    'eval-images/tragus-to-wall/4.PNG', 'eval-images/tragus-to-wall/5.PNG', 'eval-images/tragus-to-wall/6.PNG',
    'eval-images/tragus-to-wall/7.PNG', 'eval-images/tragus-to-wall/8.PNG', 'eval-images/tragus-to-wall/9.PNG',
    'eval-images/tragus-to-wall/10.PNG'
]
side_flexion_paths = [
    ['eval-images/side-flexion/1LB.PNG', 'eval-images/side-flexion/1LA.PNG', 'eval-images/side-flexion/1RB.PNG', 'eval-images/side-flexion/1RA.PNG'],
    ['eval-images/side-flexion/2LB.PNG', 'eval-images/side-flexion/2LA.PNG', 'eval-images/side-flexion/2RB.PNG', 'eval-images/side-flexion/2RA.PNG'],
    ['eval-images/side-flexion/3LB.PNG', 'eval-images/side-flexion/3LA.PNG', 'eval-images/side-flexion/3RB.PNG', 'eval-images/side-flexion/3RA.PNG'],
    ['eval-images/side-flexion/4LB.PNG', 'eval-images/side-flexion/4LA.PNG', 'eval-images/side-flexion/4RB.jpg', 'eval-images/side-flexion/4RA.jpg'],
    ['eval-images/side-flexion/5B.PNG', 'eval-images/side-flexion/5L.PNG', 'eval-images/side-flexion/5B.PNG', 'eval-images/side-flexion/5R.PNG'],
    ['eval-images/side-flexion/6B.PNG', 'eval-images/side-flexion/6L.PNG', 'eval-images/side-flexion/6B.PNG', 'eval-images/side-flexion/6R.PNG'],
    ['eval-images/side-flexion/7LB.PNG', 'eval-images/side-flexion/7LA.PNG', 'eval-images/side-flexion/7RB.PNG', 'eval-images/side-flexion/7RA.PNG'],
    ['eval-images/side-flexion/8LB.PNG', 'eval-images/side-flexion/8LA.PNG', 'eval-images/side-flexion/8RB.PNG', 'eval-images/side-flexion/8RA.PNG'],
    ['eval-images/side-flexion/9LB.PNG', 'eval-images/side-flexion/9LA.PNG', 'eval-images/side-flexion/9RB.PNG', 'eval-images/side-flexion/9RA.PNG'],
    ['eval-images/side-flexion/10LB.PNG', 'eval-images/side-flexion/10LA.PNG', 'eval-images/side-flexion/10RB.PNG', 'eval-images/side-flexion/10RA.PNG']
]
lumbar_flexion_paths = [
    ['eval-images/lumbar-flexion/1B.PNG', 'eval-images/lumbar-flexion/1A.PNG'],
    ['eval-images/lumbar-flexion/2B.PNG', 'eval-images/lumbar-flexion/2A.PNG'],
    ['eval-images/lumbar-flexion/3B.PNG', 'eval-images/lumbar-flexion/3A.PNG'],
    ['eval-images/lumbar-flexion/4B.PNG', 'eval-images/lumbar-flexion/4A.PNG'],
    ['eval-images/lumbar-flexion/5B.PNG', 'eval-images/lumbar-flexion/5A.PNG'],
    ['eval-images/lumbar-flexion/6B.PNG', 'eval-images/lumbar-flexion/6A.PNG'],
    ['eval-images/lumbar-flexion/7B.PNG', 'eval-images/lumbar-flexion/7A.PNG'],
    ['eval-images/lumbar-flexion/8B.PNG', 'eval-images/lumbar-flexion/8A.PNG'],
    ['eval-images/lumbar-flexion/9B.PNG', 'eval-images/lumbar-flexion/9A.PNG'],
    ['eval-images/lumbar-flexion/10B.PNG', 'eval-images/lumbar-flexion/10A.PNG']
]
intermalleolar_distance_paths = [
    'eval-images/intermalleolar-distance/1.jpg', 'eval-images/intermalleolar-distance/2.jpg', 'eval-images/intermalleolar-distance/3.jpg',
    'eval-images/intermalleolar-distance/4.jpg', 'eval-images/intermalleolar-distance/5.jpg', 'eval-images/intermalleolar-distance/6.jpg',
    'eval-images/intermalleolar-distance/7.jpg', 'eval-images/intermalleolar-distance/8.jpg', 'eval-images/intermalleolar-distance/9.jpg',
    'eval-images/intermalleolar-distance/10.jpg'
]
cervical_rotation_paths = [
    'eval-images/cervical-rotation/0LB.jpg', 'eval-images/cervical-rotation/0LA.jpg',
   'eval-images/cervical-rotation/0RB.PNG', 'eval-images/cervical-rotation/0RA.PNG'
]

cv = MediaPipe()

tragus_to_wall_results = []
for x in range(10):
    wall = cv.edge_detection(tragus_to_wall_paths[x], 'eval-images/MediaPipe/tragus-walls/' + str(x+1) + '.png')
    tragus_landmarks, tragus_world_landmarks = cv.produce_annotated_image(tragus_to_wall_paths[x], 'eval-images/MediaPipe/tragus-results/' + str(x+1) + '.png')
    result = cv.tragus_to_wall(tragus_to_wall_paths[x], tragus_landmarks, tragus_world_landmarks, wall)
    tragus_to_wall_results.append(result)

side_flexion_results = []
for x in range(10):
    lb_landmarks, lb_world_landmarks = cv.produce_annotated_image(side_flexion_paths[x][0], 'eval-images/MediaPipe/side-results/' + str(x+1) + 'LB.png')
    la_landmarks, la_world_landmarks = cv.produce_annotated_image(side_flexion_paths[x][1], 'eval-images/MediaPipe/side-results/' + str(x+1) + 'LA.png')
    rb_landmarks, rb_world_landmarks = cv.produce_annotated_image(side_flexion_paths[x][2], 'eval-images/MediaPipe/side-results/' + str(x+1) + 'RB.png')
    ra_landmarks, ra_world_landmarks = cv.produce_annotated_image(side_flexion_paths[x][3], 'eval-images/MediaPipe/side-results/' + str(x+1) + 'RA.png')
    result = cv.side_flexion(side_flexion_paths[x][0], lb_landmarks, lb_world_landmarks,
                             side_flexion_paths[x][1], la_landmarks, la_world_landmarks,
                            side_flexion_paths[x][2], rb_landmarks, rb_world_landmarks,
                            side_flexion_paths[x][3], ra_landmarks, ra_world_landmarks)
    side_flexion_results.append(result)

lumbar_flexion_results = []
for x in range(10):
    b_landmarks, b_world_landmarks = cv.produce_annotated_image(lumbar_flexion_paths[x][0], 'eval-images/MediaPipe/lumbar-results/' + str(x+1) + 'B.png')
    a_landmarks, a_world_landmarks = cv.produce_annotated_image(lumbar_flexion_paths[x][1], 'eval-images/MediaPipe/lumbar-results/' + str(x+1) + 'A.png')
    result = cv.lumbar_flexion(lumbar_flexion_paths[x][0], b_landmarks, b_world_landmarks,
                             lumbar_flexion_paths[x][1], a_landmarks, a_world_landmarks)
    lumbar_flexion_results.append(result)

intermalleolar_distance_results = []
for x in range(10):
    _, intermalleolar_world_landmarks = cv.produce_annotated_image(intermalleolar_distance_paths[x], 'eval-images/MediaPipe/intermalleolar-results/' + str(x+1) + '.png')
    result = cv.intermalleolar_distance(intermalleolar_world_landmarks)
    intermalleolar_distance_results.append(result)

_, left_before_world_landmarks = cv.produce_annotated_image(cervical_rotation_paths[0], 'eval-images/MediaPipe/cervical-results/0LB-result.PNG')
_, left_after_world_landmarks = cv.produce_annotated_image(cervical_rotation_paths[1], 'eval-images/MediaPipe/cervical-results/0LA-result.PNG')
_, right_before_world_landmarks = cv.produce_annotated_image(cervical_rotation_paths[2], 'eval-images/MediaPipe/cervical-results/0RB-result.PNG')
_, right_after_world_landmarks = cv.produce_annotated_image(cervical_rotation_paths[3], 'eval-images/MediaPipe/cervical-results/0RA-result.PNG')
cervical_rotation_result = cv.cervical_rotation(left_before_world_landmarks, left_after_world_landmarks, right_before_world_landmarks, right_after_world_landmarks)

print("Tragus to Wall Results:")
print(tragus_to_wall_results)
print("")

print("Side Flexion Results:")
print(side_flexion_results)
print("")

print("Lumbar Flexion Results:")
print(lumbar_flexion_results)
print("")

print("Intermalleolar Distance Results:")
print(intermalleolar_distance_results)
print("")

print("Cervical Rotation Result:")
print(cervical_rotation_result )