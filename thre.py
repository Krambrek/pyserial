from threading import Lock, Thread
from time import sleep

from serial.tools.list_ports_windows import comports
from serial import Serial
from serial.serialutil import SerialException


class ThreadSafeList():
    def __init__(self, data):
        self._lock = Lock()
        self._list = list(data)

    def __len__(self):
        with self._lock:
            return len(self._list)

    def append(self, item):
        with self._lock:
            self._list.append(item)

    def pop(self):
        with self._lock:
            return self._list.pop()


def read(name, data, exit_):
    try:
        port = Serial(name, timeout=0.05)
        print(f'connected to {name}')
        buff = bytes()
        while not exit_:
            buff += port.read_until(size=1)
            if len(buff) == 10:
                data.append(buff.decode('utf-8').rstrip('\r\n'))
                buff = bytes()
        print(f'disconnected from {name}')
        port.close()
    except SerialException as e:
        print(str(e))


if __name__ == '__main__':
    readers = []
    data = ThreadSafeList([])
    exit_ = ThreadSafeList([])

    for port in comports():
        if port.name in ['COM3', 'COM5']:
            continue
        reader = Thread(target=read, name=f'{port.name} Reader', args=(port.name, data, exit_))
        readers.append(reader)
        reader.start()

    try:
        while True:
            if len(data):
                print(f'received {data.pop()}')
            sleep(0.05)
    except KeyboardInterrupt:
        exit_.append('EXIT')

    print('waiting for threads...')

    for reader in readers:
        reader.join()
