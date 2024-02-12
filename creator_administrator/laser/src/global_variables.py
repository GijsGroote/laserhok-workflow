"""
Global variables specific for the local machine managing the PMMA laser.
"""

import json
import os
import sys
from PyQt6.QtCore import QThreadPool

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if sys.platform == 'linux':
    data_dir_home = os.path.join(os.path.expanduser('~'), '.creator-administrator')
elif sys.platform == 'win32':
    data_dir_home = os.path.join(os.getenv('LOCALAPPDATA'), 'creator-administrator')
else: 
    raise ValueError(f'This software does not work for platform: {sys.platform}')

if not os.path.exists(data_dir_home):
    os.mkdir(data_dir_home)
    
settings_file_path = os.path.join(data_dir_home, 'laser_settings.json')
jobs_dir_home = os.path.join(data_dir_home, 'laser_jobs')
tracker_file_path = os.path.join(data_dir_home, 'laser_job_log.json')

# TODO: move this to setup file
if not os.path.exists(settings_file_path):
    with open(settings_file_path, 'w') as settings_file:
        json.dump(dict(), settings_file, indent=4)

if not os.path.exists(jobs_dir_home):
    os.mkdir(jobs_dir_home)
    
# Global Variables (gv)
gv = {'SETTINGS_FILE_PATH': settings_file_path,
      'DATA_DIR_HOME': data_dir_home,
      'JOBS_DIR_HOME': jobs_dir_home,
      'TRACKER_FILE_PATH': tracker_file_path}

# TODO: if this is not all in the file, do a setup wizard please
with open(settings_file_path, 'r') as settings_file:
    gv_data = json.load(settings_file)
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']

    if 'MAIL_NAME' in gv_data and\
        'MAIL_ADRESS' in gv_data and\
        'MAIL_PASSWORD' in gv_data:

        gv['MAIL_NAME'] = gv_data['MAIL_NAME']
        gv['MAIL_ADRESS'] = gv_data['MAIL_ADRESS']
        gv['MAIL_PASSWORD'] = gv_data['MAIL_PASSWORD']
    
    gv['TODO_DIR_HOME'] = gv_data['TODO_DIR_HOME']

    gv['ACCEPTED_EXTENSIONS'] = tuple(gv_data['ACCEPTED_EXTENSIONS'].split(', '))
    gv['ACCEPTED_MATERIALS'] = tuple(gv_data['ACCEPTED_MATERIALS'].split(', '))

    gv['DAYS_TO_KEEP_JOBS'] = int(gv_data['DAYS_TO_KEEP_JOBS'])
    gv['DARK_MODE'] = True if gv_data['DARK_MODE'] == 'true' else False
    gv['THEME_COLOR_HEX'] = gv_data['THEME_COLOR_HEX']


    gv['ONLY_UNREAD_MAIL'] = True if gv_data['ONLY_UNREAD_MAIL'] == 'true' else False
    gv['MOVE_MAILS_TO_VERWERKT_FOLDER'] = True if gv_data['MOVE_MAILS_TO_VERWERKT_FOLDER'] == 'true' else False
    gv['DISPLAY_TEMP_MESSAGES'] = True if gv_data['DISPLAY_TEMP_MESSAGES'] == 'true' else False
    gv['DISPLAY_WARNING_MESSAGES'] = True if gv_data['DISPLAY_WARNING_MESSAGES'] == 'true' else False

    gv['PASSWORD'] = gv_data['PASSWORD']


    if 'MAIL_INBOX_NAME' in gv_data:
        gv['MAIL_INBOX_NAME'] = gv_data['MAIL_INBOX_NAME']
    else:
        gv['MAIL_INBOX_NAME'] = 'Inbox'


    for mail_template in ['RECEIVED_MAIL_TEMPLATE',
                          'DECLINED_MAIL_TEMPLATE',
                          'FINISHED_MAIL_TEMPLATE']:

        if mail_template in gv_data:
            if os.path.exists(gv_data[mail_template]):
                gv[mail_template] = resource_path(gv_data[mail_template])
            else:
                raise FileNotFoundError(f'could not find file: {gv_data[mail_template]}')
        else:
            gv[mail_template] = resource_path(os.path.join(
                    gv['REPO_DIR_HOME'],
                    'laser/email_templates', 'DEFAULT_'+mail_template+'.html'))


    gv['GOOD_COLOR_RGBA'] = 'rgba(0, 255, 0, 0.4)'
    gv['BAD_COLOR_RGBA'] = 'rgba(255, 0, 0, 0.4)'

gv['GLOBAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'src')
gv['LOCAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'laser/src')
gv['UI_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], 'laser/ui')

# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])
sys.path.append(gv['GLOBAL_SRC_DIR'])
sys.path.append(gv['LOCAL_SRC_DIR'])
sys.path.append(gv['UI_DIR_HOME'])

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], 'figures')

gv['THREAD_POOL'] = QThreadPool() # the one and only threadpool

