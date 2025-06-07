# BASMI Home Measurement Application
![alt text](https://github.com/samuel-thomson/basmi-measure/blob/main/Images/BASMI_measurements.png)
BASMI Home Measurement Application to Monitor Ankylosing Spondylitis Progression.

## CV Analysis
This includes all python programs used to explore the possibility of different pose estimation frameworks and models
to automatically calculate the BASMI measurements shown above. Four framework and model combinations are implemented:

* MediaPipe Pose (Google, 2023)
* MMPose (MMPose Contributors, 2020) with wholebody
* MMPose with human3d
* MMPose RTMPose3D (Jiang, Xie and Li, 2024).

These require MediaPipe, MMPose and mmcv to run. RTMPose3D also requires the respective config and checkpoint files.

Please note that no images of participants have been included, and so the evaluation section of the code 
will not run, but the code can be run on other images.

Using the most accurate models, a general pose estimator class was then implemented.

## The Application

The application consists of three pages accessible by tabs: the home, results and manual instructions pages, 
as well as the measuring page which is accessible from the main page.

The backend for this application is a FastAPI, which requires the `basmi-backend` directory and its files to run in 
a separate project. This estimator is lifted from the development performed in _CV Analysis and Design_.

### Expo


This is an [Expo](https://expo.dev) project created with 
[`create-expo-app`](https://www.npmjs.com/package/create-expo-app).

The original Expo README has been included for installation and running instructions.

## Research Project Abstract
Axial Spondyloarthritis is a chronic inflammatory form of arthritis affecting 1 in 200 individuals. The Bath Ankylosing 
Spondylitis Metrology Index, a composite index to measure spinal mobility, helps to ensure patients are monitored and 
treated effectively as the disease progresses. These measurements are currently undertaken by healthcare professionals,
providing administrative burden and leading to infrequent measurements. A home measurement application enables patients 
to monitor themselves regularly, leveraging pose estimation algorithms to power the calculations to combat sacrificing 
the validity of clinical measurements. We present an analysis of computer vision techniques, an application to perform
automatic home measurement, and an evaluation of its accuracy and usability.

## References
Google (2023) MediaPipe Pose. Available at: https://developers.google.com/mediapipe/solutions/vision/pose 
(Accessed: 2 May 2025).

Jiang, T., Xie, X. and Li, Y. (2024) RTMW: Real-Time Multi-Person 2D and 3D Whole-body Pose Estimation. 
arXiv preprint arXiv:2407.08634. Available at: https://arxiv.org/abs/2407.08634 (Accessed: 2 May 2025).

MMPose Contributors (2020) OpenMMLab Pose Estimation Toolbox and Benchmark. Available at: 
https://github.com/open-mmlab/mmpose (Accessed: 2 May 2025).