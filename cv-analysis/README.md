# CV Design and Analysis

In this project, four framework and model combinations are implemented for the 5 BASMI measurements: MediaPipe Pose (Google, 2023), and MMPose (MMPose Contributors, 2020) with wholebody, human3d, and RTMPose3D (Jiang, Xie and Li, 2024).

This requires MediaPipe, MMPose and mmcv to run. RTMPose3D also requires the respective config and checkpoint files.    

Please note that no images of participants have been included due to ethics, and so the evaluation section of the code will not run, but the code can be run on other images.

Using the most accurate models, a general pose estimator class was then impelemented.



## References

Google (2023) MediaPipe Pose. Available at: https://developers.google.com/mediapipe/solutions/vision/pose (Accessed: 2 May 2025).

Jiang, T., Xie, X. and Li, Y. (2024) RTMW: Real-Time Multi-Person 2D and 3D Whole-body Pose Estimation. arXiv preprint arXiv:2407.08634. Available at: https://arxiv.org/abs/2407.08634 (Accessed: 2 May 2025).

MMPose Contributors (2020) OpenMMLab Pose Estimation Toolbox and Benchmark. Available at: https://github.com/open-mmlab/mmpose (Accessed: 2 May 2025).