from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, PythonExpression
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    rtabmap_launch_dir = FindPackageShare('rtabmap_launch')
    
    # Default bag path from user
    default_bag_path = '/media/thippe/project two world\'s HD/dataset/BUGGY/buggy_ros2/Buggy1_sb_circles/'

    return LaunchDescription([
        # --- Arguments ---
        DeclareLaunchArgument('use_sim_time', default_value='true', description='Use simulation (Gazebo) clock if true'),
        DeclareLaunchArgument('qos', default_value='100', description='General QoS used for sensor input data'),
        DeclareLaunchArgument('rosbag_path', default_value=default_bag_path, description='Path to rosbag file to play'),
        DeclareLaunchArgument('bag_rate', default_value='0.1', description='Playback rate for rosbag'),
        DeclareLaunchArgument('use_bag_odom', default_value='false', description='If true, use /gnss/odometry/base_link from bag. If false, compute ICP odometry.'),
        
        # --- Static Transforms ---
        # User confirmed bag only has camera TFs. We MUST publish the rig TFs.
        
        # 1. base_link -> velodyne
        # Pitch 14.25 degrees ~= 0.2495 radians
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='base_link_to_velodyne',
            arguments=['--x', '0', '--y', '0', '--z', '0', '--yaw', '0', '--pitch', '0.2495', '--roll', '0', '--frame-id', 'base_link', '--child-frame-id', 'velodyne'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),
        
        # 2. velodyne -> camera_color_optical_frame
        # Camera is 20cm above VLP (z=0.1 in previous file? checking previous file it was 0.1).
        # Previous file had: z=0.1, yaw=-1.57..., roll=-1.57...
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            name='velodyne_to_camera',
            arguments=['--x', '0', '--y', '0', '--z', '0.1', '--yaw', '-1.57079632679', '--pitch', '0', '--roll', '-1.57079632679', '--frame-id', 'velodyne', '--child-frame-id', 'camera_color_optical_frame'],
            parameters=[{'use_sim_time': LaunchConfiguration('use_sim_time')}]
        ),

        # --- Point Cloud Filter ---
        # Optional: Filter VLP16 points if needed. keeping it as it might be useful for cleaning up self-hits.
        Node(
            package='rtabmap_bringup',
            executable='velodyne_filter',
            name='velodyne_filter',
            parameters=[{'min_range': 0.25}, {'use_sim_time': LaunchConfiguration('use_sim_time')}],
            remappings=[
                ('points_raw', '/velodyne_points_ray'),
                ('points_filtered', '/velodyne_points')
            ]
        ),

        # --- RTAB-Map Launch ---
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                PathJoinSubstitution([rtabmap_launch_dir, 'launch', 'rtabmap.launch.py'])
            ),
            launch_arguments={
                'rtabmap_args': "--delete_db_on_start --Vis/FeatureType 6 --Vis/CorNNType 3 --Vis/MinInliers 12 --Reg/Strategy 1 --RGBD/NeighborLinkRefining true --Grid/Sensor 2 --Icp/VoxelSize 0.1 --Mem/NotLinkedNodesKept true --Mem/IntermediateNodes true --Icp/RangeMin 0.25 --Grid/RangeMin 0.25",
                'use_sim_time': LaunchConfiguration('use_sim_time'),
                'rgb_topic': '/camera/color/image_raw',
                'depth_topic': '/camera/aligned_depth_to_color/image_raw',
                'camera_info_topic': '/camera/color/camera_info',
                
                'subscribe_scan_cloud': 'true',
                'scan_cloud_topic': '/velodyne_points', # Use filtered topic
                
                'subscribe_scan': 'false', 
                'scan_topic': '/scan_ignore',
                
                # Odometry Configuration
                # If use_bag_odom is true: odom_topic=/gnss/..., visual_odometry=false, icp_odometry=false
                'odom_topic': PythonExpression(['"/gnss/odometry/base_link" if "', LaunchConfiguration('use_bag_odom'), '" == "true" else "/odom"']),
                'visual_odometry': 'false',
                'icp_odometry': PythonExpression(['"false" if "', LaunchConfiguration('use_bag_odom'), '" == "true" else "true"']),
                'vo_frame_id': 'odom',
                
                'frame_id': 'base_link',
                'approx_sync': 'true',
                'wait_for_transform': '3.0', # Large tolerance for bag playback
                'qos': LaunchConfiguration('qos'),
                'queue_size': '50',
                'sync_queue_size': '50',
                'topic_queue_size': '50',
                'odom_always_process_most_recent_frame': 'false', 
            }.items()
        ),

        # --- Rosbag Playback ---
        ExecuteProcess(
            condition=IfCondition(
                PythonExpression(['"', LaunchConfiguration('rosbag_path'), '" != ""'])
            ),
            # Remap the raw points to _ray so our filter can pick them up and republish as /velodyne_points
            # STRICT TOPIC ALLOWLIST as requested by user. Includes TF/Static for system health.
            cmd=['ros2', 'bag', 'play', LaunchConfiguration('rosbag_path'), 
                 '--clock', '--rate', LaunchConfiguration('bag_rate'), 
                 '--remap', '/velodyne_points:=/velodyne_points_ray',
                 '--topics',
                 '/velodyne_points',
                 '/camera/accel/sample',
                 '/camera/aligned_depth_to_color/camera_info',
                 '/camera/aligned_depth_to_color/image_raw',
                 '/camera/color/camera_info',
                 '/camera/color/image_raw',
                 '/camera/depth/camera_info',
                 '/camera/depth/color/points',
                 '/camera/depth/image_rect_raw'],
                 # EXCLUDED: '/tf', '/tf_static' (Using generated static TFs and ICP odom to prevent time jumps from bag TFs)
            output='screen'
        )
    ])
