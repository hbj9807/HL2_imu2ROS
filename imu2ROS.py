from pynput import keyboard
import rospy
from sensor_msgs.msg import Imu
import hl2ss
import hl2ss_lnm

# ROS node initialization
rospy.init_node('HL2_imu_publisher')

# ROS publisher for IMU data
imu_pub = rospy.Publisher('/HL2/imu', Imu, queue_size=10)

# HoloLens settings
host = "192.168.1.161"
port = hl2ss.StreamPort.RM_IMU_ACCELEROMETER
mode = hl2ss.StreamMode.MODE_1

# Exit flag
enable = True

# Keyboard listener callback
def on_press(key):
    global enable
    enable = key != keyboard.Key.esc
    return enable

# Start keyboard listener
listener = keyboard.Listener(on_press=on_press)
listener.start()

# HoloLens client setup
client = hl2ss_lnm.rx_rm_imu(host, port, mode=mode)
client.open()

# Function to publish IMU data as ROS messages
def publish_imu(sample):
    imu_msg = Imu()
    imu_msg.header.stamp = rospy.Time.now()
    imu_msg.header.frame_id = "HL2_imu"  # Frame ID for IMU data
    imu_msg.linear_acceleration.x = sample.x
    imu_msg.linear_acceleration.y = sample.y
    imu_msg.linear_acceleration.z = sample.z
    # Fill orientation and angular velocity if available
    imu_pub.publish(imu_msg)

# Main loop
while not rospy.is_shutdown() and enable:
    data = client.get_next_packet()
    imu_data = hl2ss.unpack_rm_imu(data.payload)
    count = imu_data.get_count()
    sample = imu_data.get_frame(0)

    # Publish IMU data
    publish_imu(sample)

    # Print for debugging
    print(f'Got {count} samples at time {data.timestamp}')
    print(f'First sample: sensor_ticks={sample.vinyl_hup_ticks} soc_ticks={sample.soc_ticks} x={sample.x} y={sample.y} z={sample.z} temperature={sample.temperature}')

# Close HoloLens client and listener
client.close()
listener.join()
