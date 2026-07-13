from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
import os

def generate_launch_description():

    bag_path = LaunchConfiguration('bag_path')

    bag_play = ExecuteProcess(
        cmd=[
            'gnome-terminal', '--', 
            'ros2', 'bag', 'play', bag_path, '--rate', '0.00001'
        ],
        output='screen',
        condition=IfCondition(bag_path)
    )
    launch_file_dir = os.path.dirname(os.path.abspath(__file__))
    rviz_config_file = os.path.join(launch_file_dir, 'default.rviz')


    return LaunchDescription([

        DeclareLaunchArgument(
            'bag_path',
            default_value='',
            description='Full path to the .db3 file to play with ros2 bag. If not provided, the launch will wait for external IMU and LiDAR data to arrive on the corresponding topics.'
        ),
        DeclareLaunchArgument(
            'rviz_config_file',
            default_value=rviz_config_file,
            description='Full path to the RViz config file.'
        ),

        # Iniciar RViz con el archivo de configuración
        ExecuteProcess(
            cmd=['ros2', 'run', 'rviz2', 'rviz2', '-d', LaunchConfiguration('rviz_config_file')],
            output='screen'
        ),

        # Node(
        #     package='tf2_ros',
        #     executable='static_transform_publisher',
        #     name='map_2_odom',
        #     # x y z qx qy qz qw  parent child
        #     arguments=['0.0', '0.0', '-0.15',
        #             '0.0', '0.0', '0.0', '1.0',
        #             'map', 'odom'],
        #     output='screen'
        # ),

        # DLO3D Node
        Node(
            package='dlio',
            executable='dlo3d_node',
            name='dlo3d_node',
            output='screen',
            remappings=[
                ('/dll3d_node/initial_pose', '/initialpose')
            ],
            parameters=[
                {'use_sim_time': True},
                {'in_cloud_aux': '/back_lidar'},              # Aux LiDAR Topic if avaliable. If "aux_lidar_en = False" this topic will be ignored.
                {'in_cloud': '/front_lidar'},  # Principal LiDAR Topic.
                {'hz_cloud': 10.0},                     # Principal LiDAR Hz.
                {'in_imu': '/imu'},       # IMU Topic.
                {'hz_imu': 100.0},                      # IMU Hz
                {'calibration_time': 1.0},              # Only if the vehicle stay still before moving
                {'aux_lidar_en': False},                # If only one LiDAR avaliable make sure to set this parameter to False
                {'gyr_dev':  0.00117396706572},         # IMU dev and rw
                {'gyr_rw_dev': 2.66e-07},
                {'acc_dev': 0.0115432018302},
                {'acc_rw_dev': 0.0000333},
                {'base_frame_id': 'base_link'},         # Sensor Frames
                {'odom_frame_id': 'odom'},                   # 里程计中间帧: 发布 map->odom(标准 SLAM TF 树)
                {'map_frame_id': 'map'},
                {'keyframe_dist': 0.25},                 # KeyFrame Tresholds
                {'keyframe_rot': 25.0},
                {'tdfGridSizeX_low': -10.0},            # Grid Size Limits
                {'tdfGridSizeX_high': 70.0},
                {'tdfGridSizeY_low': -30.0},
                {'tdfGridSizeY_high': 30.0},
                {'tdfGridSizeZ_low': -5.0},
                {'tdfGridSizeZ_high': 30.0},
                {'solver_max_iter': 500},               
                {'solver_max_threads': 20},
                {'min_range': 1.0},
                {'max_range': 100.0},
                {'pc_downsampling': 1},
                {'robust_kernel_scale': 1.0},
                {'kGridMarginFactor': 0.8},
                {'maxload': 100.0},
                {'maxCells': 100000}
            ]
        ),

        # bag_play
    ])
