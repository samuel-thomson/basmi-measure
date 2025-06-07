import os

os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import sys

sys.path.append(r'C:\Users\HP\Documents\GitHub\mmpose')
sys.path.append(r'C:\Users\HP\Documents\GitHub\mmpose\projects\rtmpose3d')

from mmpose.utils import register_all_modules
register_all_modules()

import math
import numpy as np
import mmcv

from torch.serialization import add_safe_globals

add_safe_globals([
    np.ndarray,
    np.core.multiarray._reconstruct,
    np.dtype,
    type(np.dtype('float32')),  # Fix for the error you're getting now
    type(np.dtype('uint8')),  # Also needed for other weights
    type(np.dtype('int64')),  # Common fallback
])

from mmpose.apis import inference_topdown, init_model
from mmpose.registry import VISUALIZERS
from mmseg.apis import MMSegInferencer

def euclidean_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2 + (point1[2] - point2[2]) ** 2)


class MMPose():
    def __init__(self):
        self.model_3d = init_model(
            'MMPose/configs/rtmw3d-l_8xb64_cocktail14-384x288.py',
            checkpoint='MMPose/checkpoints/rtmw3d-l_8xb64_cocktail14-384x288-794dbc78_20240626.pth',
            device='cpu'
        )
        self.seg_inferencer = MMSegInferencer(model='fcn_hr48_4xb2-160k_cityscapes-512x1024')

    def infer_image(self, input_path):
        batch_results = inference_topdown(self.model_3d, input_path)
        return batch_results, batch_results[0].pred_instances.keypoints[0]

    def visualise_predictions(self, input_path, batch_results, out_file='output.jpg'):
        image = mmcv.imconvert(mmcv.imread(input_path), 'bgr', 'rgb')

        # Initialize the visualizer
        visualizer = VISUALIZERS.get('Pose3dLocalVisualizer')(
            vis_backends=[dict(type='LocalVisBackend')]
        )
        visualizer.set_dataset_meta(self.model_3d.dataset_meta)

        # Add image to the result
        batch_results[0].set_field(image, 'img')

        # Visualize
        visualizer.add_datasample(
            image = image,
            name='3d_pose',
            data_sample=batch_results[0],
            draw_gt=False,
            draw_bbox=True,
            show=False,
            wait_time=0,
            out_file=out_file
        )

    def initial_calibration(self, predictions, measured_intermalleolar):
        rtmw3d_intermalleolar = euclidean_distance(predictions[16], predictions[17])
        rtmw3d_shin = euclidean_distance(predictions[14], predictions[16])
        ratio = rtmw3d_intermalleolar / measured_intermalleolar
        calibrated_shin = rtmw3d_shin / ratio

        return calibrated_shin

    def shin_calibration(self, rtmw3d_target, rtwm3d_shin, measured_shin):
        calibrated_ratio = rtwm3d_shin / measured_shin
        return rtmw3d_target / calibrated_ratio

    def scale_pose_by_shin(self, predictions, measured_shin):
        """Scales the pose so that the shin (joint 14–16) length matches the measured length."""
        predictions = np.copy(predictions)  # avoid modifying original
        predicted_shin_length = euclidean_distance(predictions[14], predictions[16])
        if predicted_shin_length == 0:
            raise ValueError("Predicted shin length is zero — invalid pose?")
        scale_factor = measured_shin / predicted_shin_length
        return predictions * scale_factor

    #def edge_detection(self, image_path):
    #    results = self.seg_inferencer(image_path, show=True)
    #    print((results['predictions']), results['predictions'][0])

    def tragus_to_wall(self, predictions): #, measured_shin):
        #print(predictions[4], predictions[16])

        #Flattened x-distance of shin
        #rtmw3d_shin_x = predictions[14][0] - predictions[16][0]
        #ratio = rtmw3d_shin_x / measured_shin
        rtmw3d_tragus_x = abs(predictions[4][0] - predictions[16][0])

        return rtmw3d_tragus_x #/ ratio

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
        rtmw3d_shin = euclidean_distance(predictions_left_before[14], predictions_left_before[16])
        left_before_scaled = self.shin_calibration(left_distance_before, rtmw3d_shin, shin_length)

        left_distance_after = lf_after[1] - lh_after[1]
        rtmw3d_shin = euclidean_distance(predictions_left_after[14], predictions_left_after[16])
        left_after_scaled = self.shin_calibration(left_distance_after, rtmw3d_shin, shin_length)

        right_distance_before = rf_before[1] - rh_before[1]
        rtmw3d_shin = euclidean_distance(predictions_right_before[14], predictions_right_before[16])
        right_before_scaled = self.shin_calibration(right_distance_before, rtmw3d_shin, shin_length)

        right_distance_after = rf_after[1] - rh_after[1]
        rtmw3d_shin = euclidean_distance(predictions_right_after[14], predictions_right_after[16])
        right_after_scaled = self.shin_calibration(right_distance_after, rtmw3d_shin, shin_length)

        left = left_before_scaled - left_after_scaled
        right = right_before_scaled - right_after_scaled

        return left, right

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
        rtmw3d_shin_before = euclidean_distance(predictions_before[14], predictions_before[16])
        left_before_scaled = self.shin_calibration(left_distance_before, rtmw3d_shin_before, shin_length)

        left_distance_after = lf_after[1] - lh_after[1]
        rtmw3d_shin_after = euclidean_distance(predictions_after[14], predictions_after[16])
        left_after_scaled = self.shin_calibration(left_distance_after, rtmw3d_shin_after, shin_length)

        right_distance_before = rf_before[1] - rh_before[1]
        right_before_scaled = self.shin_calibration(right_distance_before, rtmw3d_shin_before, shin_length)

        right_distance_after = rf_after[1] - rh_after[1]
        right_after_scaled = self.shin_calibration(right_distance_after, rtmw3d_shin_after, shin_length)

        left = left_before_scaled - left_after_scaled
        right = right_before_scaled - right_after_scaled

        return left, right

    def intermalleolar_distance(self, predictions): #, measured_shin):
        return euclidean_distance(predictions[16], predictions[17])
        #rtmw3d_distance = euclidean_distance(predictions[15], predictions[16])
        #rtmw3d_shin = euclidean_distance(predictions[14], predictions[16])
        #return self.shin_calibration(rtmw3d_distance, rtmw3d_shin, measured_shin)

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
#_, preds = cv.infer_image(ankle_image_path)
#cv.visualise_predictions(image_path, _, 'MMPose/test-images/4D-result.jpg')
#_, raw_preds = cv.infer_image(ankle_image_path)
#measured_shin = cv.initial_calibration(preds, 1.10) #Application solution would ask patients to measure shin
#scaled_preds = cv.scale_pose_by_shin(raw_preds, measured_shin)
#shin_length =
#print(preds[:, 2])
#print(cv.intermalleolar_distance(raw_preds))
#print(cv.intermalleolar_distance(scaled_preds))

#tragus_image_path = 'MMPose/test-images/4A.png'
#_, raw_preds = cv.infer_image(tragus_image_path)
#scaled_preds = cv.scale_pose_by_shin(raw_preds, measured_shin)
#print(cv.tragus_to_wall(raw_preds))
#print(cv.tragus_to_wall(scaled_preds))

#lb_side_path = 'MMPose/test-images/4BLB.png'
#la_side_path = 'MMPose/test-images/4BLA.png'
#rb_side_path = 'MMPose/test-images/4BRB.jpg'
#ra_side_path = 'MMPose/test-images/4BRA.jpg'
#_, lb_raw_preds = cv.infer_image(lb_side_path)
#_, la_raw_preds = cv.infer_image(la_side_path)
#_, rb_raw_preds = cv.infer_image(rb_side_path)
#_, ra_raw_preds = cv.infer_image(ra_side_path)
#print(cv.side_flexion(lb_raw_preds, la_raw_preds, rb_raw_preds, ra_raw_preds, measured_shin))

#before_lumbar_path = 'MMPose/test-images/4CB.png'
#after_lumbar_path = 'MMPose/test-images/4CA.png'
#_, before_raw_preds = cv.infer_image(before_lumbar_path)
#_, after_raw_preds = cv.infer_image(after_lumbar_path)
#print(cv.lumbar_flexion(before_raw_preds, after_raw_preds, measured_shin))

#cervical_left_before_path = "MMPose/test-images/0ELB.jpg"
#cervical_left_after_path = "MMPose/test-images/0ELA.jpg"
#cervical_right_before_path = "MMPose/test-images/0ERB.png"
#cervical_right_after_path = "MMPose/test-images/0ERA.png"
#_, left_before_predictions = cv.infer_image(cervical_left_before_path)
#_, left_after_predictions = cv.infer_image(cervical_left_after_path)
#_, right_before_predictions = cv.infer_image(cervical_right_before_path)
#_, right_after_world_landmarks = cv.infer_image(cervical_right_after_path)
#print(cv.cervical_rotation(left_before_predictions, left_after_predictions, right_before_predictions, right_after_world_landmarks))


#cervical_left_before_path = "MMPose/test-images/4EB.png"
#cervical_left_after_path = "MMPose/test-images/4EL.png"
#cervical_right_before_path = "MMPose/test-images/4EB.png"
#cervical_right_after_path = "MMPose/test-images/4ER.png"
#_, left_before_predictions = cv.infer_image(cervical_left_before_path)
#_, left_after_predictions = cv.infer_image(cervical_left_after_path)
#_, right_before_predictions = cv.infer_image(cervical_right_before_path)
#_, right_after_world_landmarks = cv.infer_image(cervical_right_after_path)
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

##visualise_predictions(self, input_path, batch_results, out_file='output.jpg'):##

measured_intermalleolar = [1.40, 1.23, 1.14, 1.10, 1.24, 1.06, 1.34, 1.50, 1.43, 1.00]
shin_lengths = []
for x in range(10):
    _, raw_preds = cv.infer_image(intermalleolar_distance_paths[x])
    shin_length = cv.initial_calibration(raw_preds, measured_intermalleolar[x])  # Application solution would ask patients to measure shin
    shin_lengths.append(shin_length)

tragus_to_wall_results = []
for x in range(10):
    batch_results, raw_preds = cv.infer_image(tragus_to_wall_paths[x])
    cv.visualise_predictions(tragus_to_wall_paths[x], batch_results, 'eval-images/RTMPose3D/tragus-results/' + str(x + 1) + '.png')
    result = cv.tragus_to_wall(raw_preds)
    tragus_to_wall_results.append(result)

side_flexion_results = []
for x in range(10):
    batch_results, lb_raw_preds = cv.infer_image(side_flexion_paths[x][0])
    cv.visualise_predictions(side_flexion_paths[x][0], batch_results, 'eval-images/RTMPose3D/side-results/' + str(x + 1) + 'LB.png')
    batch_results, la_raw_preds = cv.infer_image(side_flexion_paths[x][1])
    cv.visualise_predictions(side_flexion_paths[x][1], batch_results, 'eval-images/RTMPose3D/side-results/' + str(x + 1) + 'LA.png')
    batch_results, rb_raw_preds = cv.infer_image(side_flexion_paths[x][2])
    cv.visualise_predictions(side_flexion_paths[x][2], batch_results, 'eval-images/RTMPose3D/side-results/' + str(x + 1) + 'RB.png')
    batch_results, ra_raw_preds = cv.infer_image(side_flexion_paths[x][3])
    cv.visualise_predictions(side_flexion_paths[x][3], batch_results, 'eval-images/RTMPose3D/side-results/' + str(x + 1) + 'RA.png')
    result = cv.side_flexion(lb_raw_preds, la_raw_preds, rb_raw_preds, ra_raw_preds, shin_lengths[x])
    side_flexion_results.append(result)

lumbar_flexion_results = []
for x in range(10):
    batch_results, before_raw_preds = cv.infer_image(lumbar_flexion_paths[x][0])
    cv.visualise_predictions(lumbar_flexion_paths[x][0], batch_results, 'eval-images/RTMPose3D/lumbar-results/' + str(x+1) + 'B.png')
    _, after_raw_preds = cv.infer_image(lumbar_flexion_paths[x][1])
    cv.visualise_predictions(lumbar_flexion_paths[x][1], batch_results, 'eval-images/RTMPose3D/lumbar-results/' + str(x + 1) + 'A.png')
    result = cv.lumbar_flexion(before_raw_preds, after_raw_preds, shin_lengths[x])
    lumbar_flexion_results.append(result)


intermalleolar_distance_results = []
for x in range(10):
    batch_results, raw_preds = cv.infer_image(intermalleolar_distance_paths[x])
    scaled_preds = cv.scale_pose_by_shin(raw_preds, shin_lengths[x])
    result = cv.intermalleolar_distance(scaled_preds)
    intermalleolar_distance_results.append(result)
    cv.visualise_predictions(intermalleolar_distance_paths[x], batch_results, 'eval-images/RTMPose3D/intermalleolar-results/' + str(x+1) + '.png')

batch_results, left_before_predictions = cv.infer_image(cervical_rotation_paths[0])
cv.visualise_predictions(cervical_rotation_paths[0], batch_results, 'eval-images/RTMPose3D/cervical-results/0LB-result.PNG')
batch_results, left_after_predictions = cv.infer_image(cervical_rotation_paths[1])
cv.visualise_predictions(cervical_rotation_paths[1], batch_results, 'eval-images/RTMPose3D/cervical-results/0LA-result.PNG')
batch_results, right_before_predictions = cv.infer_image(cervical_rotation_paths[2])
cv.visualise_predictions(cervical_rotation_paths[2], batch_results, 'eval-images/RTMPose3D/cervical-results/0RB-result.PNG')
batch_results, right_after_world_landmarks = cv.infer_image(cervical_rotation_paths[3])
cv.visualise_predictions(cervical_rotation_paths[3], batch_results, 'eval-images/RTMPose3D/cervical-results/0RA-result.PNG')
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