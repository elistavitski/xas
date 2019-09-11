from datetime import datetime
import os
from subprocess import call
import numpy as np
import pandas as pd
from . import xray
from .xia import xiaparser


def load_dataset_from_xia(db,uid='82e91527-6a68-4eae-8760-443fd3d2222d'):
    hdr = db[uid]
    path_to_xia_file = hdr.start['xia_filename']
    xp = xiaparser()
    xp.parse(path_to_xia_file)
    data = xp.df


    all_counts = np.zeros((data.shape[1],12))

    for pixel in range(data.shape[1]):
        for mca in range(1, 17):
            counts = []
            for roi in range(12):
                hi = hdr.start['xia_rois'][f'xia1_mca{mca}_roi{roi}_high']
                lo = hdr.start['xia_rois'][f'xia1_mca{mca}_roi{roi}_low']
                if hi >= 0 and lo >= 0:
                    p_hi = int(round(hi * 2048 / hdr.start['xia_max_energy']))
                    p_lo = int(round(lo * 2048 / hdr.start['xia_max_energy']))
                    all_counts[pixel, roi] += np.sum(data.iloc[mca-1,pixel].data[p_lo:p_hi+1])



    return all_counts


def timestamp_rois(timestamps, all_counts):
    rois = {}
    for roi in range(12):
        roi_i = pd.DataFrame()
        rois[f'roi{roi}'] = roi_i
        roi1 = all_counts[:,0]
        shortest = np.min((roi1.shape[0], timestamps.shape[0]))

        roi_i['timestamp'] = timestamps.iloc[0:shortest].data
        roi_i['roi1'] = roi1[0:shortest]


return shortest



    
