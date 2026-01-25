# Evaluation Plan: One World Dataset (Buggy1_sb_circles)

## Objective

Evaluate the trajectory accuracy of SLAM systems (RTAB-Map, ORB-SLAM3) on the **Buggy1_sb_circles** dataset. The primary focus is on **RGB-D** methods, with **Monocular** methods as a secondary baseline. LiDAR is explicitly excluded.

## Dataset Details

* **Sequence Name**: `Buggy1_sb_circles`
* **Duration**: ~230 seconds
* **Bag Size**: 28.3 GiB
* **Ground Truth**: `/gnss/odometry/base_link` (NavSat/Odometry)

### Sensor Topics

* **RGB Image**: `/camera/color/image_raw`
* **Depth Image**: `/camera/aligned_depth_to_color/image_raw`
* **IMU**: `/camera/accel/sample`, `/camera/gyro/sample`
* **Camera Info**: `/camera/color/camera_info`, `/camera/aligned_depth_to_color/camera_info`

## Configurations to Test

We will evaluate the following configurations. "ID" refers to RTAB-Map parameters where applicable.

### 1. RGB-D SLAM (Visual + Depth)

Utilizes RGB and Aligned Depth images. This is expected to be the most robust configuration without LiDAR.

| Configuration Name | Feature Extractor | Matcher | Notes |
| :--- | :--- | :--- | :--- |
| **RGB-D (ORB)** | ORB | BruteForce Hamming | Standard baseline. |
| **RGB-D (GFTT+BRIEF)** | GFTT + BRIEF | BruteForce Hamming | Often more stable keypoints. |
| **RGB-D (SuperPoint)** | SuperPoint | SuperGlue / NN | Deep learning based features (`--Vis/FeatureType 11`). |

### 2. RGB-D + VIO (Visual-Inertial + Depth)

Utilizes RGB, Depth, and IMU data.

* *Note: Requires accurate extrinsic calibration between Camera and IMU.*

### 3. Monocular SLAM (RGB Only)

Uses only the RGB image stream. Useful for comparison to see how much Depth aids the system.

| Configuration Name | Feature Extractor | Matcher | Notes |
| :--- | :--- | :--- | :--- |
| **Mono (ORB)** | ORB | BruteForce Hamming | Standard Monocular VSLAM. |

## Results Table

Fill in this table as experiments are conducted.

| Run ID | Configuration | Status | RMSE (m) | Max Error (m) | Loop Closures | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **RGB-D (ORB)** | Pending | - | - | - | |
| 2 | **RGB-D (GFTT+BRIEF)** | Pending | - | - | - | |
| 3 | **RGB-D (SuperPoint)** | Pending | - | - | - | |
| 4 | **RGB-D + VIO** | Pending | - | - | - | |
| 5 | **Mono (ORB)** | Pending | - | - | - | |

## Instructions

1. **Launch RTAB-Map**:

    ```bash
    ros2 launch rtabmap_ros rtabmap.launch.py \
        args:="-d --DeleteDbOnStart \
        --UseSimTime true \
        --RGBD/NeighborLinkRefining true \
        --Reg/Strategy 0" \
        rgb_topic:=/camera/color/image_raw \
        depth_topic:=/camera/aligned_depth_to_color/image_raw \
        camera_info_topic:=/camera/color/camera_info \
        frame_id:=base_link
    ```

2. **Play Bag**:

    ```bash
    ros2 bag play Buggy1_sb_circles.db3 --clock
    ```

3. **Evaluate**:
    Compare the generated trajectory with `/gnss/odometry/base_link` using `evo_ape`.

    ```bash
    evo_ape tum ground_truth.txt estimated_trajectory.txt -va --plot
    ```
