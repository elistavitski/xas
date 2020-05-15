from datetime import datetime
import os
from subprocess import call
import numpy as np
import pandas as pd
from . import xray

def load_data_with_xs3(db,uid):
    hdr = db[uid]
    roi_lims=hdr.start['rois']

    # Get Xs3 data
    roi1 = []
    roi2 = []
    roi3 = []
    roi4 = []
    xs_data = hdr.table(stream_name='xs',fill=True)['xs']
    for point in xs_data:
        chsum = point['ch_1'] + point['ch_2'] + point['ch_3'] + point['ch_4']
        r1 = sum(chsum[roi_lims[0]:roi_lims[1]])
        r2 = sum(chsum[roi_lims[2]:roi_lims[3]])
        r3 = sum(chsum[roi_lims[4]:roi_lims[5]])
        r4 = sum(chsum[roi_lims[6]:roi_lims[7]])
        roi1.append(r1)
        roi2.append(r2)
        roi3.append(r3)
        roi4.append(r4)


    # Get time stamps
    trigger_ts = hdr.table(stream_name='pb2_di', fill=True)['pb2_di'][1]
    triggers = []
    for trigger in trigger_ts:
        t= trigger.ts_s + 1e-9 * trigger.ts_ns
        triggers.append(t)

    roi1 = np.array(roi1)
    roi2 = np.array(roi2)
    roi3 = np.array(roi3)
    roi4 = np.array(roi4)
    triggers = np.array(triggers)
    triggers_up = triggers[::2]

    ROI1 = pd.DataFrame()
    ROI2 = pd.DataFrame()
    ROI3 = pd.DataFrame()
    ROI4 = pd.DataFrame()



    if len(triggers_up) >= len(r1):
        last_num = len(r1)
        ROI1['timestamp']= triggers_up[0:last_num]
        ROI1['roi'] = roi1
        ROI2['timestamp'] = triggers_up[0:last_num]
        ROI2['roi'] = roi2
        ROI3['timestamp'] = triggers_up[0:last_num]
        ROI3['roi'] = roi3
        ROI4['timestamp'] = triggers_up[0:last_num]
        ROI4['roi'] = roi4
    else:
        last_num = len(triggers_up)
        ROI1['timestamp']= triggers_up
        ROI1['roi'] = roi1[0:last_num]
        ROI2['timestamp'] = triggers_up[0:last_num]
        ROI2['roi'] = roi2[0:last_num]
        ROI3['timestamp'] = triggers_up[0:last_num]
        ROI3['roi'] = roi3[0:last_num]
        ROI4['timestamp'] = triggers_up[0:last_num]
        ROI4['roi'] = roi4[0:last_num]



    return ROI1, ROI2, ROI3, ROI4
