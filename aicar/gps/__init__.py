
import pynmea2
import serial
import io

from threading import Thread

GPS_SPEED_FILTER = 0.5

class GPS():

    def __init__(self):
        self._running = True
        self._speed = 0

        self._thread = Thread(target=self._update)
        self._thread.setDaemon(True)
        self._thread.start()

    def stop(self):
        self._running = False
        self._thread.join()

    def _update(self):
        ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=0.2)
        sio = io.TextIOWrapper(io.BufferedRWPair(ser, ser))

        while self._running:
            try:
                line = sio.readline()
                msg = pynmea2.parse(line)
                if isinstance(msg, pynmea2.types.talker.VTG):
                    if msg.spd_over_grnd_kmph is None:
                        print("GPS has no location fix! GPS Speed: %s" % str(msg.spd_over_grnd_kmph))
                        continue

                    self._speed = self._speed * GPS_SPEED_FILTER + msg.spd_over_grnd_kmph * (1 - GPS_SPEED_FILTER)

            except serial.SerialException as e:
                print('GPS Device error: {}'.format(e))
                break
            except pynmea2.ParseError as e:
                print('GPS Parse error: {}'.format(e))
                continue

    def get_speed(self):
        return self._speed
