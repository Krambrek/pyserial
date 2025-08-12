from multiprocessing import Pipe, Process
from signal import signal, SIGINT, SIG_IGN
from time import sleep

from serial.tools.list_ports_windows import comports
from serial import Serial
from serial.serialutil import SerialException


def read(name, conn):
    signal(SIGINT, SIG_IGN)
    try:
        port = Serial(name, timeout=0.05)
        print(f'connected to {name}')
        buff = bytes()
        while True:
            buff += port.read_until(size=1)
            if len(buff) == 10:
                conn.send(buff.decode('utf-8').rstrip('\r\n'))
                buff = bytes()
            if conn.poll():
                data = conn.recv()
                if data == 'EXIT':
                    print(f'disconnected from {name}')
                    port.close()
                    break
    except SerialException as e:
        conn.send(str(e))


if __name__ == '__main__':
    readers = []
    for port in comports():
        if port.name in ['COM3', 'COM5']:
            continue
        (conn1, conn2) = Pipe()
        reader = Process(target=read, name=f'{port.name} Reader', args=(port.name, conn2))
        readers.append((port.name, conn1))
        reader.start()

    while True:
        try:
            for name, conn in readers:
                if conn.poll():
                    data = conn.recv()
                    print(f'received {data} from {name}')
            sleep(0.05)
        except KeyboardInterrupt:
            for name, conn in readers:
                conn.send('EXIT')
            break
