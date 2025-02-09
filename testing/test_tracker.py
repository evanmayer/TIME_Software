import socket, struct, subprocess, os, sys
import time
import numpy as np
import multiprocessing as mp

def start_tracker():
    PORT = 4444
    l = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    l.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    l.bind(('',PORT))
    print('Server Listening')
    l.listen(5)

    PORT = 1806
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('',6666))
    s.connect(('192.168.1.252',PORT))
    print('Socket 1 Connected')
    s.send('TIME_START_TELEMETRY 2'.encode())
    reply = s.recv(1024).decode("ascii")
    print(reply)

    client, info = l.accept()
    print('Socket 2 Connected')
    unpacker = struct.Struct('i i i i d d d d d d d d d d d d d d d d Q Q') # d = float , s = char string , i = integer
    n = 0

    while True :

        try :
            data = client.recv(unpacker.size)
            if len(data) !=0 :
                # unpacking data packet ===============================================
                blanking, direction, observing, pad, utc, lst, deltaT, cur_ra, cur_dec,\
                map_ra, map_dec, ra_off, dec_off, az, el, azvelcmd, elvelcmd, azvelact,\
                elvelact, pa, unix_val, unix_delta = unpacker.unpack(data)
                # ==================================================================
                print('val: %s , delta: %s' %(unix_val,unix_delta))

                # if n == 20 :
                #     break

                n += 1

        except KeyboardInterrupt :
            s.send('TIME_START_TELEMETRY 0'.encode())
            s.shutdown(1)
            l.shutdown(1)
            s.close()
            l.close()
            break

    sys.exit()

def fake_gui_socket():
    PORT = 8500
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('',PORT))
    print('Fake GUI Listening')
    s.listen(5)
    client, info = s.accept()
    print('Fake GUI Socket Connected')
    unpacker = struct.Struct('d i d d')

    while True :
        try:
            data = client.recv(unpacker.size)
            if len(data) !=0 :
                pa, flag, time, enc_pos = unpacker.unpack(data)
                print('kms data :', time, pa)
        except KeyboardInterrupt:
            s.shutdown(1)
            s.close()

if __name__ == '__main__' :
    t2 = mp.Process(target=fake_gui_socket)
    t2.start()
    t1 = mp.Process(target=start_tracker)
    t1.start()
