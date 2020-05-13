from datetime import datetime
import os
from subprocess import call
import numpy as np
import pandas as pd
from . import xray



def load_data_with_xs3(db,uid):

    doc= db[uid].start
    xs3_filename = doc['xs3_filename']
    print(xs3_filename)
    rois =doc['rois']
    table_xs = db[uid].table(stream_name='xs',fill=True)
    xs_data = t_xs['xs']

    for point in xsdata:
        chsum = point['ch_1'] + point['ch_2'] + point['ch_3'] + point['ch_4']
        r1 = sum(chsum[rois[0]:rois[1]])
        r2 = sum(chsum[rois[2]:rois[3]])
        roi1.append(r1)
        roi2.append(r2)

    time_stamp = hdr.table(stream_name='pb2_di', fill=True)
    ts = time_stamp['pb2_di'][1]

    triggers = []
    for trigger in ts:
        t= trigger.ts_s + 1e-9 * trigger.ts_ns
        triggers.append(t)









            # def load_adc_trace(filename='', master = True):
    #     df=pd.DataFrame()
    #     keys = ['times', 'timens', 'counter', 'adc_master', 'adc_slave']
    #     if os.path.isfile(filename):
    #         df_raw = pd.read_table(filename, delim_whitespace=True, comment='#', names=keys, index_col=False)
    #         df['timestamp'] = df_raw['times'] + 1e-9 * df_raw['timens']
    #         if master:
    #             df['adc'] = df_raw['adc_master'].apply(lambda x: (int(x, 16) >> 8) -
    #                                                              0x40000 if (int(x, 16) >> 8) > 0x1FFFF else int(x, 16) >> 8) * 7.62939453125e-05
    #         else:
    #             df['adc'] = df_raw['adc_slave'].apply(lambda x: (int(x, 16) >> 8) -
    #                                                              0x40000 if (int(x, 16) >> 8) > 0x1FFFF else int(x, 16) >> 8) * 7.62939453125e-05
    #         return df
    #     else:
    #         return -1