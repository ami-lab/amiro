import rospy
from std_msgs.msg import Int32
from amiro_services.srv import IsAvailable, IsAvailableResponse
from amiro_services.msg import Availability

import RPi.GPIO as GPIO
import json


class BlindsNode:
	ROS_NODE_NAME = "rpi_1"

	def __init__(self, topic_name, gpio_up, gpio_down):
		GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD
		rospy.init_node('rpi_1', anonymous=True)
		self.topic_name = topic_name
		self.gpio_up = gpio_up
		self.gpio_down = gpio_down

		GPIO.setup(gpio_up, GPIO.OUT, initial=1)
		GPIO.setup(gpio_down, GPIO.OUT, initial=1)

		# setup availability service
		self.availability_service = None
		self.availability_publisher = None

		self.__setup_availability_services()


	def __setup_availability_services(self):
		availability_service_name = 	BlindsNode.ROS_NODE_NAME + "_is_available"
		availability_topic_name = 	BlindsNode.ROS_NODE_NAME + "_availability"

		# setup the service
		self.availability_service = \
			rospy.Service(availability_service_name, IsAvailable, self.is_available)

		# setup the publisher
		self.availability_publisher = \
			rospy.Publisher(availability_topic_name, Availability, queue_size=10)



	def is_available(self):
		return IsAvailableResponse(True)


	def announce_available(self):
		msg = Availability()
		msg.is_available = True

		if self.availability_publisher:
			self.availability_publisher.publish(msg)


	def listen(self):
		rospy.Subscriber(self.topic_name, Int32, self.on_blinds_msg)


	def on_blinds_msg(self, data):
		rospy.loginfo(rospy.get_caller_id() + "I heard %s", data.data)
		GPIO.output(self.gpio_up, 1);
		GPIO.output(self.gpio_down, 1);

		if data.data == -1:
			GPIO.output(self.gpio_down, 0)
		elif data.data == 1:
			GPIO.output(self.gpio_up, 0)

with open('blinds_config.json') as json_data_file:
	gpio_config = json.load(json_data_file)

for key in gpio_config:
	bnode = BlindsNode(key, gpio_config[key]['up'], gpio_config[key]['down'])
	bnode.announce_available()
	bnode.listen()

rospy.spin()
