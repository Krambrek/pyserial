from queue import Empty, Queue
from threading import Event, Thread

from serial.tools.list_ports_windows import comports
from serial import Serial
from serial.serialutil import SerialException


def read(name, data_queue, exit_event):
    try:
        port = Serial(name, timeout=0.05)
        print(f'connected to {name}')
        buff = bytes()
        while not exit_event.wait(0):
            buff += port.read_until(size=1)
            if len(buff) == 10:
                data_queue.put(buff.decode('utf-8').rstrip('\r\n'), block=True)
                buff = bytes()
        print(f'disconnected from {name}')
        port.close()
    except SerialException as e:
        print(str(e))


if __name__ == '__main__':
    readers = []
    data_queue = Queue()
    exit_event = Event()

    for port in comports():
        if port.name in ['COM3', 'COM5']:
            continue
        reader = Thread(target=read, name=f'{port.name} Reader', args=(port.name, data_queue, exit_event))
        readers.append(reader)
        reader.start()

    try:
        while True:
            try:
                print(f'received {data_queue.get(block=True, timeout=0.05)}')
            except Empty:
                pass
    except KeyboardInterrupt:
        exit_event.set()

    print('waiting for threads...')

    for reader in readers:
        reader.join()
