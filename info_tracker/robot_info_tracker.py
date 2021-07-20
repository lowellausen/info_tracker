import rclpy, math, json
from datetime import datetime
from rclpy.node import Node
from nav_msgs.msg import Odometry
from std_msgs.msg import String
from action_msgs.msg import GoalStatusArray

global IDLE
IDLE = 0
global MOVING_TO_GOAL
MOVING_TO_GOAL = 2
global REACHED_GOAL
REACHED_GOAL = 4
global PREEMPTED
PREEMPTED = 6

global TIMER_PERIOD
TIMER_PERIOD = 0.5

# class to treat te points received from odometry
class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
     return "x : {:.2f}    y: {:.2f}    z: {:.2f}".format(self.x, self.y, self.z)

    def as_list(self):
        return [self.x, self.y, self.z]

    def update(self, new_value):
        self.x = new_value.x
        self.y = new_value.y
        self.z = new_value.z

    def distance_to(self, point_b):
        return math.sqrt((self.x - point_b.x)**2 + (self.y - point_b.y)**2 + (self.z - point_b.z)**2)

# class that holds all the logic of the package
class RobotMovementTracker(Node):

    def __init__(self):
        super().__init__('robot_movement_tracker')

        self.get_logger().info("Starting subscribers")

        # this one will receive movement info
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10)

        # and this one will receive goal info
        self.subscription = self.create_subscription(
            GoalStatusArray,
            '/follow_path/_action/status',
            self.goal_callback,
            10)

        # and this one will log path info
        self.timer = self.create_timer(TIMER_PERIOD, self.path_callback)

        self.subscription  # prevent unused variable warning

        self.current_position = Point(0.0, 0.0, 0.0)  #not true, workaround with a flag
        self.first_message = True
        self.total_distance_travelled = 0.0

        self.status = IDLE
        self.goal_index = 0
        self.goal_start_distance_travelled = 0
        self.path_list = []  # list of places visited by the robot! don't want to keep this in memory...also don't want to explode on IO operations

        # used to create files with same name for each run
        self.date_string = self.date_string_file()

    # callbak to receive the data sent by odometry, to keep track of position and distance travelled
    def odom_callback(self, msg):
        new_position = Point(msg.pose.pose.position.x,
                             msg.pose.pose.position.y,
                             msg.pose.pose.position.z)

        #workaround to get first position
        if self.first_message:
            self.first_message = False
            self.current_position.update(new_position)

        distance_travelled = self.current_position.distance_to(new_position)
        if distance_travelled > 0.01: # random precision to check it robot is just chillin, values keep oscilating when idle
            self.current_position.update(new_position)
            self.total_distance_travelled += distance_travelled

            json_dict = {"distance_travelled" : self.total_distance_travelled}
            with open("robot_distance_travelled_{}.json".format(self.date_string), "w") as json_file:
                json.dump(json_dict, json_file)

            self.get_logger().info("Sent new distance_travelled to file {}".format(self.total_distance_travelled))

    # callbak to receive updates about robot's goal
    def goal_callback(self, msg):
        status = self.get_status_from_msg(msg)

        if status == REACHED_GOAL:
            self.status = IDLE
            goal_distance_travelled = self.total_distance_travelled - self.goal_start_distance_travelled
            json_dict = {"path" : self.path_list, "distance_travelled" : goal_distance_travelled, "status" : "reached"}
            with open("robot_goal_{}_{}.json".format(self.goal_index, self.date_string),  "w") as json_file:
                json.dump(json_dict, json_file)
            self.path_list.clear()
            self.get_logger().info("Goal reached!")
        elif status == PREEMPTED:
            self.status = IDLE
            goal_distance_travelled = self.total_distance_travelled - self.goal_start_distance_travelled
            json_dict = {"path" : self.path_list, "distance_travelled" : goal_distance_travelled, "status" : "preempted"}
            with open("robot_goal_{}_{}.json".format(self.goal_index, self.date_string),  "w") as json_file:
                json.dump(json_dict, json_file)
            self.path_list.clear()
            self.get_logger().info("Goal preempted")
        elif self.status == IDLE:   # our previous status was idle and now should be moving
            self.status = MOVING_TO_GOAL
            self.goal_start_distance_travelled = self.total_distance_travelled
            self.goal_index += 1
            self.get_logger().info("Following new goal")

    #timer to record robot's path
    def path_callback(self):
        if self.status != MOVING_TO_GOAL:
            return

        self.get_logger().info("Recording position to path")
        self.path_list.append(self.current_position.as_list())

    @staticmethod
    def get_status_from_msg(msg):
        return msg.status_list[-1].status

    @staticmethod
    def date_string_log():
        return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    @staticmethod
    def date_string_file():
        return datetime.now().strftime("%Y-%m-%d_%H%M%S")


def main(args=None):
    rclpy.init(args=args)

    robot_goal_tracker = RobotMovementTracker()

    rclpy.spin(robot_goal_tracker)

    robot_goal_tracker.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
