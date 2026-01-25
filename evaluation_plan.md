
# Evaluation Plan: ORB-SLAM / RTAB-Map on KITTI Sequence 09 (Monocular)

## Objective

Evaluate the trajectory accuracy of the Monocular SLAM system on KITTI Sequence 09 using different combinations of **Feature Extractors** and **Feature Matchers**.

## Dataset

* **Sequence**: 09
* **Sensors**: Monocular Camera (Left Gray: `image_0`)
* **Ground Truth**: `09.txt` (poses)

## Configurations to Test

We will test the following combinations. The "ID" corresponds to the RTAB-Map parameters:

* `Vis/FeatureType` (and `Kp/DetectorStrategy`)
* `Vis/CorNNType` (Nearest Neighbor strategy for matching)

| Configuration Name | Feature Extractor (ID) | Description | Matcher (ID) | Description | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline (ORB)** | `2` | ORB (Oriented FAST and Rotated BRIEF) | `3` | BruteForce Hamming | Standard ORB-SLAM2/3 configuration. Fast and robust. |
| **FAST + BRIEF** | `4` | FAST detector + BRIEF descriptor | `3` | BruteForce Hamming | Very fast, good for high-speed motion, less scale/rotation invariant. |
| **GFTT + BRIEF** | `6` | Good Features To Track + BRIEF | `3` | BruteForce Hamming | Often more stable keypoints than FAST. |
| **BRISK** | `7` | BRISK | `3` | BruteForce Hamming | Scale-invariant binary descriptor. |
| **KAZE** | `9` | KAZE | `1` | FLANN (L2) | Non-linear scale space, very robust but slower. |
| **SuperPoint** | `11` | SuperPoint (Deep Learning) | `3` or `6` | BruteForce or SuperGlue | State-of-the-art learned features. Requires GPU. |
| **SIFT** | `1` | SIFT | `1` | FLANN (L2) | Classic high-accuracy descriptor (Slower). |

## Results Table (Empty)

Fill in this table as you run the experiments.

| Run ID | Configuration | Status (Success/Fail) | Duration (s) | Loop Closures | RMSE (m) | Max Error (m) | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **ORB (Stereo)** |  |  |  |  |  |  |
| 2 | **FAST+BRIEF (Stereo)** |  |  |  |  |  |  |
| 3 | **GFTT+BRIEF (Stereo)** |  |  |  |  |  |  |
| 4 | **SuperPoint + SuperGlue (Stereo)** |  |  |  |  |  |  |

## Parameter Reference

### Feature Types (`Vis/FeatureType` & `Kp/DetectorStrategy`)

* 0=SURF
* 1=SIFT
* 2=ORB
* 3=FAST/FREAK
* 4=FAST/BRIEF
* 5=GFTT/FREAK
* 6=GFTT/BRIEF
* 7=BRISK
* 8=GFTT/ORB
* 9=KAZE
* 10=ORB-OCTREE
* 11=SuperPoint

### Matcher Types (`Vis/CorNNType`)

* 0=FLANN (KDTree) - For float descriptors (SIFT, SURF, KAZE)
* 1=FLANN (LSH) - For binary descriptors (ORB, BRIEF, BRISK)
* 3=BruteForce (Hamming) - For binary descriptors (Recommended for ORB)
* 4=BruteForce (L2) - For float descriptors
* 6=SuperGlue - Specific for SuperPoint

## Instructions

1. Open `run_kitti_benchmark.sh`.
2. Add a new line for each configuration you want to test in the "Run Methods" section.
    * Example: `run_test "gftt_brief" "6" "3" "/kitti/camera_color_left/image_raw"`
3. Run the script: `./run_kitti_benchmark.sh`
4. The results (poses and database) will be saved in `results_seq09`.
5. Use `evo` or `rtabmap-report` to calculate RMSE (if not automatically done).
