import netCDF4 as nc
import os, sys
import time as t
import datetime as now
import numpy as np
from termcolor import colored
import config.utils as ut
from config import directory
# os.nice(-20)

def new_file(filestarttime,dir):
    """
    Purpose: to create a new netcdf file for the mce/K-mirror/telescope data
    Inputs: filestarttime - the time of the first set of data that is appended to the file
            dir - the directory in which you want to create the netcdf files
    Outputs : None
    Calls : None
    """
    mce = nc.Dataset(dir + "/raw_mce_%s.nc" %(filestarttime),"w",format="NETCDF4_CLASSIC")

     # GUI PARAMETERS ---------------------------------------------------------------------------------
    mce.createDimension('det',1)
    mce.createDimension('obs',3)
    mce.createDimension('date',26)
    mce.createDimension('f',8)
    mce.createDimension('mode',2)
    mce.createDimension('r',1)
    mce.createDimension('t',None)
    # Dimensions for Data Arrays -------------------------------------------------------------------
    mce.createDimension('raw_rows',33)
    mce.createDimension('raw_cols',32)
    mce.createDimension('raw_num', int(ut.german_freq))
    mce.createDimension('k',1)
    mce.createDimension('v',1700)
    mce.createDimension('hk_tuple',2)
    mce.createDimension('hk_det',256)
    mce.createDimension('hk_num', int(ut.german_freq))
    mce.createDimension('hk',1)
    mce.createDimension('sf',5)
    mce.createDimension('tel_pos',21)
    mce.createDimension('kms_pos',4)
    mce.createDimension('sock_rate',20)
    mce.createDimension('time_num',100)

    # creating MCE variables --------------------------------------------------------------------------------
    Observer = mce.createVariable("observer","S1",("obs",))
    Datetime = mce.createVariable('datetime', 'S1',('date',))
    Frames = mce.createVariable('frames', 'S1',('f',))
    Datamode = mce.createVariable('datamode','S1',('mode',))
    Detector = mce.createVariable('detector','f8',('det',))
    Rc = mce.createVariable('rc','S1',('r',)) # can either use rc name or integer used by gui
    # creating HK variables --------------------------------------------------------------------------------
    global HK_Data
    HK_Data = mce.createVariable('hk_data','f8',('t','hk_num','hk_det'))
    global HK_Time
    HK_Time = mce.createVariable('hk_time', 'f8',('t','hk_tuple','hk_num'))
    # =========================================================================

    global Time
    Time = mce.createVariable('time','f8',('t','time_num','mode'))

    # MCE DATA =============================================================================================
    global MCE0_Raw_Data_All
    global MCE1_Raw_Data_All
    MCE0_Raw_Data_All = mce.createVariable('mce0_raw_data_all','f8',('t','raw_rows','raw_cols','raw_num'))
    MCE1_Raw_Data_All = mce.createVariable('mce1_raw_data_all','f8',('t','raw_rows','raw_cols','raw_num'))
    # =========================================================================================================

    # MCE ROW COL On/Off ========================================================================================
    global MCE0_on_off
    global MCE1_on_off
    MCE0_on_off = mce.createVariable('mce0_on_off','i4',('t','raw_rows','raw_cols'))
    MCE1_on_off = mce.createVariable('mce1_on_off','i4',('t','raw_rows','raw_cols'))
    # ============================================================================================================

    # MCE HEADER INFO =========================================================
    global MCE0_Header
    global MCE1_Header
    MCE0_Header = mce.createVariable('mce0_header','f8',('t','v','k'))
    MCE1_Header = mce.createVariable('mce1_header','f8',('t','v','k'))
    # =========================================================================

    # TELESCOPE Data ==============================================================
    global Tel
    Tel = mce.createVariable('tel','f8',('t','sock_rate','tel_pos'))
    # ================================================================================

    # KMS Data ======================================================================
    global KMS
    KMS = mce.createVariable('kms','f8',('t','sock_rate','kms_pos'))
    # ================================================================================

    global Status_Flags
    Status_Flags = mce.createVariable('status','i4',('t','k','sf'))

    parafile = (directory.temp_dir + 'tempparameters.txt')
    with open(parafile, 'r') as f :
        content = f.readlines()
    parameters = [x.strip().split('\n') for x in content]

    Observer._Encoding = 'ascii'
    Frames._Encoding = 'ascii'
    Datamode._Encoding = 'ascii'
    Rc._Encoding = 'ascii'

    Observer[:] = np.array([parameters[0][0]],dtype='S3')
    Frames[:] = np.array([parameters[3][0]],dtype='S8')
    Datamode[:] = np.array([parameters[1][0]],dtype='S2')
    Rc[:] = np.array([parameters[2][0]],dtype='S1')
    mce.close()

def data_append(nc_file, p, flags, head1, head2, mce0_data, mce1_data, mce0_on, mce1_on, tele, kms, hk_data):
    """
    Purpose: to append data to the netcdf file created in the above function
    inputs: nc_file - the file in which you want to append data to
    Outputs: None
    Calls : None
    """
    if os.path.exists(nc_file):
        mce = nc.Dataset(nc_file,"r+",format="NETCDF4_CLASSIC")
        Status_Flags[p,:,:] = flags
        HK_Data[p,:,:] = hk_data[0]
        HK_Time[p,:,:] = hk_data[1]

        if ut.which_mce[0] == 1 :
            MCE0_Raw_Data_All[p,:,:,:] = mce0_data
            MCE0_Header[p,:,:] = head1
            MCE0_on_off[p,:,:] = mce0_on

        if ut.which_mce[1] == 1 :
            MCE1_Raw_Data_All[p,:,:,:] = mce1_data
            MCE1_Header[p,:,:] = head2
            MCE1_on_off[p,:,:] = mce1_on

        Tel[p,:,:] = tele
        KMS[p,:,:] = kms
        mce.close()
    else :
        print(colored("Could find NETCDF File!", 'red'))
