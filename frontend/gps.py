# This is the code for GPS connection, inspired by Abdullah Jirjees
# https://github.com/AbdullahJirjees/VK-16_GPS/tree/main

# PySerial: manages serial communication between serial port and GPS module
# Pynmea2 library used for NMEA 0183 protocol, commonly used in GPS data.
# Geopy library used for geocoding and geographical data manipulation in the program.

# pip install pyserial pynmea2 geopy

import serial
import pynmea2
from geopy.distance import geodesic
from datetime import datetime
import os

# Velocity limit that sets minimum threshold for accounting for incidents
# PROGRAMMER: update velocity limit at a later time, 0.05 m/s is used during development
# 1 MPH = 0.44704 m/s
velocity_limit = 0.05

def read_gps_data(serial_port='/dev/ttyACM0'):

    # Set serial port name and timeout time
    ser = serial.Serial(serial_port, timeout=1)

    # Ensure reset location and time
    last_location = None
    last_time = None

    # Counter to keep track the number of violations and label them
    violation_count = 0

    while True:
        # Read data and parse data message
        data = ser.readline()
        if data.startswith(b'$GPGGA'):
            msg = pynmea2.parse(data.decode('utf-8'))
            
            # Assign current location and time
            current_location = (msg.latitude, msg.longitude)
            current_time = datetime.now()

            # If location and time exist, calculate velocity
            if last_location is not None and last_time is not None:
                distance = geodesic(last_location, current_location).meters
                time_difference = (current_time - last_time).total_seconds()
                velocity_mps = distance / time_difference if time_difference > 0 else 0.0
                velocity_mph = velocity_mps * 2.23694  # Convert to mph

                print(f"Latitude: {msg.latitude}, Longitude: {msg.longitude}, Velocity: {velocity_mph} mph")
                    
            # Set last location/time as current after most recent calculation
            last_location = current_location
            last_time = current_time

if __name__ == "__main__":
    read_gps_data()
