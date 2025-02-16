import serial
import pynmea2
from geopy.distance import geodesic
from datetime import datetime, date, timedelta

# Global variables to store last location and time
last_location = None
last_time = None

def get_speed(serial_port='/dev/ttyACM0'):
    """
    Opens the specified serial port, reads NMEA data until
    a valid GPGGA sentence is found, computes velocity based
    on the previous reading, and returns (lat, lon, speed_mph).
    """

    global last_location, last_time

    # Open the serial connection
    with serial.Serial(serial_port, timeout=1) as ser:
        while True:
            # Read one line from the GPS
            data = ser.readline()

            # Check if we have a GPGGA sentence
            if data.startswith(b'$GPGGA'):
                try:
                    # Parse NMEA data
                    msg = pynmea2.parse(data.decode('utf-8', errors='ignore'))

                    # Extract current coordinates
                    current_location = (msg.latitude, msg.longitude)
                    gps_time = msg.timestamp
                    current_time = datetime.combine(date.today(), gps_time)

                    # Default to 0 mph if no prior reading
                    velocity_mph = 0.0

                    # If previous location/time exists, compute velocity
                    velocity_mph = 0.0
                    if last_location is not None and last_time is not None:
                        distance_m = geodesic(last_location, current_location).meters
                        time_diff_s = (current_time - last_time).total_seconds()
                        # If time difference is too small (GPS timestamps update only once per second),
                        # skip the calculation to avoid huge speeds.
                        if time_diff_s > 0.5:
                            velocity_mps = distance_m / time_diff_s
                            velocity_mph = velocity_mps * 2.23694
                        else:
                            velocity_mph = 0.0

                    # Update global state
                    last_location = current_location
                    last_time = current_time

                    # Return the current lat, lon, and speed in mph
                    #return (msg.latitude, msg.longitude, velocity_mph)

                    # Return velocity in mph
                    return velocity_mph

                except pynmea2.ParseError:
                    # If parse fails, ignore and read next line
                    continue
