import csv, os
from datetime import datetime
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped

class TrajectoryLogger(Node):
    def __init__(self):
        super().__init__('trajectory_logger')
        self.declare_parameter('output_dir','results')
        d=str(self.get_parameter('output_dir').value); os.makedirs(d,exist_ok=True)
        self.path=os.path.join(d,datetime.now().strftime('trajectory_%Y%m%d_%H%M%S.csv'))
        self.file=open(self.path,'w',newline=''); self.writer=csv.writer(self.file)
        self.writer.writerow(['time_s','x','y','z'])
        self.create_subscription(PoseStamped,'/vio/pose',self.cb,50)
    def cb(self,msg):
        t=msg.header.stamp.sec+msg.header.stamp.nanosec*1e-9; p=msg.pose.position
        self.writer.writerow([f'{t:.9f}',p.x,p.y,p.z]); self.file.flush()
    def destroy_node(self):
        if not self.file.closed: self.file.close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args); node=TrajectoryLogger()
    try: rclpy.spin(node)
    finally: node.destroy_node(); rclpy.shutdown()
