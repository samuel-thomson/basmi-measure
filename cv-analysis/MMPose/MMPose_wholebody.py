import os
import math

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

from mmpose.apis import MMPoseInferencer

def distance_between_points(point_one, point_two):
    return math.sqrt((point_one[0] - point_two[0]) ** 2 + (point_one[1] - point_two[1]) ** 2)

class MMPose:
    def __init__(self):
        self.inferencer = MMPoseInferencer('wholebody')

    def infer_image(self, input_path, output_path):
        result_generator = self.inferencer(input_path, vis_out_dir=output_path, draw_bbox=True) #change to vis_out_dir='MMPose/2d-results/' for development
        result = next(result_generator)

        keypoints = result['predictions'][0][0]['keypoints']
        bbox = result['predictions'][0][0]['bbox'] #'xyxy'

        return keypoints, bbox

    def estimate_shin_length(self, predictions, known_intermalleolar):
        model_intermalleolar = distance_between_points(predictions[16], predictions[17])
        model_shin = distance_between_points(predictions[14], predictions[16])
        ratio = model_intermalleolar / known_intermalleolar

        return model_shin / ratio

    def calibrate_with_shin(self, predictions, known_shin_length):
        model_shin = distance_between_points(predictions[14], predictions[16])
        ratio = model_shin / known_shin_length

        return ratio

    def tragus_to_wall(self, predictions, bbox, shin_length):
        model_distance = bbox[0][2] - predictions[39][0]
        ratio = self.calibrate_with_shin(predictions, shin_length)

        return model_distance / ratio

    def side_flexion(self, predictions_left_before, predictions_left_after, predictions_right_before, predictions_right_after, shin_length):
        lh_before = predictions_left_before[104]
        lf_before = predictions_left_before[18]

        lh_after = predictions_left_after[104]
        lf_after = predictions_left_after[18]

        rh_before = predictions_right_before[125]
        rf_before = predictions_right_before[21]

        rh_after = predictions_right_after[125]
        rf_after = predictions_right_after[21]

        left_distance_before = lf_before[1] - lh_before[1]
        left_before_ratio = self.calibrate_with_shin(predictions_left_before, shin_length)
        left_before = left_distance_before / left_before_ratio

        left_distance_after = lf_after[1] - lh_after[1]
        left_after_ratio = self.calibrate_with_shin(predictions_left_after, shin_length)
        left_after = left_distance_after / left_after_ratio

        right_distance_before = rf_before[1] - rh_before[1]
        right_before_ratio = self.calibrate_with_shin(predictions_right_before, shin_length)
        right_before = right_distance_before / right_before_ratio

        right_distance_after = rf_after[1] - rh_after[1]
        right_after_ratio = self.calibrate_with_shin(predictions_right_after, shin_length)
        right_after = right_distance_after / right_after_ratio

        left = left_before - left_after
        right = right_before - right_after

        return abs(left), abs(right)

    def lumbar_flexion(self, predictions_before, predictions_after, shin_length):
        lh_before = predictions_before[104]
        lf_before = predictions_before[18]

        lh_after = predictions_after[104]
        lf_after = predictions_after[18]

        rh_before = predictions_before[125]
        rf_before = predictions_before[21]

        rh_after = predictions_after[125]
        rf_after = predictions_after[21]

        left_distance_before = lf_before[1] - lh_before[1]
        right_distance_before = rf_before[1] - rh_before[1]
        before_ratio = self.calibrate_with_shin(predictions_before, shin_length)
        left_before = left_distance_before / before_ratio
        right_before = right_distance_before / before_ratio

        left_distance_after = lf_after[1] - lh_after[1]
        right_distance_after = rf_after[1] - rh_after[1]
        after_ratio = self.calibrate_with_shin(predictions_after, shin_length)
        left_after = left_distance_after / after_ratio
        right_after = right_distance_after / after_ratio

        left = left_before - left_after
        right = right_before - right_after

        return abs(left), abs(right)

    def intermalleolar_distance(self, predictions, shin_length):
        model_intermalleolar = distance_between_points(predictions[16], predictions[17])
        ratio = self.calibrate_with_shin(predictions, shin_length)
        return model_intermalleolar / ratio

    def cervical_rotation(self, left_before_predictions, left_after_predictions, right_before_predictions, right_after_predictions):
        # left
        left_shoulder_before = left_before_predictions[6]
        right_shoulder_before = left_before_predictions[7]
        shoulder_midpoint_before = [
            (left_shoulder_before[0] + right_shoulder_before[0]) / 2,
            (left_shoulder_before[1] + right_shoulder_before[1]) / 2
        ]

        nose_before = left_before_predictions[54]
        translated_nose_before = [
            nose_before[0] - shoulder_midpoint_before[0],
            nose_before[1] - shoulder_midpoint_before[1]
        ]

        left_shoulder_after = left_after_predictions[6]
        right_shoulder_after = left_after_predictions[7]
        shoulder_midpoint_after = [
            (left_shoulder_after[0] + right_shoulder_after[0]) / 2,
            (left_shoulder_after[1] + right_shoulder_after[1]) / 2
        ]

        nose_after = left_after_predictions[54]
        translated_nose_after = [
            nose_after[0] - shoulder_midpoint_after[0],
            nose_after[1] - shoulder_midpoint_after[1]
        ]

        dot_product = translated_nose_before[0] * translated_nose_after[0] + translated_nose_before[1] * \
                      translated_nose_after[1]
        magnitude_before = math.sqrt(translated_nose_before[0] ** 2 + translated_nose_before[1] ** 2)
        magnitude_after = math.sqrt(translated_nose_after[0] ** 2 + translated_nose_after[1] ** 2)
        rad_angle = math.acos(dot_product / (magnitude_before * magnitude_after))

        left = math.degrees(rad_angle)

        # right
        left_shoulder_before = right_before_predictions[6]
        right_shoulder_before = right_before_predictions[7]
        shoulder_midpoint_before = [
            (left_shoulder_before[0] + right_shoulder_before[0]) / 2,
            (left_shoulder_before[1] + right_shoulder_before[1]) / 2
        ]

        nose_before = right_before_predictions[54]
        translated_nose_before = [
            nose_before[0] - shoulder_midpoint_before[0],
            nose_before[1] - shoulder_midpoint_before[1]
        ]

        left_shoulder_after = right_after_predictions[6]
        right_shoulder_after = right_after_predictions[7]
        shoulder_midpoint_after = [
            (left_shoulder_after[0] + right_shoulder_after[0]) / 2,
            (left_shoulder_after[1] + right_shoulder_after[1]) / 2
        ]

        nose_after = right_after_predictions[54]
        translated_nose_after = [
            nose_after[0] - shoulder_midpoint_after[0],
            nose_after[1] - shoulder_midpoint_after[1]
        ]

        dot_product = translated_nose_before[0] * translated_nose_after[0] + translated_nose_before[1] * \
                      translated_nose_after[1]
        magnitude_before = math.sqrt(translated_nose_before[0] ** 2 + translated_nose_before[1] ** 2)
        magnitude_after = math.sqrt(translated_nose_after[0] ** 2 + translated_nose_after[1] ** 2)
        rad_angle = math.acos(dot_product / (magnitude_before * magnitude_after))

        right = math.degrees(rad_angle)

        return left, right

#Testing and development (uncomment to change development)

#cv = MMPose()
#ankle_image_path = 'MMPose/test-images/4D.jpg'
#ankle_predictions, _ = cv.infer_image(ankle_image_path)
#shin_length = cv.estimate_shin_length(ankle_predictions, 110)

#tragus_image_path = 'MMPose/test-images/4A.png'
#predictions, bbox = cv.infer_image(tragus_image_path)
#print(cv.tragus_to_wall(predictions, bbox,shin_length))

#side_left_before_path = 'MMPose/test-images/4BLB.png'
#side_left_after_path = 'MMPose/test-images/4BLA.png'
#side_right_before_path = 'MMPose/test-images/4BRB.jpg'
#side_right_after_path = 'MMPose/test-images/4BRA.jpg'
#left_before_predictions, _ = cv.infer_image(side_left_before_path)
#left_after_predictions, _ = cv.infer_image(side_left_after_path)
#right_before_predictions, _ = cv.infer_image(side_right_before_path)
#right_after_predictions, _ = cv.infer_image(side_right_after_path)
#print(cv.side_flexion(left_before_predictions, left_after_predictions, right_before_predictions, right_after_predictions, shin_length))

#lumbar_before_path = 'MMPose/test-images/4CB.png'
#lumbar_after_path = 'MMPose/test-images/4CA.png'
#before_predictions, _ = cv.infer_image(lumbar_before_path)
#after_predictions, _ = cv.infer_image(lumbar_after_path)
#print(cv.lumbar_flexion(before_predictions, after_predictions, shin_length))

#print(cv.intermalleolar_distance(ankle_predictions, shin_length))

#cervical_before_path = "MMPose/test-images/4EB.png"
#cervical_left_path = "MMPose/test-images/4EL.png"
#cervical_right_path = "MMPose/test-images/4ER.png"
#_, _ = cv.infer_image(cervical_before_path)
#_, _ = cv.infer_image(cervical_left_path)
#_, _ = cv.infer_image(cervical_right_path)

#cervical_left_before_path = "MMPose/test-images/0ELB.jpg"
#cervical_left_after_path = "MMPose/test-images/0ELA.jpg"
#cervical_right_before_path = "MMPose/test-images/0ERB.png"
#cervical_right_after_path = "MMPose/test-images/0ERA.png"
#left_before_predictions, _ = cv.infer_image(cervical_left_before_path)
#left_after_predictions, _ = cv.infer_image(cervical_left_after_path)
#right_before_predictions, _ = cv.infer_image(cervical_right_before_path)
#right_after_world_landmarks, _ = cv.infer_image(cervical_right_after_path)
#print(cv.cervical_rotation(left_before_predictions, left_after_predictions, right_before_predictions, right_after_world_landmarks))


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

measured_intermalleolar = [140, 123, 114, 110, 124, 106, 134, 150, 143, 100]
shin_lengths = []
for x in range(10):
    ankle_predictions, _ = cv.infer_image(intermalleolar_distance_paths[x], 'eval-images/wholebody/intermalleolar-results/' + str(x+1) + '.png')
    shin_length = cv.estimate_shin_length(ankle_predictions, measured_intermalleolar[x])
    shin_lengths.append(shin_length)

tragus_to_wall_results = []
for x in range(10):
    predictions, bbox = cv.infer_image(tragus_to_wall_paths[x],'eval-images/wholebody/tragus-results/' + str(x+1) + '.png')
    result = cv.tragus_to_wall(predictions, bbox, shin_lengths[x])
    tragus_to_wall_results.append(result)

side_flexion_results = []
for x in range(10):
    left_before_predictions, _ = cv.infer_image(side_flexion_paths[x][0], 'eval-images/wholebody/side-results/' + str(x+1) + 'LB.png')
    left_after_predictions, _ = cv.infer_image(side_flexion_paths[x][1], 'eval-images/wholebody/side-results/' + str(x+1) + 'LA.png')
    right_before_predictions, _ = cv.infer_image(side_flexion_paths[x][2], 'eval-images/wholebody/side-results/' + str(x+1) + 'RB.png')
    right_after_predictions, _ = cv.infer_image(side_flexion_paths[x][3], 'eval-images/wholebody/side-results/' + str(x+1) + 'RA.png')
    result = cv.side_flexion(left_before_predictions, left_after_predictions, right_before_predictions, right_after_predictions, shin_lengths[x])
    side_flexion_results.append(result)

lumbar_flexion_results = []
for x in range(10):
    before_predictions, _ = cv.infer_image(lumbar_flexion_paths[x][0], 'eval-images/wholebody/lumbar-results/' + str(x+1) + 'B.png')
    after_predictions, _ = cv.infer_image(lumbar_flexion_paths[x][1], 'eval-images/wholebody/lumbar-results/' + str(x+1) + 'A.png')
    result = cv.lumbar_flexion(before_predictions, after_predictions, shin_lengths[x])
    lumbar_flexion_results.append(result)

intermalleolar_distance_results = []
for x in range(10):
    ankle_predictions, _ = cv.infer_image(intermalleolar_distance_paths[x], 'eval-images/wholebody/intermalleolar-results/' + str(x+1) + '.png')
    result = cv.intermalleolar_distance(ankle_predictions, shin_lengths[x])
    intermalleolar_distance_results.append(result)

left_before_predictions, _ = cv.infer_image(cervical_rotation_paths[0], 'eval-images/wholebody/cervical-results/0LB-result.PNG')
left_after_predictions, _ = cv.infer_image(cervical_rotation_paths[1], 'eval-images/wholebody/cervical-results/0LA-result.PNG')
right_before_predictions, _ = cv.infer_image(cervical_rotation_paths[2], 'eval-images/wholebody/cervical-results/0RB-result.PNG')
right_after_world_landmarks, _ = cv.infer_image(cervical_rotation_paths[3], 'eval-images/wholebody/cervical-results/0RA-result.PNG')
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