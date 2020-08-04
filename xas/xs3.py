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
        ch_roi1_sum = 0
        ch_roi2_sum = 0
        ch_roi3_sum = 0
        ch_roi4_sum = 0
        for ch in range(len(xs_data[1].columns)):


            channel = point['ch_{}'.format(ch+1)]
            ch_roi1_lo = roi_lims[ch][0]
            ch_roi1_hi = roi_lims[ch][1]
            ch_roi2_lo = roi_lims[ch][2]
            ch_roi2_hi = roi_lims[ch][3]
            ch_roi3_lo = roi_lims[ch][4]
            ch_roi3_hi = roi_lims[ch][5]
            ch_roi4_lo = roi_lims[ch][6]
            ch_roi4_hi = roi_lims[ch][7]
            ch_roi1_sum += sum(channel[ch_roi1_lo:ch_roi1_hi])
            ch_roi1_sum += sum(channel[ch_roi2_lo:ch_roi2_hi])
            ch_roi1_sum += sum(channel[ch_roi3_lo:ch_roi3_hi])
            ch_roi1_sum += sum(channel[ch_roi4_lo:ch_roi4_hi])

        roi1.append(ch_roi1_sum)
        roi2.append(ch_roi2_sum)
        roi3.append(ch_roi3_sum)
        roi4.append(ch_roi4_sum)


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



    if len(triggers_up) >= len(roi1):
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
