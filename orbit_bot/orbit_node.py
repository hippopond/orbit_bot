import math                                                                                                    
import rclpy                                                                                                   
from rclpy.node import Node                                                                                    
from geometry_msgs.msg import TransformStamped                                                                 
from tf2_ros import TransformBroadcaster                                                                       
                                                                                                               
class OrbitNode(Node): 
    def __init__(self):                                                                                        
        super().__init__('orbit_node')                                                                         
        self.tf_broadcaster = TransformBroadcaster(self)                                                       
                                                                                                               
        # We are keeping track of where the robot is in the world                                              
        self.x = 0.0                                                                                           
        self.y = 0.0                                                                                           
        self.theta = 0.0                                                                                       
                                                                                                               
        # 1. NEW: Subscribe to the keyboard velocity commands                                                  
        self.subscription = self.create_subscription(                                                          
            Twist,                                                                                             
            '/cmd_vel',                                                                                        
            self.cmd_vel_callback,                                                                             
            10)                                                                                                
                                                                                                               
        # 2. Timer to constantly publish our position to RViz at 10Hz                                          
        self.timer = self.create_timer(0.1, self.publish_transform)                                            
                                                                                                               
    def cmd_vel_callback(self, msg):
        # Update the robot's position based on the keyboard command
        # (Assuming the command is applied for 0.1 seconds)
        dt = 0.1
        
        self.x += (msg.linear.x * math.cos(self.theta)) * dt
        self.y += (msg.linear.x * math.sin(self.theta)) * dt
        
        self.theta += msg.angular.z * dt

    def publish_transform(self):
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
