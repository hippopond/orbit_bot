import math                                                                                                    
import rclpy                                                                                                   
from rclpy.node import Node                                                                                    
from geometry_msgs.msg import TransformStamped                                                                 
from tf2_ros import TransformBroadcaster                                                                       
                                                                                                               
class OrbitNode(Node):                                                                                         
    def __init__(self):                                                                                        
        super().__init__('orbit_node')                                                                         
        self.tf_broadcaster = TransformBroadcaster(self)                                                       
        self.timer = self.create_timer(0.1, self.publish_transform)                                            
        self.angle = 0.0                                                                                       
                                                                                                               
    def publish_transform(self):                                                                               
        t = TransformStamped()                                                                                 
                                                                                                               
        t.header.stamp = self.get_clock().now().to_msg()                                                       
        t.header.frame_id = 'odom'                                                                             
        t.child_frame_id = 'base_link'                                                                         
                                                                                                               
        radius = 2.0                                                                                           
        t.transform.translation.x = radius * math.cos(self.angle)                                              
        t.transform.translation.y = radius * math.sin(self.angle)                                              
        t.transform.translation.z = 0.0                                                                        
                                                                                                               
        t.transform.rotation.x = 0.0                                                                           
        t.transform.rotation.y = 0.0                                                                           
                                                                                                               
        t.transform.rotation.z = math.sin((self.angle + (math.pi/2)) / 2.0)
        t.transform.rotation.w = math.cos((self.angle + (math.pi/2)) / 2.0)                                    
                                                                                                               
        self.tf_broadcaster.sendTransform(t)                                                                   
        self.angle += 0.05                                                                                     

def main(args=None):
    rclpy.init(args=args)
    node = OrbitNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
