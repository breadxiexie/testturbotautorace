import rospy
from std_msgs.msg import String
from geometry_msgs.msg import Twist
import sys
import threading

class VehicleController:
    def __init__(self):
        # 初始化 ROS 节点
        rospy.init_node('vehicle_controller')

        # 创建发布者和订阅者
        self.cmd_vel_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        self.stop_sign_sub = rospy.Subscriber('/stop_sign', String, self.stop_sign_callback)

        # 初始化速度命令
        self.cmd_vel = Twist()
        self.cmd_vel.linear.x = 0.01  # 初始线性速度为 0.01 m/s
        self.cmd_vel.angular.z = 0.0  # 初始角速度为 0 rad/s

        # 初始化停止标志
        self.stop_sign_received = False

    def stop_sign_callback(self, msg):
        """当接收到停止信号时，设置停止标志为 True"""
        if msg.data == "stop":
            self.stop_sign_received = True

    def run(self):
        """控制小车的主循环"""
        rate = rospy.Rate(10)  # 更新频率为 10 Hz
        while not rospy.is_shutdown():
            # 如果接收到停止信号，则停止小车
            if self.stop_sign_received:
                self.cmd_vel.linear.x = 0.0
                self.cmd_vel_pub.publish(self.cmd_vel)
                break

            # 发布当前速度命令
            self.cmd_vel_pub.publish(self.cmd_vel)

            # 等待下一个循环
            rate.sleep()

    def emergency_stop(self):
        """紧急停止小车"""
        self.cmd_vel.linear.x = 0.0
        self.cmd_vel.angular.z = 0.0
        self.cmd_vel_pub.publish(self.cmd_vel)

def listen_for_commands(controller):
    """监听用户的输入命令"""
    while not rospy.is_shutdown():
        command = input("Enter 'cl' to stop the vehicle: ").strip().lower()
        if command == 'cl':
            controller.emergency_stop()
            break

if __name__ == '__main__':
    # 创建控制器实例
    controller = VehicleController()

    # 检查 /cmd_vel 话题是否可用
    cmd_vel_topic_available = rospy.get_published_topics('/cmd_vel')
    if not cmd_vel_topic_available:
        print("The '/cmd_vel' topic is not available.")
        sys.exit(1)

    # 检查 /stop_sign 话题是否可用
    stop_sign_topic_available = rospy.get_published_topics('/stop_sign')
    if not stop_sign_topic_available:
        print("The '/stop_sign' topic is not available.")
        sys.exit(1)

    # 获取用户输入
    command = input("Enter 'run' to start the vehicle: ").strip().lower()

    # 检查用户输入
    if command == 'run':
        # 启动控制器
        threading.Thread(target=controller.run).start()
        threading.Thread(target=listen_for_commands, args=(controller,)).start()
    elif command == 'cl':
        # 立即停止小车
        controller.emergency_stop()
    else:
        print("Invalid command. Please enter 'run' or 'cl'.")

    # 当用户中断程序时，确保小车停止
    rospy.on_shutdown(controller.emergency_stop)
