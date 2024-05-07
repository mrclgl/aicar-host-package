import struct
import time

from smbus2 import SMBus
from enum import Enum

I2C_ADDRESS = 4

class ModeOfOperation(Enum):
    ConfirmSwitch = 0
    Standby = 1
    RC = 2
    AI = 3

class RCController():

    def __init__(self, i2c_bus:int):
        self.bus = SMBus(i2c_bus)

    def get_mode_of_operation(self):
        mode = self.bus.read_byte_data(I2C_ADDRESS, 0b00000000)
        try:
            return ModeOfOperation(mode)
        except ValueError:
            print("RCController returned invalid mode-of-operation:", mode)
            raise

    def get_rc_receiver_input(self):
        data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0b00000001, 4)
        result = {}
        result['throttle'] = struct.unpack("<H", bytes(data[0:2]))[0]
        result['steering'] = struct.unpack("<H", bytes(data[2:4]))[0]
        return result

    def get_motor_fan_info(self):
        data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0b00000010, 9)
        result = {}
        result['fan_speed']                 = data[0]
        result['update_interval_millis']    = struct.unpack("<H", bytes(data[1:3]))[0]
        result['fan_off_temp']              = float(struct.unpack("<h", bytes(data[3:5]))[0])/100
        result['fan_max_temp']              = float(struct.unpack("<h", bytes(data[5:7]))[0])/100
        result['manual_override']           = data[7]
        result['manual_speed']              = data[8]
        return result

    def get_motor_temp(self):
        data = self.bus.read_i2c_block_data(I2C_ADDRESS, 0b00000011, 2)
        return float(struct.unpack("<h", bytes(data))[0])/100

    def request_mode_of_operation(self, mode:ModeOfOperation):
        if mode == ModeOfOperation.ConfirmSwitch:
            print("Warning: Invalid mode to request!", "(" + str(mode) + ")")
            return
        self.bus.write_byte_data(I2C_ADDRESS, 0b10000000, mode.value)

    def set_rc_control_signals(self, throttlePulseMicros, steeringPulseMicros):
        data = []
        data.extend(struct.pack("<H", throttlePulseMicros))
        data.extend(struct.pack("<H", steeringPulseMicros))
        self.bus.write_i2c_block_data(I2C_ADDRESS, 0b10000001, data)

    def set_motor_fan_settings(self, updateIntervalMillis, fanOffTemp, fanMaxTemp, manualOverride, manualSpeed):
        data = []
        data.extend(struct.pack("<H", updateIntervalMillis))
        data.extend(struct.pack("<h", int(fanOffTemp * 100)))
        data.extend(struct.pack("<h", int(fanMaxTemp * 100)))
        data.append(1 if manualOverride else 0)
        data.append(manualSpeed)
        self.bus.write_i2c_block_data(I2C_ADDRESS, 0b10000010, data)

    #Returns True if successfull and False otherwise
    def change_mode_of_operation(self, mode:ModeOfOperation):

        print("RCController: Requesting %s-Mode" % mode.name, end="")
        self.request_mode_of_operation(mode)

        while True:
            time.sleep(0.5)
            print(".", end="", flush=True)
            
            current_mode = self.get_mode_of_operation()

            if current_mode == mode:
                break
            elif current_mode == ModeOfOperation.ConfirmSwitch:
                continue
            else:
                print("\nRCController: Failed to change mode!")
                return False

        print("\nRCController: Mode change successful!")
        return True
