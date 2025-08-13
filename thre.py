from threading import Lock, Thread
from time import sleep

from serial.tools.list_ports_windows import comports
from serial import Serial
from serial.serialutil import SerialException


def read(name, data, lock, exit_):
    try:
        port = Serial(name, timeout=0.05)
        print(f'connected to {name}')
        buff = bytes()
        e = False
        while not e:
            buff += port.read_until(size=1)
            if len(buff) == 10:
                with lock:
                    data.append(buff.decode('utf-8').rstrip('\r\n'))
                buff = bytes()
            with lock:
                if len(exit_) > 0:
                    e = True
        print(f'disconnected from {name}')
        port.close()
    except SerialException as e:
        print(str(e))


if __name__ == '__main__':
    readers = []
    data = []
    exit_ = []
    lock = Lock()

    for port in comports():
        if port.name in ['COM3', 'COM5']:
            continue
        reader = Thread(target=read, name=f'{port.name} Reader', args=(port.name, data, lock, exit_))
        readers.append(reader)
        reader.start()

    while True:
        try:
            with lock:
                if len(data) > 0:
                    print(f'received {data.pop()}')
                sleep(0.05)
        except KeyboardInterrupt:
            with lock:
                exit_.append('EXIT')
                break

    print('waiting for threads...')

    for reader in readers:
        reader.join()
