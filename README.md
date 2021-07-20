# info_tracker


Simple ROS package that tracks the following info on a robot:

 1. Total distance travelled, either by teleoperation or autonomous driving.
 2. Paths that have been driven through autonomous driving to reach a goal.
 
Both informations are logged to json files located in your current_path/log. 

For distance there's only one file that will record the total distance driven.
For each goal one file will be generated, containing: path taken towards the goal, distance driven, status if goal was reached (status = reached) or not (status = preempted).

## How to run

The packages provided by Neobotix were used for simulation and robot set up:
https://docs.neobotix.de/display/R2/ROS+2-Simulation

Environment description:
- ROS version: ROS 2 Foxy
- Robot: Neobotix MPO-500
- Simulation: Gazebo

All installations were hence done following their tutorials. Same applies to this package, it can be installed and built accordingly to their tutorial.

This package can be launched as the following:

    ros2 run info_tracker tracker

## Example execution

Some output after executing the package and giving a short navigation goal to the robot, and after that navigating with teleoperation for a few more meters:

    {"path": [[-0.6348177706820847, 2.8270511154238758, -0.013000213530152026], [-0.5590902083080409, 2.829581269204776, -0.013725359335736124], [-0.4185774229111341, 2.8273414374946557, -0.013000213437648584], [-0.24381408719214204, 2.8181120097248886, -0.013000213450401445], [-0.11235797147143706, 2.769704564470079, -0.013000213437250958], [-0.021029871295660522, 2.729584866165249, -0.013725516131119686], [0.04809204988484633, 2.7029955153730367, -0.0130002134369907], [0.08794283439734865, 2.6897130553219397, -0.012999999982603209], [0.11743410324508587, 2.6812663113081783, -0.01300021343705178], [0.13742821164194347, 2.6763142961887, -0.013725516132001268], [0.15714268136129367, 2.6722456329439814, -0.013000213437112329], [0.16714739283684435, 2.670515915200851, -0.012999999984382954], [0.17712377095873386, 2.6690725038303706, -0.01372551613208815], [0.17712377095873386, 2.6690725038303706, -0.01372551613208815]], "distance_travelled": 0.8505321065378575, "status": "reached"}

    {"distance_travelled": 3.999623505291731}



