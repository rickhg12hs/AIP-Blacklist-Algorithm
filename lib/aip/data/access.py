import datetime as dt
import logging
import pandas as pd
import numpy as np

from pathlib import Path
from os import scandir, path
from joblib import Parallel, delayed
from aip.data.functions import scramble, read_zeek, getrawdata, removerawdata

project_dir = Path(__file__).resolve().parents[3]

def _process_zeek_file(date):
    '''
    Create a dataset for the date string date in the data/interim folder
    THIS FUNCTION IS DESTRUCTIVE and will overwrite the datasets for the processed date if exists.
    '''
    logger = logging.getLogger(__name__)
    honeypots = pd.read_csv(path.join(project_dir, 'data', 'external', 'honeypots_public_ips.csv'))
    ips = honeypots.public_ip.values
    # if data directory does not exist, execute the magic to get it
    if path.isdir(path.join(project_dir,'data','raw', date)) == False:
        logging.debug(f'Downloading data for {date}')
        getrawdata(date)
    # after this point, if directory does not exist, we can skip it.
    try:
        zeek_files = (x for x in scandir(path.join(project_dir,'data','raw', date)) if x.name.startswith('conn.'))
    except FileNotFoundError:
        logger.warning(f'Skipping {path.join(project_dir,"data","raw", date)}. Directory not exist.')
        return
    daily = pd.DataFrame()
    for z in zeek_files:
        #df = read_zeek(z, usecols=['id.orig_h', 'id.resp_h'])
        hourly = pd.DataFrame()
        zeekdata = read_zeek(z)
        logger.debug(f'Processing hourly file: {z.name}')
        for ip in ips:
            #hourly = hourly.append(zeekdata[zeekdata['id.resp_h'] == ip])
            hourly = pd.concat([hourly, zeekdata[zeekdata['id.resp_h'] == ip]])
        #hourly.to_csv(path.join(project_dir,'data','interim', f'hourly.conn.{date}-{z.name[5:10]}.csv'), index=False)
        #logger.debug('Writting file: ' + path.join(project_dir,'data','interim', f'hourly.conn.{date}-{z.name[5:10]}.csv'))
        #daily = daily.append(hourly)
        daily = pd.concat([daily, hourly])
    daily.to_csv(path.join(project_dir,'data','interim', f'daily.conn.{date}.csv'), index=False)
    logger.debug('Writting file: ' + path.join(project_dir,'data','interim', f'daily.conn.{date}.csv'))
    #logger.debug('Removing raw data (not needed anymore): ' + path.join(project_dir,'data','raw', f'{date}'))
    #removerawdata(date)
    return

def _extract_attacks(date):
    '''
    Create a dataset for the date string date in the data/interim folder
    THIS FUNCTION IS DESTRUCTIVE and will overwrite the datasets for the processed date if exists.
    '''
    logger = logging.getLogger(__name__)
    try:
        daily = pd.read_csv(path.join(project_dir,"data","interim", f'daily.conn.{date}.csv'))
        daily['ts'] = pd.to_datetime(daily['ts'])
        daily['duration'] = daily.duration.replace('-',0).astype(float)
    except FileNotFoundError:
        logger.warning(f'Skipping {path.join(project_dir,"data","interim", f"daily.conn.{date}.csv")}. File not exist.')
        # Generate an empty attacks file
        pd.DataFrame(columns=['orig', 'flows', 'duration', 'packets', 'bytes']).to_csv(
                path.join(project_dir,'data','processed', f'attacks.{date}.csv'), index=False)
        return

    # Calculate the total attacks for each origin
    df = daily[['id.orig_h', 'duration', 'orig_pkts', 'orig_ip_bytes']].groupby(['id.orig_h']).sum()
    df.rename(columns={'duration':'duration', 'orig_pkts':'packets', 'orig_ip_bytes':'bytes'}, inplace=True)
    df['orig'] = df.index.values
    df['flows'] = daily.groupby(['id.orig_h']).count().ts.values
    df.reset_index(drop=True, inplace=True)
    logger.debug('Writting file: ' + path.join(project_dir,'data','processed', f'attacks.{date}.csv'))
    df.to_csv(path.join(project_dir,'data','processed', f'attacks.{date}.csv'), columns=['orig', 'flows', 'duration', 'packets', 'bytes'], index=False)
    logger.debug('Removing raw data (not needed anymore): ' + path.join(project_dir,'data','raw', f'{date}'))
    removerawdata(date)
    return

def process_zeek_files(dates=None):
    """ 
    Creates the dataset or part of it
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'Making  dataset from raw data for dates {dates}')
    if dates is None:
        dates = []
        for x in scandir(path.join(project_dir, 'data', 'raw')):
            try:
                dt.datetime.strptime(x.name, '%Y-%m-%d')
                dates.append(x.name)
            except ValueError:
                pass
    Parallel(n_jobs=12, backend='multiprocessing')(delayed(_process_zeek_file)(date) for date in dates)
    return

def extract_attacks(dates=None):
    """
    Creates the dataset or part of it
    """
    logger = logging.getLogger(__name__)
    logger.debug(f'Creating attacks for dates {dates}')
    filesready = [x.name for x in scandir(path.join(project_dir, 'data', 'processed'))]
    datesnotready = []
    for date in dates:
        if f'daily.conn.{date}.csv' not in filesready:
            datesnotready.append(date)
    process_zeek_files(datesnotready)
    if dates is None:
        dates = []
        for x in scandir(path.join(project_dir, 'data', 'interim')):
            try:
                dt.datetime.strptime(x.name, '%Y-%m-%d')
                dates.append(x.name)
            except ValueError:
                pass
    Parallel(n_jobs=12, backend='multiprocessing')(delayed(_extract_attacks)(date) for date in dates)
    return

def get_attacks(start=None, end=None, dates=None, usecols=None):
    '''
    Returns a DataFrame with the attacks between the dates start and end or the
    ones especified in the list dates.
    '''
    if start is not None:
        dates = [str(x.date()) for x in pd.date_range(start, end)]
    
    filesready = [x.name for x in scandir(path.join(project_dir, 'data', 'processed'))]
    datesnotready = []
    for date in dates:
        if f'attacks.{date}.csv' not in filesready:
            datesnotready.append(date)
    if len(datesnotready) > 0:
        extract_attacks(datesnotready)
    dfs = [pd.read_csv(path.join(project_dir, 'data', 'processed',f'attacks.{date}.csv'), usecols=usecols)
            for date in dates]
    return dfs

if __name__ == '__main__':
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    #logging.basicConfig(level=logging.INFO, format=log_fmt)
    logging.basicConfig(level=logging.DEBUG, format=log_fmt)

    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    #load_dotenv(find_dotenv())

    extract_attacks()
