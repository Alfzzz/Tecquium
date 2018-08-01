#! /usr/bin/env python

import rospy
#from sensor_msgs.msg import Image
from ar_track_alvar_msgs.msg import AlvarMarkers
import os
import time
import right
import left


class ar_switch():
    def __init__(self):
        rospy.Subscriber('ar_pose_marker', AlvarMarkers, self.callback, queue_size = 1)
        #rospy.Subscriber("/camera/rgb/image_rect_color", Image, self.callback,  queue_size = 1)

    def callback(self,marker):
        if len(marker.markers) > 0:
            if marker.markers[0].id == 1:
         	right.right()

            if marker.markers[0].id == 4:
                left.left()
                   

if __name__ == "__main__":
    rospy.init_node("ar_switch", anonymous = True)
    node =ar_switch()
    rospy.spin()
