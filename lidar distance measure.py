import serial
import struct

def read_and_print_serial_data(port, baudrate):
    ser = serial.Serial(port, baudrate, timeout=1)
    
    while True:
        data = ser.read(1024)
        hex_data = data.encode('hex')
        
        start = 0
        while True:
            start = hex_data.find('542c', start)
            if start == -1:
                break
            
            end = start + 94
            if end > len(hex_data):
                break
            
            packet = hex_data[start:end]
#           print("Received packet:", packet)
            
            # Extract and process distance data
            distances = []
            for i in range(6, 42, 3):
                byte1 = packet[i*2:i*2+2]
                byte2 = packet[i*2+2:i*2+4]
                distance_hex = byte2 + byte1
                distance = int(distance_hex, 16)
                distances.append(distance)
            
            # Calculate and print the average distance
            average_distance = sum(distances) / len(distances)
#           print("Distances:", distances)
            print("Average Distance:", average_distance)
            
            start = end

if __name__ == "__main__":
    port = "/dev/ttyACM0"
    baudrate = 921600
    read_and_print_serial_data(port, baudrate)
