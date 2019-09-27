from  . import xray

import pandas as pd

def load_dataset_em(db,uid):
    record = db[uid]
    arrays = {}
    hdr = db[uid]
    adc_data = list(hdr.data('em1', stream_name='em1'))[0][0]
    columns = adc_data.columns[1:]
    for column in columns:
        array = pd.DataFrame()
        array['timestamp']=adc_data['timestamp']
        array['adc'] = adc_data[column]
        arrays[column]=array

    array = pd.DataFrame()
    enc_data = list(hdr.data('pb9_enc1', stream_name='pb9_enc1'))[0]
    array['timestamp'] = enc_data['ts_s'] + 1e-9 *enc_data['ts_ns']
    encoder = enc_data['encoder'].apply(lambda x: int(x) if int(x) <= 0 else -(int(x) ^ 0xffffff - 1))
    array['energy'] = xray.encoder2energy(encoder, 360000,
                                          -float(record['start']['angle_offset']))

    arrays['energy'] = array

    return arrays


