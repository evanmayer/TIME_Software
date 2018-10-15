import os
import subprocess
import time
import shutil
import sys
import datetime as dt

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1) # line buffering

def main():
    a = 0
    dir = '/data/cryo/current_data/'
    print '----- Starting MCE0 Data Transfer -----'
    begin = dt.datetime.utcnow()
    end = dt.datetime.utcnow()
    while end - begin < dt.timedelta(seconds = 5):
        if os.path.exists("/data/cryo/current_data/temp.%0.3i" %(a+1)) : #wait to read new file until old file is complete
            mce_file_name = '/data/cryo/current_data/temp.%0.3i' % (a)
            if a == 0:
                subprocess.Popen(['scp', '/data/cryo/current_data/temp.run',  'time-master:/home/time/Desktop/time-data/mce1/temp.run']).wait()
            elif os.path.exists(mce_file_name) :
                subprocess.Popen(['scp', mce_file_name,  'time-master:/home/time/Desktop/time-data/mce1/temp.%0.3i' % (a)]).wait()
                subprocess.Popen(['rm %s' % (mce_file_name)],shell=True)
                print 'File Transfered (MCE0):',(mce_file_name.replace(dir,''))
                a += 1
                begin = dt.datetime.utcnow()
            else:
                print "File Doesn't Exist!"
        end = dt.datetime.utcnow()

    else :
        print 'SFTP0 Stopped'
        subprocess.Popen(['rm /data/cryo/current_data/temp*'],shell=True)
        subprocess.Popen(["ssh -t time@time-master.caltech.edu 'pkill -f /home/time/time-software/main/read_files.py'"],shell=True)
        print 'File Read Stopped'
        sys.exit()


if __name__ == '__main__':
    main()
