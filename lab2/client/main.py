import serial
import time

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1)


def send_and_recv(data):
    for char in data:
        arduino.write(char.encode(encoding='ascii'))
        time.sleep(.1)

    data = ''
    while True:
        response = arduino.readline()
        if response != b'':
            data += response.decode()

        if ';' in data:
            break

    return data.replace('\r\n', '')


def main():
    request = '    Hello;'

    print('Start data: ', request)
    print('Received from HW data: ',  send_and_recv(request))


if __name__ == "__main__":
    main()
