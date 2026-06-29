import math                                                                                                    
import rclpy                                                                                                   
from rclpy.node import Node                                                                                    
from geometry_msgs.msg import TransformStamped, Twist
from nav_msgs.msg import Odometry
from tf2_ros import TransformBroadcaster
                                                                                                               
class OrbitNode(Node): 
    def __init__(self):                                                                                        
        super().__init__('orbit_node')                                                                         
        self.tf_broadcaster = TransformBroadcaster(self)                                                       
                                                                                                               
        # We are keeping track of where the robot is in the world                                              
        self.x = 0.0                                                                                           
        self.y = 0.0                                                                                           
        self.theta = 0.0                                                                                       
        
        # Track velocities for Odometry
        self.vx = 0.0
        self.vtheta = 0.0
        
        # Create the Odometry publisher
        self.odom_pub = self.create_publisher(Odometry, '/odom', 10)
        
        # Track time for dynamic dt
        self.last_time = self.get_clock().now()
                                                                                                               
        # 1. NEW: Subscribe to the keyboard velocity commands                                                  
        self.subscription = self.create_subscription(                                                          
            Twist, 
            '/cmd_vel',                                                                                        
            self.cmd_vel_callback,                                                                             
            10)                                                                                                
                                                                                                               
        # 2. Timer to constantly publish our position to RViz at 10Hz                                          
        self.timer = self.create_timer(0.1, self.publish_transform)                                            
                                                                                                               
    def cmd_vel_callback(self, msg: Twist) -> None:
        # Update current velocities for odometry
        self.vx = msg.linear.x
        self.vtheta = msg.angular.z

    def publish_transform(self):
        # Calculate dynamic dt
        current_time = self.get_clock().now()
        dt = (current_time - self.last_time).nanoseconds / 1e9
        self.last_time = current_time

        # Calculate physics in the timer loop, NOT the callback!
        self.x += (self.vx * math.cos(self.theta)) * dt
        self.y += (self.vx * math.sin(self.theta)) * dt
        self.theta += self.vtheta * dt

        t = TransformStamped()

        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        # Set the Translation (X, Y)
        t.transform.translation.x = self.x
        t.transform.translation.y = self.y
        t.transform.translation.z = 0.0

        # Set the Rotation (Quaternion from Theta)
        t.transform.rotation.x = 0.0
        t.transform.rotation.y = 0.0
        t.transform.rotation.z = math.sin(self.theta / 2.0)
        t.transform.rotation.w = math.cos(self.theta / 2.0)

        self.tf_broadcaster.sendTransform(t)

        # Also publish the Odometry message
        odom = Odometry()
        odom.header.stamp = t.header.stamp
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'
        
        # Set the position
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation = t.transform.rotation
        
        # Set the velocity
        odom.twist.twist.linear.x = self.vx
        odom.twist.twist.angular.z = self.vtheta
        
        self.odom_pub.publish(odom)

def main(args=None):
    rclpy.init(args=args)
    node = OrbitNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
