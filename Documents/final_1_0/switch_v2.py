#! /usr/bin/env python

import rospy
from ar_track_alvar_msgs.msg import AlvarMarkers
import time
from right import * as der
from left import * as izq

current_wall = 0
class ar_switch():
    def __init__(self):
        rospy.Subscriber('ar_pose_marker', AlvarMarkers, self.ar_callback, queue_size = 1)
        rospy.Subscriber("ackermann_cmd_mux/output", AckermannDriveStamped,self.ackermann_cmd_input_callback)
        self.cmd_pub = rospy.Publisher('/vesc/ackermann_cmd_mux/input/navigation', AckermannDriveStamped, queue_size = 10)

        self.master = 0

    def ar_callback(self,marker):
        if len(marker.markers) > 0 and marker.markers[0].id != 255:	
            self.master = marker.markers[0].id
            print(self.master)


        if self.master == 19 or self.master == 23:
            der.Follow_Right_Wall.ackermann_cmd_input_callback(AckermannDriveStamped())
        elif self.master == 18 or self.master == 22:
            izq.Follow_Left_Wall.ackermann_cmd_input_callback(AckermannDriveStamped())


if __name__ == "__main__":
    rospy.init_node("ar_switch", anonymous = True)
    rospy.init_node("Follow_Wall_Left", anonymous = True)
    rospy.init_node("Follow_Wall_Right", anonymous = True)
    node = ar_switch()
    node = Follow_Wall_Left()
    node = Follow_Wall_Right()
rospy.spin()