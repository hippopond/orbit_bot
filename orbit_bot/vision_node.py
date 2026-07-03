import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class VisionNode(Node):
    def __init__(self):
        super().__init__('vision_node')
        # 1. Subscribe to the raw video feed
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.image_callback,
            10)
        # 2. Create a publisher for our new, drawn-on video feed
        self.publisher = self.create_publisher(Image, '/camera/image_annotated', 10)
        self.bridge = CvBridge()
        self.get_logger().info("Vision Node initialized! Hunting for the red RoboCup ball...")

    def image_callback(self, msg):
        try:
            # Convert ROS Image message to OpenCV format
            cv_image = self.bridge.imgmsg_to_cv2(msg, "bgr8")
        except Exception as e:
            self.get_logger().error(f"Failed to convert image: {e}")
            return
        
        # Convert BGR to HSV for better color isolation
        hsv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2HSV)
        
        # Define math boundaries for the color RED in HSV space
        lower_red1 = np.array([0, 100, 100])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 100, 100])
        upper_red2 = np.array([180, 255, 255])
        
        # Create a Black & White mask where the White pixels are Red in real life
        mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
        mask = mask1 + mask2
        
        # Find contours (outlines) of all red blobs
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the absolute largest red object (ignoring background noise)
            largest_contour = max(contours, key=cv2.contourArea)
            
            if cv2.contourArea(largest_contour) > 500:
                # Draw a green bounding box around it
                x, y, w, h = cv2.boundingRect(largest_contour)
                cv2.rectangle(cv_image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # Mark the center coordinate
                center_x = x + w // 2
                center_y = y + h // 2
                cv2.circle(cv_image, (center_x, center_y), 5, (255, 0, 0), -1)
                
                # Log that we saw it!
                # self.get_logger().info(f"Red ball detected at ({center_x}, {center_y})")
        
        # Convert OpenCV image back to a ROS message and publish it!
        try:
            annotated_msg = self.bridge.cv2_to_imgmsg(cv_image, "bgr8")
            self.publisher.publish(annotated_msg)
        except Exception as e:
            self.get_logger().error(f"Failed to publish annotated image: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = VisionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
