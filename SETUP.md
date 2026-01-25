# RTAB-Map AI Runtime Setup & Usage

## 1. Environment Setup

### Source Environment

Because LibTorch is in a custom location, you must source the environment correctly every time you open a new terminal.

We use a helper script: `env_setup.bash`.

**Contents of `env_setup.bash`:**

```bash
#!/bin/bash
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/media/thippe/SDV/Ubuntu/rtab_ws/libtorch_cxx11/libtorch/lib
source install/setup.bash
```

**Usage:**

```bash
cd /media/thippe/SDV/Ubuntu/rtab_ws
source env_setup.bash
```

### Static Transform

Ensure the static transform between `base_link` and `camera_link` is published:

```bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0.249503 0 base_link camera_link
```

## 2. Running RTAB-Map

Choose one of the following methods to launch RTAB-Map.

### Method A: SuperPoint & SuperGlue

Execute the following command to launch RTAB-Map with AI features enabled.

**Key Parameters:**

- `Vis/FeatureType 11`: Enables SuperPoint (Torch).
- `Vis/CorNNType 6`: Enables SuperGlue (Nearest Neighbor Matcher).
- `SuperPoint/ModelPath`: Path to `superpoint_v1.pt`.
- `PyMatcher/Path`: Path to `rtabmap_superglue.py`.

```bash
ros2 launch rtabmap_launch rtabmap.launch.py \
    rtabmap_args:="--delete_db_on_start \
                   --Vis/FeatureType 11 \
                   --Vis/CorNNType 6 \
                   --SuperPoint/ModelPath /media/thippe/SDV/Ubuntu/rtab_ws/superpoint_v1.pt \
                   --PyMatcher/Path /media/thippe/SDV/Ubuntu/rtab_ws/src/SuperGluePretrainedNetwork/rtabmap_superglue.py \
                   --Vis/MinInliers 12 \
                   --RGBD/OptimizeMaxError 0 \
                   --Mem/NotLinkedNodesKept true \
                   --Mem/IntermediateNodes true \
                   --RGBD/ExportPoses $(pwd)/trajectory_results.txt" \
    database_path:="$(pwd)/rtabmap.db" \
    use_sim_time:=true \
    rgb_topic:=/camera/color/image_raw \
    depth_topic:=/camera/aligned_depth_to_color/image_raw \
    camera_info_topic:=/camera/color/camera_info \
    frame_id:=camera_link \
    approx_sync:=true \
    visual_odometry:=true \
    qos:=1
```

### Method B: GFTT + BRIEF

Often provides more stable keypoints than FAST.

**Key Parameters:**

- `Vis/FeatureType 6`: Good Features To Track (GFTT) + BRIEF.
- `Vis/CorNNType 3`: BruteForce Hamming.

```bash
ros2 launch rtabmap_launch rtabmap.launch.py \
    rtabmap_args:="--delete_db_on_start \
                   --Vis/FeatureType 6 \
                   --Vis/CorNNType 3 \
                   --Vis/MinInliers 12 \
                   --RGBD/OptimizeMaxError 0 \
                   --Rtabmap/DetectionRate 0 \
                   --Mem/NotLinkedNodesKept true \
                   --Mem/IntermediateNodes true \
                   --RGBD/ExportPoses $(pwd)/trajectory_results.txt" \
    database_path:="$(pwd)/rtabmap.db" \
    use_sim_time:=true \
    rgb_topic:=/camera/color/image_raw \
    depth_topic:=/camera/aligned_depth_to_color/image_raw \
    camera_info_topic:=/camera/color/camera_info \
    frame_id:=camera_link \
    approx_sync:=true \
    visual_odometry:=true \
    qos:=1
```

## 3. Play Dataset

Run the bag file to feed data into RTAB-Map.

```bash
ros2 bag play /media/thippe/project\ two\ world\'s\ HD/dataset/BUGGY/buggy_ros2/Buggy1_sb_circles/ --clock -r 0.2
```

## 4. Post-Processing & Analysis

### Database Viewer

To visualize the database after the run:

```bash
export LD_LIBRARY_PATH=/home/thippe/.local/lib/python3.10/site-packages/torch/lib:$LD_LIBRARY_PATH
rtabmap-databaseViewer rtabmap.db
```
