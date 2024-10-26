'''
Global variables/Settings specific for the computer managing the printer machine.
'''

import json
import os
import sys
import shutil

from PyQt6.QtCore import QThreadPool

if sys.platform == 'linux':
    settings_dir_home = os.path.join(os.path.expanduser('~'), '.creator_administrator')
elif sys.platform == 'win32':
    settings_dir_home = os.path.join(os.getenv('LOCALAPPDATA'), 'Creator Administrator')
else: 
    raise ValueError(f'This software does not work for platform: {sys.platform}')

if not os.path.exists(settings_dir_home):
    os.mkdir(settings_dir_home)

settings_file_path = os.path.join(settings_dir_home, 'print_settings.json')

# Create default settings file 
if not os.path.exists(settings_file_path):

    this_file_path = os.path.dirname(os.path.realpath(__file__))
    if sys.platform == 'win32':
        repo_folder_name = r'creator_administrator\creator_administrator'
    elif sys.platform == 'linux':
        repo_folder_name = 'creator_administrator/creator_administrator'
    else:
        raise ValueError(f'Software not intended for platform {sys.platform}')
    
    if repo_folder_name in this_file_path:
        root, _ = this_file_path.split(repo_folder_name)
        repo_dir_home = os.path.join(root, repo_folder_name)
    else:
        raise ValueError(f'could not find folder {repo_folder_name}')

    desktop_dir_home = os.path.join(os.path.expanduser('~'), 'Desktop')
    if os.path.exists(desktop_dir_home):
        todo_dir_home = os.path.join(desktop_dir_home, 'Print TODO')
    else:
        raise ValueError('Could not find users Desktop directory')

    with open(os.path.join(repo_dir_home, 'printer/email_templates/print_settings_template.json'), 'r') as settings_template_file:
        default_settings_dict = json.load(settings_template_file)


        default_settings_dict ["REPO_DIR_HOME"] = repo_dir_home
        default_settings_dict ["TODO_DIR_HOME"] = todo_dir_home
        default_settings_dict ["DATA_DIR_HOME"] = settings_dir_home 
        default_settings_dict ["RECEIVED_MAIL_TEMPLATE"] = os.path.join(repo_dir_home, "printer/email_templates/DEFAULT_RECEIVED_MAIL_TEMPLATE.html"),
        default_settings_dict ["FINISHED_MAIL_TEMPLATE"] = os.path.join(repo_dir_home, "printer/email_templates/DEFAULT_FINISHED_MAIL_TEMPLATE.html"),
        default_settings_dict ["DECLINED_MAIL_TEMPLATE"] = os.path.join(repo_dir_home, "printer/email_templates/DEFAULT_DECLINED_MAIL_TEMPLATE.html")

        if sys.platform == 'linux':
            default_settings_dict["MAIL_NAME"] = "Fill in Your Name"
            default_settings_dict["MAIL_INBOX_NAME"] = "Inbox"
            default_settings_dict["MAIL_ADRESS"] = "Fill in Your Mail Adress"

            default_settings_dict["MAIL_PASSWORD"]= "Fill in Your Mail Password"

    with open(os.path.join(settings_dir_home, 'print_settings.json'), 'w') as settings_file:
        json.dump(default_settings_dict, settings_file, indent=4)



with open(settings_file_path, 'r') as settings_file:
    gv_data = json.load(settings_file)
    if 'DATA_DIR_HOME' in gv_data:
        data_dir_home = gv_data['DATA_DIR_HOME']
    else:
        data_dir_home = settings_dir_home


jobs_dir_home = os.path.join(data_dir_home, 'print_jobs')
tracker_file_path = os.path.join(data_dir_home, 'print_job_log.json')
temp_dir_home = os.path.join(data_dir_home, 'TEMP')

for directory in (data_dir_home, jobs_dir_home, temp_dir_home):
    if not os.path.exists(directory):
        os.mkdir(directory)

# remove temp_dir_home content
for temp_item in os.listdir(temp_dir_home):
    try:
        shutil.rmtree(os.path.join(temp_dir_home, temp_item))

    except NotADirectoryError:
        os.remove(os.path.join(temp_dir_home, temp_item))

    except PermissionError:
        pass

    
# Global Variables (gv)
gv = {'SETTINGS_FILE_PATH': settings_file_path,
      'DATA_DIR_HOME': data_dir_home,
      'TEMP_DIR_HOME': temp_dir_home,
      'JOBS_DIR_HOME': jobs_dir_home,
      'TRACKER_FILE_PATH': tracker_file_path}

# Load settings into global variables (gv)
with open(settings_file_path, 'r') as settings_file:
    gv_data = json.load(settings_file)
    gv['REPO_DIR_HOME'] = gv_data['REPO_DIR_HOME']
    
    if 'DEFAULT_SLICER_EXECUTABLE_PATH' in gv_data:
        gv['DEFAULT_SLICER_EXECUTABLE_PATH'] = gv_data['DEFAULT_SLICER_EXECUTABLE_PATH']


    if 'SPECIAL_PRINTERS' in gv_data:
        gv['SPECIAL_PRINTERS'] = gv_data['SPECIAL_PRINTERS']
        for key, printer in gv_data['SPECIAL_PRINTERS'].items():
            gv['SPECIAL_PRINTERS'][key]['ACCEPTED_MATERIALS'] = tuple(
                    gv_data['SPECIAL_PRINTERS'][key]['ACCEPTED_MATERIALS'])

    else:
        gv['SPECIAL_PRINTERS'] = {}

    # TODO, For loop this below
    if 'MAIL_ADRESS' in gv_data:
        gv['MAIL_ADRESS'] = gv_data['MAIL_ADRESS']
    
    if 'MAIL_NAME' in gv_data:
        gv['MAIL_NAME'] = gv_data['MAIL_NAME']
    
    if 'MAIL_PASSWORD' in gv_data:        
        gv['MAIL_PASSWORD'] = gv_data['MAIL_PASSWORD']
    
    gv['TODO_DIR_HOME'] = gv_data['TODO_DIR_HOME']

    gv['ACCEPTED_EXTENSIONS'] = tuple(gv_data['ACCEPTED_EXTENSIONS'].split(', '))
    gv['ACCEPTED_MATERIALS'] = tuple(gv_data['ACCEPTED_MATERIALS'].split(', '))
    gv['DEFAULT_PRINTER_NAME'] = gv_data['DEFAULT_PRINTER_NAME']

    gv['DAYS_TO_KEEP_JOBS'] = int(gv_data['DAYS_TO_KEEP_JOBS'])
    gv['DARK_THEME'] = gv_data['DARK_THEME'] == 'true'


    gv['ONLY_UNREAD_MAIL'] = gv_data['ONLY_UNREAD_MAIL'] == 'true'
    gv['MOVE_MAILS_TO_VERWERKT_FOLDER'] = gv_data['MOVE_MAILS_TO_VERWERKT_FOLDER'] == 'true'
    gv['SEND_MAILS_ON_SEPERATE_THREAD'] = gv_data['SEND_MAILS_ON_SEPERATE_THREAD'] == 'true'
    gv['EMPTY_TODO_DIR_BEFORE_EXPORT'] =  gv_data['EMPTY_TODO_DIR_BEFORE_EXPORT'] == 'true'
    gv['DISPLAY_TEMP_MESSAGES'] = gv_data['DISPLAY_TEMP_MESSAGES'] == 'true'
    gv['DISPLAY_WARNING_MESSAGES'] = gv_data['DISPLAY_WARNING_MESSAGES'] == 'true'


    if 'MAIL_INBOX_NAME' in gv_data:
        gv['MAIL_INBOX_NAME'] = gv_data['MAIL_INBOX_NAME']
    else:
        gv['MAIL_INBOX_NAME'] = 'Inbox'


    for mail_template in ('RECEIVED_MAIL_TEMPLATE',
                          'DECLINED_MAIL_TEMPLATE',
                          'FINISHED_MAIL_TEMPLATE'):

        if mail_template in gv_data:
            if os.path.exists(gv_data[mail_template]):
                gv[mail_template] = gv_data[mail_template]
            else:
                raise FileNotFoundError(f'could not find file: {gv_data[mail_template]}')
        else:
            gv[mail_template] = os.path.join(
                    gv['REPO_DIR_HOME'],
                    'printer/email_templates', 'DEFAULT_'+mail_template+'.html')

gv['SLICED_FILE_EXTENSIONS'] = tuple('.gcode, .bgcode, .gcode.3mf'.split(', '))

if not os.path.exists(gv["TODO_DIR_HOME"]):
    os.mkdir(gv["TODO_DIR_HOME"])

if gv['DARK_THEME']:
    gv['GOOD_COLOR_HEX'] = '#3F643F'
    gv['BAD_COLOR_HEX'] = '#165a72'
    gv['GOOD_COLOR_RGBA'] = 'rgba(0, 255, 0, 0.7)'
    gv['BAD_COLOR_RGBA'] = 'rgba(255, 0, 0, 0.7)'
else: 
    # light theme 
    gv['GOOD_COLOR_HEX'] = '#7fc97f'
    gv['BAD_COLOR_HEX'] = '#add8e5'
    gv['GOOD_COLOR_RGBA'] = 'rgba(0, 255, 0, 0.4)'
    gv['BAD_COLOR_RGBA'] = 'rgba(255, 0, 0, 0.4)'


gv['GLOBAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'src')
gv['LOCAL_SRC_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'printer/src')
gv['GLOBAL_UI_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'ui')
gv['LOCAL_UI_DIR'] = os.path.join(gv['REPO_DIR_HOME'], 'printer/ui')

# import functions from src
sys.path.append(gv['REPO_DIR_HOME'])
sys.path.append(gv['GLOBAL_SRC_DIR'])
sys.path.append(gv['LOCAL_SRC_DIR'])
sys.path.append(gv['GLOBAL_UI_DIR'])
sys.path.append(gv['LOCAL_UI_DIR'])

gv['FIGURES_DIR_HOME'] = os.path.join(gv['REPO_DIR_HOME'], 'figures')
gv['THREAD_POOL'] = QThreadPool() # the one and only threadpool


