import numpy as np
from os import stat
import os, sys, mce_data_jon, subprocess
import netcdf_files as nc
import datetime as dt
from termcolor import colored
import time
from multiprocessing import Pipe
import multiprocessing as mp
import utils as ut
import init
h_shape = 0
p = 0

def netcdfdata(queue1,flags):
    # os.nice(-20)
    dir = init.mce0_dir
    a = 0
    print('starting mce0 read')
    while not ut.mce_exit.is_set():
        mce_file_len = len(os.listdir(dir))
        mce_file_name = dir + 'temp.%0.3i' %(a)
        mce_file = os.path.exists(dir + 'temp.%0.3i' %(a+1))
        mce_run = os.path.exists(dir + 'temp.run')
        if mce_file and mce_run:
            head,h,frame_num,mce_on = readdata(mce_file_name,flags)
            queue1.send([h,head,frame_num,mce_on])
            a += 1
            subprocess.Popen(['rm %s' %(mce_file_name)], shell = True)

        else :
            time.sleep(0.01)

    # print(colored('No More Files','red'))
    sys.exit()

# ===========================================================================================================================
def readdata(file,flags):
    global h_shape
    global p
    f = mce_data_jon.MCEFile(file)
    l = f.Read(row_col=True, unfilter='DC', all_headers=True)
    h = l.data

    # -------CHECK FOR FRAME SIZE CHANGE----------------------------------------
    # if frame size is wrong, just append zeros instead of partial array to prevent netcdf error
    # also gives a frame size error flag
    if p == 0 :
        h_shape = h.shape
        with flags.get_lock() :
            flags[3] = 0

    else :
        if (h.shape != h_shape):
            # print(colored('WARNING! MCE0 Frame Size Has Changed','red'))
            sys.stdout.flush()
            with flags.get_lock():
                flags[3] = 11
            h = np.zeros((h_shape[0],h_shape[1],h_shape[2]))

        else :
            with flags.get_lock():
                flags[3] = 0
    # -------------------------------------------------------------------------
    # check for row/col that are off or reporting zeros
    mce_on = np.empty([33,32],dtype=int)
    for i in range(h_shape[0]):
        for j in range(h_shape[1]):
            if np.sum(h[i][j][:]) == 0.0 :
                mce_on[i][j] = 0
            else :
                mce_on[i][j] = 1

    # send data to header to be parsed and append data
    head, frame_num = read_header(l)
    p += 1

    return head, h, frame_num, mce_on, l

# ===========================================================================
def read_header(l):
    keys = []
    values = []
    frame_num = []
    print('hello world')
    for i in range(len(l.headers)):
        for key,value in l.headers[i].items():
            print(key)
            if key == '_rc_present':
                for i in range(len(value)):
                    if value[i] == True:
                        value[i] = '1'
                    elif value[i] == False:
                        value[i] = '0'
                    else:
                        print("I don't know what I am...")
                value = ''.join(map(str,value))
            if key == 'sync_box_num' :
                frame_num.append(value)
                print('sync num', value)
            if key == 'frame_counter':
                print('frame num',value)
            value = int(value)
            values.append(value)
    values = np.asarray(values)
    sys.stdout.flush()
    return values, frame_num
