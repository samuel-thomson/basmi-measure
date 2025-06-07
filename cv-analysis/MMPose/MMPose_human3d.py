import os
import math

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from mmpose.apis import MMPoseInferencer

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2 + (point1[2] - point2[2])**2)

def distance_between_points(point_one, point_two):
    return math.sqrt((point_one[0] - point_two[0]) ** 2 + (point_one[1] - point_two[1]) ** 2)

class MMPose:
    def __init__(self):
        self.inferencer = MMPoseInferencer(pose3d='human3d')

    def infer_image(self, input_path, output_path):
        result_generator = self.inferencer(input_path, vis_out_dir=output_path, draw_bbox=True) #change to vis_out_dir='MMPose/human3d-results/'
        result = next(result_generator)

        keypoints = result['predictions'][0][0]['keypoints']
        #bbox = result['predictions'][0][0]['bbox'] #'xyxy'
        #bbox = None
        return keypoints#, bbox

    def calibrate(self, predictions):
        knee = predictions[5]
        toe = predictions[6]
        knee_coord = [knee[0], knee[1]]
        toe_coord = [toe[0], toe[1]]
        pixel_distance = distance_between_points(knee_coord, toe_coord)

        knee_world = predictions[5]
        toe_world = predictions[6]
        knee_point = [knee_world[0], knee_world[1], knee_world[2]]
        toe_point = [toe_world[0], toe_world[1], toe_world[2]]
        world_distance = euclidean_distance(knee_point, toe_point)

        return world_distance / pixel_distance

    def tragus_to_wall(self, predictions):
        return abs(predictions[10][2]-predictions[8][2])

    def side_flexion(self, predictions_left_before, predictions_left_after, predictions_right_before, predictions_right_after):
        lh_before = predictions_left_before[13]
        lf_before = predictions_left_before[6]

        lh_y = lh_before[1]
        lf_y = lf_before[1]
        lb_pixel_distance = abs(lh_y - lf_y)
        pixel_size = self.calibrate(predictions_left_before)
        left_before = lb_pixel_distance * pixel_size

        lh_after = predictions_left_after[13]
        lf_after = predictions_left_after[6]

        lh_y = lh_after[1]
        lf_y = lf_after[1]
        la_pixel_distance = abs(lh_y - lf_y)
        pixel_size = self.calibrate(predictions_left_after)
        left_after = la_pixel_distance * pixel_size

        rh_before = predictions_right_before[16]
        rf_before = predictions_right_before[3]

        rh_y = rh_before[1]
        rf_y = rf_before[1]
        rb_pixel_distance = abs(rh_y - rf_y)
        pixel_size = self.calibrate(predictions_right_before)
        right_before = rb_pixel_distance * pixel_size

        rh_after = predictions_right_after[16]
        rf_after = predictions_right_after[3]
        rh_y = rh_after[1]
        rf_y = rf_after[1]
        ra_pixel_distance = abs(rh_y - rf_y)
        pixel_size = self.calibrate(predictions_right_after)
        right_after = ra_pixel_distance * pixel_size

        left = left_before - left_after
        right = right_before - right_after

        return abs(left), abs(right)

    def lumbar_flexion(self, predictions_before, predictions_after):
        lh_before = predictions_before[13]
        lf_before = predictions_before[6]

        lh_y = lh_before[1]
        lf_y = lf_before[1]
        pixel_distance = abs(lh_y - lf_y)
        before_pixel_size = self.calibrate(predictions_before)
        left_before = pixel_distance * before_pixel_size

        lh_after = predictions_after[13]
        lf_after = predictions_after[6]

        lh_y = lh_after[1]
        lf_y = lf_after[1]
        pixel_distance = abs(lh_y - lf_y)
        after_pixel_size = self.calibrate(predictions_after)
        left_after = pixel_distance * after_pixel_size

        rh_before = predictions_before[16]
        rf_before = predictions_before[3]

        rh_y = rh_before[1]
        rf_y = rf_before[1]
        pixel_distance = abs(rh_y - rf_y)
        right_before = pixel_distance * before_pixel_size

        rh_after = predictions_after[16]
        rf_after = predictions_after[3]

        rh_y = rh_after[1]
        rf_y = rf_after[1]
        pixel_distance = abs(rh_y - rf_y)
        right_after = pixel_distance * after_pixel_size

        left = left_before - left_after
        right = right_before - right_after

        return abs(left), abs(right)

    def intermalleolar_distance(self, predictions):
        return euclidean_distance(predictions[3], predictions[6])

    def cervical_rotation(self, left_before_predictions, left_after_predictions, right_before_predictions, right_after_predictions):
        # left
        axis_before = left_before_predictions[8]
        head_before = left_before_predictions[10]
        translated_before = [
            head_before[0] - axis_before[0],
            head_before[1] - axis_before[1],
            head_before[2] - axis_before[2],
        ]

        axis_after = left_after_predictions[8]
        head_after = left_after_predictions[10]
        translated_after = [
            head_after[0] - axis_after[0],
            head_after[1] - axis_after[1],
            head_after[2] - axis_after[2],
        ]

        dot_product = translated_before[0] * translated_after[0] + translated_before[2] * translated_after[2]
        magnitude_before = math.sqrt(translated_before[0] ** 2 + translated_before[2] ** 2)
        magnitude_after = math.sqrt(translated_after[0] ** 2 + translated_after[2] ** 2)
        rad_angle = math.acos(dot_product / (magnitude_before * magnitude_after))

        left = math.degrees(rad_angle)

        # right
        axis_before = right_before_predictions[8]
        head_before = right_before_predictions[10]
        translated_before = [
            head_before[0] - axis_before[0],
            head_before[1] - axis_before[1],
            head_before[2] - axis_before[2],
        ]

        axis_after = right_after_predictions[8]
        head_after = right_after_predictions[10]
        translated_after = [
            head_after[0] - axis_after[0],
            head_after[1] - axis_after[1],
            head_after[2] - axis_after[2],
        ]

        dot_product = translated_before[0] * translated_after[0] + translated_before[2] * translated_after[2]
        magnitude_before = math.sqrt(translated_before[0] ** 2 + translated_before[2] ** 2)
        magnitude_after = math.sqrt(translated_after[0] ** 2 + translated_after[2] ** 2)
        rad_angle = math.acos(dot_product / (magnitude_before * magnitude_after))

        right = math.degrees(rad_angle)

        return left, right

#Testing and development (uncomment to change development)

#cv = MMPose()

#tragus_image_path = 'MMPose/test-images/4A.png'
#predictions = cv.infer_image(tragus_image_path)
#print(cv.tragus_to_wall(predictions))

#side_left_before_path = 'MMPose/test-images/4BLB.png'
#side_left_after_path = 'MMPose/test-images/4BLA.png'
#side_right_before_path = 'MMPose/test-images/4BRB.jpg'
#side_right_after_path = 'MMPose/test-images/4BRA.jpg'
#left_before_predictions = cv.infer_image(side_left_before_path)
#left_after_predictions = cv.infer_image(side_left_after_path)
#right_before_predictions = cv.infer_image(side_right_before_path)
#right_after_predictions = cv.infer_image(side_right_after_path)
#print(cv.side_flexion(left_before_predictions, left_after_predictions, right_before_predictions, right_after_predictions))

#lumbar_before_path = 'MMPose/test-images/4CB.png'
#lumbar_after_path = 'MMPose/test-images/4CA.png'
#before_predictions = cv.infer_image(lumbar_before_path)
#after_predictions = cv.infer_image(lumbar_after_path)
#print(cv.lumbar_flexion(before_predictions, after_predictions))

#ankle_image_path = 'MMPose/test-images/4D.jpg'
#predictions = cv.infer_image(ankle_image_path)
#print(cv.intermalleolar_distance(predictions))

#cervical_left_before_path = "MMPose/test-images/0ELB.jpg"
#cervical_left_after_path = "MMPose/test-images/0ELA.jpg"
#cervical_right_before_path = "MMPose/test-images/0ERB.png"
#cervical_right_after_path = "MMPose/test-images/0ERA.png"
#left_before_predictions = cv.infer_image(cervical_left_before_path)
#left_after_predictions = cv.infer_image(cervical_left_after_path)
#right_before_predictions = cv.infer_image(cervical_right_before_path)
#right_after_world_landmarks = cv.infer_image(cervical_right_after_path)
#print(cv.cervical_rotation(left_before_predictions, left_after_predictions, right_before_predictions, right_after_world_landmarks))

#For Visualising
#cv.infer_image("MMPose/test-images/4EB.png")
#cv.infer_image("MMPose/test-images/4EL.png")
#cv.infer_image("MMPose/test-images/4ER.png")


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

cv = MMPose()

tragus_to_wall_results = []
for x in range(10):
    predictions = cv.infer_image(tragus_to_wall_paths[x], 'eval-images/human3d/tragus-results/' + str(x+1) + '.png')
    result = cv.tragus_to_wall(predictions)
    tragus_to_wall_results.append(result)

side_flexion_results = []
for x in range(10):
    left_before_predictions = cv.infer_image(side_flexion_paths[x][0], 'eval-images/human3d/side-results/' + str(x+1) + 'LB.png')
    left_after_predictions = cv.infer_image(side_flexion_paths[x][1], 'eval-images/human3d/side-results/' + str(x+1) + 'LA.png')
    right_before_predictions = cv.infer_image(side_flexion_paths[x][2], 'eval-images/human3d/side-results/' + str(x+1) + 'RB.png')
    right_after_predictions = cv.infer_image(side_flexion_paths[x][3], 'eval-images/human3d/side-results/' + str(x+1) + 'RA.png')
    result = cv.side_flexion(left_before_predictions, left_after_predictions, right_before_predictions, right_after_predictions)
    side_flexion_results.append(result)

lumbar_flexion_results = []
for x in range(10):
    before_predictions = cv.infer_image(lumbar_flexion_paths[x][0], 'eval-images/human3d/lumbar-results/' + str(x+1) + 'B.png')
    after_predictions = cv.infer_image(lumbar_flexion_paths[x][1], 'eval-images/human3d/lumbar-results/' + str(x+1) + 'A.png')
    result = cv.lumbar_flexion(before_predictions, after_predictions)
    lumbar_flexion_results.append(result)

intermalleolar_distance_results = []
for x in range(10):
    predictions = cv.infer_image(intermalleolar_distance_paths[x], 'eval-images/human3d/intermalleolar-results/' + str(x+1) + '.png')
    result = cv.intermalleolar_distance(predictions)
    intermalleolar_distance_results.append(result)

left_before_predictions = cv.infer_image(cervical_rotation_paths[0], 'eval-images/human3d/cervical-results/0LB-result.PNG')
left_after_predictions = cv.infer_image(cervical_rotation_paths[1], 'eval-images/human3d/cervical-results/0LA-result.PNG')
right_before_predictions = cv.infer_image(cervical_rotation_paths[2], 'eval-images/human3d/cervical-results/0RB-result.PNG')
right_after_world_landmarks = cv.infer_image(cervical_rotation_paths[3], 'eval-images/human3d/cervical-results/0RA-result.PNG')
cervical_rotation_result = cv.cervical_rotation(left_before_predictions, left_after_predictions, right_before_predictions, right_after_world_landmarks)

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