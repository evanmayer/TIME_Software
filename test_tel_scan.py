
import socket, struct, subprocess, os, sys
# from socket import htonl
import time
import numpy as np
import multiprocessing as mp
import tom_tel

class TIME_TELE :

    def __init__(self):
        self.tel_exit = mp.Event()

        PORT = 1806
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.bind(('',6666))
        s1.connect(('192.168.1.252',PORT))
        print('Socket Connected')

        # =============================================================================================================================
        cmnd_list = ['TIME_START_TELEMETRY on','TIME_START_TRACKING off','TIME_SCAN_TIME 6.0','TIME_MAP_SIZE 1.0','TIME_MAP_ANGLE 0.0',\
                        'TIME_MAP_COORD RA','SEEK 05:32:47.0 -5:24:21.0 B1950.0 OrionA ']
        for i in range(len(cmnd_list)):
            s1.send(cmnd_list[i].encode('utf-8'))
            reply = s1.recv(1024).decode("ascii")
            print(reply)
            if i == 0 :
                if 'OK' in reply:
                    p = mp.Process(target=tom_tel.start_sock_tracker)
                    p.start()
                else :
                    print('ERROR reply')
            while True :
                if 'OK' in reply : # wait for ack from tel
                    message = 'TELESCOPE INITIALIZED, STATUS: READY'
        # ==============================================================================================================================
        time.sleep(10.0)
        s1.send('time_start_telemetry off')
        print('telemetry off')
        data2 = s1.recv(1024).decode("ascii")
        print(data2)


if __name__ == '__main__':
    TIME_TELE() #sec,map_size,map_angle,coord,epoch,object
