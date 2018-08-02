#! /usr/bin/env python

import rospy
#from sensor_msgs.msg import Image
from sensor_msgs.msg import LaserScan
from ar_track_alvar_msgs.msg import AlvarMarkers
import os
import time
from ackermann_msgs.msg import AckermannDriveStamped
import numpy as np


class ar_switch():
    def __init__(self):
        #::::::::::::::::::::::::::::::::::::: SUBSCRIBERS :::::::::::::::::::::::::::::::::
        rospy.Subscriber("ackermann_cmd_mux/output", AckermannDriveStamped,self.ackermann_cmd_input_callback)
        rospy.Subscriber('ar_pose_marker', AlvarMarkers, self.callback, queue_size = 1)
        #rospy.Subscriber("/camera/rgb/image_rect_color", Image, self.callback,  queue_size = 1)
 
        #::::::::::::::::::::::::::::::::::::: PUBLISHERS ::::::::::::::::::::::::::::::::::
        self.cmd_pub = rospy.Publisher('/ackermann_cmd_mux/input/default', AckermannDriveStamped, queue_size = 10)
        self.maxSpeed = 1
        self.velCoeff = 1
        self.futCon = 0

        self.prev_error = 0

        self.averageL = 0
        self.futureL = 0

        self.wall = 0

        self.averageR = 0
        self.futureR = 0
        self.idealDis = 0.5 # En el caso de L or R

        self.output = 0
        self.current_time = time.time() #No estpy seguro pero nos puede ayudar en un futuro
        self.prev_time = 0

    def callback(self,marker):
        if (len(marker.markers) > 0) and:
            if marker.markers.id != None:
                print(marker.markers[0].id)
                if marker.markers[0].id == 1:
                    rospy.Subscriber("/scan", left_callback, self.laser_callback)
                elif marker.markers[0].id == 4:
                    rospy.Subscriber("/scan", right_callback, self.laser_callback)
                else:
                    pass
                    
    def left_callback(self,msg):
        
        ranges = msg.ranges

        #Right average
        self.futureL = np.mean(ranges[600: 740])
        print("future L = {}".format(self.futureL)) ####
        self.averageL = np.mean(ranges[740 : 900])
        print("average L = {}".format(self.averageL))
        #Front average
        self.wall = np.mean(ranges[480 : 600])

        self.left_PID(1.0, 1.2, 0.0, 0.4, 'Left')
        
    def right_callback(self,msg):
        
        ranges = msg.ranges

        #Right average
        self.averageR = np.mean(ranges[180 : 340])
        print("future R = {}".format(self.futureR))
        self.futureR = np.mean(ranges[340 : 480])
        print("average R = {}".format(self.averageR))
        #Front average
        self.wall = np.mean(ranges[480 : 600])

        self.right_PID(1.0, 1.2, 0.0, 0.4, 'Right')
        
    def right_PID(self, maxSpeed, kp, ki, kd, mode):
        print("ENTRANDO A PID")

        if  mode == 'Right':
            error = self.averageR - self.idealDis
            dir = -1 
            if self.futureR >= (2 * self.averageR):
                self.futCon = - 0.1
            elif self.futureR <= self.averageR:
                self.futCon = 0.1
            else:
                self.futCon = 0

        self.maxSpeed = maxSpeed
        self.current_time = time.time()

        #P
        prop = kp * error

        #I
        integ = ki * ((error + self.prev_error) * (self.current_time - self.prev_time))

        #D
        deriv = kd * ((error - self.prev_error) / (self.current_time - self.prev_time))

        self.prev_error = error
        self.prev_time = self.current_time

        if self.futureR >= (2 * self.averageR):
            self.futCon = - 0.1

        elif self.futureR <= self.averageR:
            self.futCon = 0.1

        self.output = (prop + integ + deriv + self.futCon) * dir

        if abs(self.output) >= 0.34:
            self.velCoeff = 0.7

        elif abs(self.output) >= 0.25:
            self.velCoeff = 0.9

        else:
            self.velCoeff = 1

        #print("P = {} I = {} D = {}".format(round(prop, 4), round(integ, 4), round(deriv, 4)))
        #print("Angle = {}".format(self.output))

        #print("SALIENDO DE PID")
        print("right")
        self.ackermann_cmd_input_callback(AckermannDriveStamped())
    def left_PID(self, maxSpeed, kp, ki, kd, mode):

        print("ENTRANDO A PID")
        if mode == 'Left':
            dir = 1
            error = self.averageL - self.idealDis
            print(error)
            if self.futureL >= (2 * self.averageL):
                self.futCon = - 0.1
            elif self.futureL <= self.averageL:
                self.futCon = 0.1
            else:
                self.futCon = 0

        self.maxSpeed = maxSpeed
        self.current_time = time.time()

        #P
        prop = kp * error

        #I
        integ = ki * ((error + self.prev_error) * (self.current_time - self.prev_time))

        #D
        deriv = kd * ((error - self.prev_error) / (self.current_time - self.prev_time))

        self.prev_error = error
        self.prev_time = self.current_time

        if self.futureR >= (2 * self.averageR):
            self.futCon = - 0.1

        elif self.futureR <= self.averageR:
            self.futCon = 0.1

        self.output = (prop + integ + deriv + self.futCon) * dir

        if abs(self.output) >= 0.34:
            self.velCoeff = 0.7

        elif abs(self.output) >= 0.25:
            self.velCoeff = 0.9

        else:
            self.velCoeff = 1

        #print("P = {} I = {} D = {}".format(round(prop, 4), round(integ, 4), round(deriv, 4)))
        #print("Angle = {}".format(self.output))
        
        #print("SALIENDO PID")
        print("left")
        self.ackermann_cmd_input_callback(AckermannDriveStamped())    
        
    def ackermann_cmd_input_callback(self, msg):
        msg.drive.speed = self.maxSpeed * self.velCoeff
        msg.drive.steering_angle = self.output
        msg.drive.steering_angle_velocity = 1
        self.cmd_pub.publish(msg)
        
if __name__ == "__main__":
    rospy.init_node("ar_switch", anonymous = True)
    node =ar_switch()
rospy.spin()