from datetime import datetime
import os
from subprocess import call
import numpy as np
import pandas as pd
from . import xray



def load_dataset_from_files(db,uid):

    def load_adc_trace(filename='', master = True):
        df=pd.DataFrame()
        keys = ['times', 'timens', 'counter', 'adc_master', 'adc_slave']
        if os.path.isfile(filename):
            df_raw = pd.read_table(filename, delim_whitespace=True, comment='#', names=keys, index_col=False)
            df['timestamp'] = df_raw['times'] + 1e-9 * df_raw['timens']
            if master:
                df['adc'] = df_raw['adc_master'].apply(lambda x: (int(x, 16) >> 8) -
                                                                 0x40000 if (int(x, 16) >> 8) > 0x1FFFF else int(x, 16) >> 8) * 7.62939453125e-05
            else:
                df['adc'] = df_raw['adc_slave'].apply(lambda x: (int(x, 16) >> 8) -
                                                                 0x40000 if (int(x, 16) >> 8) > 0x1FFFF else int(x, 16) >> 8) * 7.62939453125e-05
            return df
        else:
            return -1

    def load_enc_trace(filename=''):
        df = pd.DataFrame()
        keys = ['times', 'timens', 'encoder', 'counter', 'di']
        if os.path.isfile(filename):
            df_raw = pd.read_table(filename, delim_whitespace=True, comment='#', names=keys, index_col=False)
            df['timestamp'] = df_raw['times'] + 1e-9 * df_raw['timens']
            df['encoder'] = df_raw['encoder'].apply(lambda x: int(x) if int(x) <= 0 else -(int(x) ^ 0xffffff - 1))
            return df
        else:
            return -1

    def load_trig_trace(filename=''):
        keys = ['times', 'timens', 'encoder', 'counter', 'di']
        if os.path.isfile(filename):
            df = pd.read_table(filename, delim_whitespace=True, comment='#', names=keys,
                               index_col=False)
            df['timestamp'] = df['times'] + 1e-9 * df['timens']
            df = df.iloc[::2]
            return df.iloc[:, [5, 3]]
        else:
            return -1

    arrays = {}
    record = db[uid]
    for stream in record['descriptors']:
        data = pd.DataFrame()
        stream_device = stream['name']
        # WIP Another terrible hack
        try:
            stream_name = stream['data_keys'][stream['name']]['devname']
            print(f'STREAM {stream_name}')
            stream_file = stream['data_keys'][stream['name']]['filename']
        except:
            print('STREAM IS NOT FOUND')
            stream_name = None
            stream_file = None

        stream_source = stream['data_keys'][stream['name']]['source']

        print(stream_file)

        if stream_source == 'pizzabox-di-file':
            data = load_trig_trace(stream_file)
        if stream_source == 'pizzabox-adc-file':
            print(f'STREAM DEVICE {stream_device}')

            #Monkey patch to deal with dual ADC
            if ('adc4' in stream_device) or  ('adc6' in stream_device) or  ('adc8' in stream_device):
                data = load_adc_trace(stream_file, master=False)
            else:
                data = load_adc_trace(stream_file, master=True)
            stream_offset = f'{stream_device} offset'
            if stream_offset in db[uid]['start']:
                print("subtracting offset")
                data.iloc[:, 1] = data.iloc[:, 1] - record['start'][stream_offset]
            #stream_gain =  f'{stream_device} gain'
            # if stream_gain in db[uid]['start']:
            #   print("correcting for gain")
            #   data.iloc[:, 1] = data.iloc[:, 1]/(10**record['start'][stream_gain])


        if stream_source == 'pizzabox-enc-file':
            data = load_enc_trace(stream_file)
            print(stream_name)
            if stream_name =='mono1_enc':
                data.iloc[:,1] = xray.encoder2energy(data['encoder'], 26222.222222222223,
                                                       -float(record['start']['angle_offset']))
                stream_name = 'energy'
                print(f'STREAM NAME {stream_name}')
        if stream_name is not None:
            arrays[stream_name] = data

    return arrays

def validate_file_exists(path_to_file,file_type = 'interp'):
    if file_type == 'interp':
        prefix = 'r'
    elif file_type == 'bin':
        prefix = 'b'
    if os.path.isfile(path_to_file):
        (path, extension) = os.path.splitext(path_to_file)
        iterator = 2

        while True:

            new_filename = '{}-{}{:04d}{}'.format(path, prefix, iterator,extension)
            if not os.path.isfile(new_filename):
                return new_filename
            iterator += 1
    else:
        return path_to_file


def validate_path_exists(db, uid):
    path_to_file = db[uid].start['interp_filename']
    (path, filename) = os.path.split(path_to_file)
    if not os.path.isdir(path):
        os.mkdir(path)
    else:
        print('...........Path exists')

def create_file_header(db,uid):
    facility = db[uid]['start']['Facility']
    beamline = db[uid]['start']['beamline_id']
    pi = db[uid]['start']['PI']
    proposal = db[uid]['start']['PROPOSAL']
    saf = db[uid]['start']['SAF']

    comment = db[uid]['start']['comment']
    year = db[uid]['start']['year']
    cycle = db[uid]['start']['cycle']
    scan_id = db[uid]['start']['scan_id']
    real_uid = db[uid]['start']['uid']
    start_time = db[uid]['start']['time']
    stop_time = db[uid]['stop']['time']
    human_start_time = str(datetime.fromtimestamp(start_time).strftime('%m/%d/%Y  %H:%M:%S'))
    human_stop_time = str(datetime.fromtimestamp(stop_time).strftime('%m/%d/%Y  %H:%M:%S'))
    human_duration = str(datetime.fromtimestamp(stop_time - start_time).strftime('%M:%S'))

    hdr = db[uid]
    foil_e = hdr.start['foil_element']
    foil_element = foil_e[0]

    hutchB_ion_chamber_gain = hdr.start['keithley_gainsB']
    hutchB_i0_gain = hutchB_ion_chamber_gain[0]
    hutchB_it_gain = hutchB_ion_chamber_gain[1]
    hutchB_ir_gain = hutchB_ion_chamber_gain[2]
    hutchB_iff_gain = hutchB_ion_chamber_gain[3]

    hutchB_ionchamber_GasRate = hdr.start['ionchamber_ratesB']
    hutchB_ion_chamber_gas_i0_He = hutchB_ionchamber_GasRate[0]
    hutchB_ion_chamber_gas_i0_N2 = hutchB_ionchamber_GasRate[1]
    hutchB_ion_chamber_gas_i0_Ar = hutchB_ionchamber_GasRate[2]
    hutchB_ion_chamber_gas_it_N2 = hutchB_ionchamber_GasRate[3]
    hutchB_ion_chamber_gas_it_Ar = hutchB_ionchamber_GasRate[4]

    hutchB_incpathPos = hdr.start['incident_beampathB']
    hutchB_incpath_vertical = hutchB_incpathPos[0]

    hutchB_slitsPos = hdr.start['incident_slits']
    hutchB_slits_top      = hutchB_slitsPos[0]
    hutchB_slits_bottom   = hutchB_slitsPos[1]
    hutchB_slits_inboard  = hutchB_slitsPos[2]
    hutchB_slits_outboard = hutchB_slitsPos[3]

    hutchB_samplestagePos = hdr.start['sample_stageB']
    hutchB_samplestage_rot = hutchB_samplestagePos[0]
    hutchB_samplestage_x   = hutchB_samplestagePos[1]
    hutchB_samplestage_y   = hutchB_samplestagePos[2]
    hutchB_samplestage_z   = hutchB_samplestagePos[3]

    pe_verticalPos = hdr.start['pe_vertical']
    pe_vertical = pe_verticalPos[0]

    cm_horizontalPos = hdr.start['cm_horizontal']
    frontend_cm_xu = cm_horizontalPos[0]
    frontend_cm_xd = cm_horizontalPos[1]

    if 'trajectory_name' in db[uid]['start']:
        trajectory_name = db[uid]['start']['trajectory_name']
    else:
        trajectory_name = ''

    if 'element' in db[uid]['start']:
        element = db[uid]['start']['element']
    else:
        element = ''

    if 'edge' in db[uid]['start']:
        edge = db[uid]['start']['edge']
    else:
        edge = ''

    if 'e0' in db[uid]['start']:
        e0 = db[uid]['start']['e0']
    else:
        e0 = ''

    comments =   '# Facility: {}\n'\
                 '# Beamline: {}\n'\
                 '# Year: {}\n' \
                 '# Cycle: {}\n' \
                 '# SAF: {}\n' \
                 '# PI: {}\n'\
                 '# Proposal: {}\n'\
                 '# Scan ID: {}\n' \
                 '# UID: {}\n'\
                 '# Comment: {}\n' \
                 '# Start time: {}\n' \
                 '# Stop time: {}\n' \
                 '# Total time: {}\n' \
                 '# Trajectory name: {}\n'\
                 '# Element: {}\n'\
                 '# Edge: {}\n'\
                 '# E0: {}\n'\
                 '# Reference Foil Element: {}\n'\
                 '# Keithley Gains I0: 1E{} V/A It: 1E{} V/A Iref: 1E{} V/A PIPS: 1E{} V/A \n'\
                 '# Ion Chamber Gas Flow Rates: I0: {:.2f} sccm He + {:.2f} sccm N2 + {:.2f} sccm Ar \n'\
                 '# Ion Chamber Gas Flow Rates: It&Iref: {:.2f} sccm N2 + {:.2f} sccm Ar\n'\
                 '# Incident Beam Path Vertical: {:.2f} mm\n'\
                 '# Incident Slits Positions B: TOP: {} mm Bottom: {} mm Inboard: {} mm Outboard: {} mm\n'\
                 '# Sample Stage Positions: Rotation: {} deg Horizontal: {:.2f} mm Vertical: {:.2f} mm Beam Direction: {:.2f} mm\n'\
                 '# PerkinElmer Vertical Position: {:.2f} mm\n'\
                 '# Front End Mirror Horizontal Positions: Up: {:.2f} mm Down: {:.2f} mm\n#\n# '.format(
                  facility,
                  beamline,
                  year,
                  cycle,
                  saf,
                  pi,
                  proposal,
                  scan_id,
                  real_uid,
                  comment,
                  human_start_time,
                  human_stop_time,
                  human_duration,
                  trajectory_name,
                  element,
                  edge,
                  e0,
                  foil_element,
                  hutchB_i0_gain, hutchB_it_gain, hutchB_ir_gain, hutchB_iff_gain,
                  hutchB_ion_chamber_gas_i0_He, hutchB_ion_chamber_gas_i0_N2, hutchB_ion_chamber_gas_i0_Ar,
                  hutchB_ion_chamber_gas_it_N2, hutchB_ion_chamber_gas_it_Ar,
                  hutchB_incpath_vertical,
                  hutchB_slits_top, hutchB_slits_bottom, hutchB_slits_inboard, hutchB_slits_outboard,
                  hutchB_samplestage_rot, hutchB_samplestage_x, hutchB_samplestage_y, hutchB_samplestage_z,
                  pe_vertical,
                  frontend_cm_xu, frontend_cm_xd)
    return  comments

def find_e0(db, uid):
    e0 = -1
    if 'e0' in db[uid]['start']:
        e0 = float(db[uid]['start']['e0'])
    return e0


def save_interpolated_df_as_file(path_to_file, df, comments):
    cols = df.columns.tolist()
    fmt = '%17.6f ' + '%12.6f ' + (' '.join(['%12.6e' for i in range(len(cols)-2)]))
    header = '  '.join(cols)

    df = df[cols]
    np.savetxt(path_to_file,
               df.values,
               fmt=fmt,
               delimiter=" ",
               header=header,
               comments= comments)

    #print("changing permissions to 774")
    call(['chmod', '774', path_to_file])


def save_binned_df_as_file(path_to_file, df, comments):
    (path, extension) = os.path.splitext(path_to_file)
    path_to_file = path + '.dat'
    path_to_file = validate_file_exists(path_to_file,file_type = 'bin')
    cols = df.columns.tolist()[::-1]
    #cols = cols[-1:] + cols[:-1]
    fmt = '%12.6f ' + (' '.join(['%12.6e' for i in range(len(cols) - 1)]))
    header = '  '.join(cols)
    df = df[cols]
    np.savetxt(path_to_file,
               df.values,
               fmt=fmt,
               delimiter=" ",
               header=header,
               comments=comments)

    #print("changing permissions to 774")
    call(['chmod', '774', path_to_file])
    return path_to_file



def load_interpolated_df_from_file(filename):
    ''' Load interp file and return'''

    if not os.path.exists(filename):
        raise IOError(f'The file {filename} does not exist.')
    header = read_header(filename)
    keys = header[header.rfind('#'):][1:-1].split()
    df = pd.read_table(filename, delim_whitespace=True, comment='#', names=keys, index_col=False).sort_values(keys[1])
    return df, header


def read_header(filename):
    header = ''
    line = '#'
    with open(filename) as myfile:
        while line[0] == '#':
            line = next(myfile)
            header += line
    return header[:-len(line)]


