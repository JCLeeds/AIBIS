#import matlab.engine
import sys 
from scipy.io import loadmat
import pandas as pd
import numpy as np
import shutil
# import simple_plot as sp
import subprocess as sp
import os
import matlab.engine 
import scrape_USGS as sUSGS
# import misc_scripts.data_ingestion_legacy as DI
import data_ingestion as DI 
import os 
import numpy as np
import LiCSBAS03op_GACOS as gacos
import LiCSBAS05op_clip_unw as clip
import LiCSBAS04op_mask_unw as mask 
import LiCSBAS_io_lib as LiCS_lib
import LiCSBAS_tools_lib as LiCS_tools
from lmfit.model import *
import matplotlib.pyplot as plt
from scipy import stats
from matplotlib.colors import LinearSegmentedColormap as LSC
from matplotlib import pyplot as plt
import matplotlib.path as path
import obspy as obspy
import re
import scipy 
import LiCSBASJC_downsample as ds 
import LiCSBAS_plot_lib as LiCS_plot
import time 
import multiprocessing as multi 
import preproc as DaN
import subprocess as sp 
import os
import h5py
from scipy import io
from scipy.io import loadmat
import LiCSBASJC_output as op 
import pandas as pd
import time 
import output_model as om
import pygmt
import timeout_decorator
import pickle
import datetime 
import local2llh as l2llh
import GBIS_run as GR 
import shutil 

@timeout_decorator.timeout(10800) # Times out after 6 hours 
def main(USGS_ID):
    locations_usgs = []
    locations_reloc_NP1 = []
    locations_reloc_NP2 = []  
    opt_models_NP1 = [] 
    opt_models_NP2 = [] 
    # try:
    print('RUNNING AGAIN ')
    # with open(full_test[ii]+'_preproc.pkl', 'wb') as outp:
    preproc_object = DaN.deformation_and_noise(USGS_ID,
                                            target_down_samp=1000,
                                            inv_soft='GBIS',
                                            look_for_gacos=True,
                                            # NP=2,
                                            all_coseis=True,
                                            single_ifgm=False,
                                            coherence_mask=0.1,
                                            min_unw_coverage=0.3, 
                                            pygmt=True,
                                            # date_primary=20200531,
                                            # date_secondary=20200718,
                                            # frame=Frame,
                                            scale_factor_mag=0.075,
                                            scale_factor_depth=0.075,
                                            scale_factor_clip_mag=0.25,
                                            scale_factor_clip_depth=0.0055,
                                            loop_processing_flow=True
                                            )
    preproc_object_copy = preproc_object

    GBIS_object = GR.auto_GBIS(preproc_object,'/home/ee18jwc/code/auto_inv/GBIS.location',NP=1,number_trials=1e5,
                                pygmt=False,generateReport=True,location_search=False,limit_trials=False)

    shutil.move(GBIS_object.outputdir,GBIS_object.outputdir + '_location_run')
    locations_usgs.append([float(preproc_object.event_object.time_pos_depth['Position'][0]),float(preproc_object.event_object.time_pos_depth['Position'][1])])

    print( preproc_object.event_object.time_pos_depth['Position'][0])
    print( preproc_object.event_object.time_pos_depth['Position'][1])
    preproc_object.event_object.time_pos_depth['Position'][0] = GBIS_object.GBIS_lat
    preproc_object.event_object.time_pos_depth['Position'][1] = GBIS_object.GBIS_lon
    print( preproc_object.event_object.time_pos_depth['Position'][0])
    print( preproc_object.event_object.time_pos_depth['Position'][1])
    # preproc_object.scale_factor_depth = 0.065
    # preproc_object.scale_factor_mag = 0.065
    # if os.path.isdir(preproc_object.event_object.LiCS_locations + '_USGS_location_used'):
    #     shutil.rmtree(preproc_object.event_object.LiCS_locations + '_USGS_location_used')
    # else:
    #     pass
    shutil.copytree(preproc_object.event_object.LiCS_locations,preproc_object.event_object.LiCS_locations + '_USGS_location_used')
    preproc_object.flush_all_processing()
    # preproc_object.geoc_path, preproc_object.gacos_path = preproc_object.data_block.pull_frame_coseis()
    # preproc_object.check_data_pull()
    # preproc_object.geoc_path =  preproc_object.check_geoc_has_data(preproc_object.geoc_path)
    attempt = 0
    while attempt < 8: # incase data is pulled incorrectly or copied wrong
        try:
            preproc_object.geoc_path, preproc_object.gacos_path = preproc_object.data_block.pull_frame_coseis()
            preproc_object.check_data_pull()
            preproc_object.geoc_path =  preproc_object.check_geoc_has_data(preproc_object.geoc_path)
            # flush_all_processing
            preproc_object.run_processing_flow(True)
            preproc_object.geoc_final_path = preproc_object.geoc_ds_path
            preproc_object.move_final_output()
            attempt = 8
        except Exception as e:
            preproc_object.flush_all_processing()
            preproc_object.geoc_path, preproc_object.gacos_path = preproc_object.data_block.pull_frame_coseis()
            preproc_object.check_data_pull()
            preproc_object.geoc_path =  preproc_object.check_geoc_has_data(preproc_object.geoc_path)
            attempt+=1
            print(e)
            print('processing flow failed trying again with attempt number ' + str(attempt))
            if attempt > 4:
                print('Failed 5 times on processing flow check errors')

    
                # pickle.dump(preproc_object,outp)



# if GBIS_run == True: 
# for ii in range(len(full_test[ii])):
#     with open(full_test[ii]+'_preproc.pkl', 'rb') as inp:
    # preproc_object = pickle.load(inp)
    
    try:
        GBIS_object = GR.auto_GBIS(preproc_object,'GBIS.location',NP=1,number_trials=2e5,pygmt=True,limit_trials=False)
        locations_reloc_NP1.append([GBIS_object.GBIS_lat,GBIS_object.GBIS_lon]) 
        opt_models_NP1.append(GBIS_object.opt_model)
    except Exception as e:
            print(e)
            pass 
    try:
        print('I am in this try')
        GBIS_object = GR.auto_GBIS(preproc_object,'GBIS.location',NP=2,number_trials=2e5,pygmt=True,limit_trials=False)
        locations_reloc_NP2.append([GBIS_object.GBIS_lat,GBIS_object.GBIS_lon]) 
        opt_models_NP2.append(GBIS_object.opt_model)
    except Exception as e:
        print(e)
        pass 


    shutil.rmtree(preproc_object.event_object.LiCS_locations)
    shutil.rmtree(preproc_object.event_object.LiCS_locations + '_USGS_location_used')

    # except Exception as e:
    #     print(e)
    #     print(crashed_events)
 

if __name__ == '__main__':
    # array = ['us6000a8nh']
    df = pd.read_csv('/uolstore/Research/a/a285/homes/ee18jwc/code/auto_inv/gCent_Catalog_no_header_info.csv')
    df_china = df[df['Location'] == 'China']
    df_Iran = df[df['Location'] == 'Iran']
    df_turkey = df[df['Location'] == 'Turkey']
    df_pakist = df[df['Location'] == 'Pakistan']

    # rest_of_data = df[df['Location'] !='Pakistan' and df['Location'] != 'Iran' and df['Location']!='Turkey' and df['Location']!= 'China']
    
    # full_test = array + list(df_china.ComCatID)+ list(df_Iran.ComCatID) + list(df_turkey.ComCatID) 
    
    # full_test = ['us7000g9zq']
    # full_test = ['us6000a8nh']
    # full_test = ['us70008cld']
    # full_test = ['us600068w0']
    
    # full_test = ['us70006sj8']

    full_test = [
                'us6000b26j',
                'us6000ddge',
                'us6000dxge',
                'us6000dyuk',
                'us6000jk0t',
                'us6000kynh',
                'us6000mjpj',
                'us7000abmk',
                'us7000cet5',
                'us7000fu12',
                'us7000gebb',
                'us60007anp',
                'us7000df40',
                'us6000bdq8',
                'us70006sj8', 
                'us7000g9zq',  
                'us70008cld',
                'us600068w0',
                'us7000m3ur',
                'us6000a8nh',

    ]
    failed_tests = [] 
    full_test = full_test + list(df_china.ComCatID)+ list(df_Iran.ComCatID) + list(df_turkey.ComCatID) +list(df_pakist.ComCatID) 
    # full_test = []
    # full_test = ['us70008cld','us6000jk0t']
    # full_test = ['us6000jk0t']
    for ii in range(len(full_test)):
        try:
            main(full_test[ii])
        except Exception as e: 
            print(e)
            print(full_test[ii])
        #     failed_tests.append(full_test[ii])