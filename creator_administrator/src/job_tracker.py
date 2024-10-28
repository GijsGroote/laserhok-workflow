import sys
import json
import shutil
import copy
import os
import abc
import re
from datetime import datetime
from unidecode import unidecode

from PyQt6.QtWidgets import QWidget

from src.directory_functions import delete_item
from src.qmessagebox import YesOrNoMessageBox, InfoQMessageBox, TimedMessage, WarningQMessageBox
from src.mail_manager import MailManager

class JobTracker:
    '''
    Job tracker, serving two purposes:

    * storing additional info on the jobs.
    * a backup to check and repair the files on the file system.

    '''

    def __init__(self, parent: QWidget, gv: dict):
        self.gv = gv
        self.parent= parent
        self.job_keys = ['job_name', 'job_folder_global_path', 'dynamic_job_name', 'status',
                          'created_on_date', 'make_files', 'sender_name', 'sender_mail_adress', 'sender_mail_receive_time']
        #TODO: its this actually needed? these job keys? sender_name is not always present for example
        self.tracker_file_path = gv['TRACKER_FILE_PATH']
        self.tracker_backup_file_path = gv['TRACKER_FILE_PATH'].replace("job_log.json",
                                        "job_log_backup.json")

    @abc.abstractmethod
    def addJob(self,
               job_name: str,
               job_folder_global_path: str,
               make_files: dict,
               sender_name=None,
               sender_mail_adress=None,
               sender_mail_receive_time=None,
               status='WACHTRIJ',
               job_dict=None) -> dict:
        ''' Add a job to the tracker. '''

    def readTrackerFile(self):
        ''' Read the tracker file. '''

        with open(self.tracker_file_path, 'r' ) as tracker_file:
            self.tracker_dict = json.load(tracker_file)

    def writeTrackerFile(self):
        ''' Write the tracker file. '''
        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump(self.tracker_dict, tracker_file, indent=4)

    def deleteJob(self, job_name: str):
        ''' Delete a job from the job tracker. '''

        self.readTrackerFile()

        deleted_job_dict = self.tracker_dict.pop(job_name)
        delete_item(self.parent, self.gv, deleted_job_dict['job_folder_global_path'])

        self.writeTrackerFile()

    @abc.abstractmethod
    def checkHealth(self):
        ''' Check and repair system. '''

    def createTrackerFile(self):
        ''' Create the file that tracks jobs. '''
        if os.path.exists(self.tracker_backup_file_path):
            if YesOrNoMessageBox(self.parent,
                     text=f"Backup file detected at: {self.tracker_backup_file_path}'\
                         ', do you want to restore it?").answer():
                os.rename(self.tracker_backup_file_path, self.tracker_file_path)
                InfoQMessageBox(self.parent, "Backup restored!")
                return

        with open(self.tracker_file_path, 'w' ) as tracker_file:
            json.dump({}, tracker_file, indent=4)

        # this message can be created without the parent being fully initialised, resulting in error
        # InfoQMessageBox(self.parent, text='New job tracker file created')

    def checkTrackerFileHealth(self):
        if not os.path.exists(self.tracker_file_path):
            self.createTrackerFile()

        try:
            self.readTrackerFile()
        except json.decoder.JSONDecodeError:
            if os.path.isfile(self.tracker_backup_file_path):
                if YesOrNoMessageBox(self.parent,
                             'Do you want to restore the backup tracker file (Y/n)?'):
                    os.remove(self.tracker_file_path)
                    os.rename(self.tracker_backup_file_path, self.tracker_file_path)

            elif YesOrNoMessageBox(self.parent,
                           'Do you want to create a new empty tracker file (Y/n)?'):
                with open(self.tracker_file_path, 'w' ) as tracker_file:
                    json.dump({}, tracker_file, indent=4)
            else:
                InfoQMessageBox(self.parent, "Could not load tracker file, closing application.")
                sys.exit(0)

    def makeBackup(self):
        ''' Make a backup of the tracker file. '''
        try:
            shutil.copy(self.tracker_file_path, self.tracker_backup_file_path)
        except FileExistsError:
            os.remove(self.tracker_backup_file_path)
            shutil.copy(self.tracker_file_path, self.tracker_backup_file_path)

    def updateJobKey(self, job_key: str, job_name: str, new_value: str):
        ''' Update job key with a new value. '''

        self.readTrackerFile()

        assert job_name in self.tracker_dict, f'{job_name} not found in tracker dict'
        assert job_key in self.job_keys, f'job key {job_key} is not an existing job key'
        assert job_key in self.tracker_dict[job_name], f'{job_key} not found in job {job_name}'

        self.tracker_dict[job_name][job_key] = new_value

        self.writeTrackerFile()

    def markFilesAsDone(self, job_name: str, file_global_path: str, done: bool, all_files_done=False):
        ''' Update one or all make files to done. '''

        self.readTrackerFile()

        assert job_name is not None, 'Job name is None'
        assert isinstance(done, bool), 'done is not a boolean'
        assert job_name in self.tracker_dict, f'job name {job_name} not found in tracker dict'


        for file_dict in self.tracker_dict[job_name]['make_files'].values():
            if all_files_done:
                file_dict['done'] = done
            elif file_dict['file_global_path']==file_global_path:
                    file_dict['done'] = done

        self.writeTrackerFile()

    def updateJobName(self, job_name: str, new_job_name: str):
        ''' Update job name to new job name. '''
        self.readTrackerFile()

        assert job_name in self.tracker_dict, f'could not find job name {job_name} in tracker file.'
        assert new_job_name not in self.tracker_dict, f'already found new job name {job_name} in tracker file.'

        job_dict = self.tracker_dict.pop(job_name)
        job_dict['job_name'] = new_job_name
        job_dict['dynamic_job_name'] = job_dict['dynamic_job_name'].replace(job_name, new_job_name)
        self.tracker_dict[new_job_name] = job_dict

        self.writeTrackerFile()

    def isJobOld(self, created_on_date: str) -> bool:
        ''' Check if the job is old. '''
        created_on_date_object = datetime.strptime(created_on_date, "%d-%m-%Y")
        current_date_object = datetime.now()
        date_difference = current_date_object - created_on_date_object
        return date_difference.days > self.gv['DAYS_TO_KEEP_JOBS']
    
    def isJobDone(self, job_name: str) -> bool:
        ''' Return boolean indicating if a job is done. '''
        self.readTrackerFile()

        return all(file_dict['done'] for file_dict in self.tracker_dict[job_name]['make_files'].values())

    def getJobDict(self, job_name: str) -> dict:
        ''' Return the job dict from a job name. '''

        self.readTrackerFile()

        if job_name in self.tracker_dict:
            return self.tracker_dict[job_name]
        return None

    def getMakeFilesString(self, job_name: str) -> str:
        ''' Return a sting representation of all make files. '''

        self.readTrackerFile()

        return_string = ""
        for file_dict in self.tracker_dict[job_name]['make_files'].values():
            return_string += f'{file_dict["file_name"]}\n'

        return return_string

    def getJobValue(self, job_key: str, job_name: str):
        ''' Return the job value (indicated with a job key) of a job. '''

        self.readTrackerFile()

        assert job_name in self.tracker_dict, f'{job_name} not found in tracker dict'
        assert job_key in self.job_keys, f'job key {job_key} is not an existing job key'
        assert job_key in self.tracker_dict[job_name], f'{job_key} not found in job {job_name}'

        return self.tracker_dict[job_name][job_key]


    def getStaticAndDynamicJobNames(self, filter_jobs_on=None, filter_str=None) -> list[tuple]:
        ''' Return a list containing all static and dynamic job names that can be filtered on status and matching pattern. '''

        if filter_jobs_on is not None:
            assert filter_str is not None, 'filter string should not be None'
            assert filter_jobs_on in {'status', 'match'}, f'filter jobs on status or match, not {filter_jobs_on}'

        self.readTrackerFile()

        if filter_jobs_on is None:
            return [(job_name, job_dict['dynamic_job_name']) for job_name, job_dict in self.tracker_dict.items()]

        if filter_jobs_on == 'status':
            return [(job_name, job_dict['dynamic_job_name']) for 
                job_name, job_dict in self.tracker_dict.items() if job_dict['status'] == filter_str]

        if filter_jobs_on == 'match':
            return [(job_name, job_dict['dynamic_job_name']) for 
                job_name, job_dict in self.tracker_dict.items() if filter_str.lower() in job_name.lower()]

        raise ValueError('Should not reach this point')

    def getNumberOfJobsWithStatus(self, status_list: list) -> int:
        ''' Return the number of jobs that have a certain status. '''

        self.readTrackerFile()

        return len([job_key for job_key, job_value in self.tracker_dict.items() if job_value['status'] in status_list])

    def fileGlobalPathToJobName(self, file_global_path: str) -> str:
        ''' Return a job name from file any file in the job folder. '''
        self.readTrackerFile()

        for job_dict in self.tracker_dict.values():
            if file_global_path.startswith(job_dict['job_folder_global_path']):
                return job_dict['job_name']
            
        return None


    def makeJobNameUnique(self, job_name: str) -> str:
        ''' Make the job name unique.

        if the job name already exists append _(NUMBER) to job name to make it unique
        if the job_name is unique but job_name_(NUMBER) exist then return job_name_(NUMBER+1).
        '''

        job_name = unidecode(job_name)

        max_job_number = 0
        does_job_name_exist = False

        self.readTrackerFile()

        for job_dict in self.tracker_dict.values():

            match_job_number= re.search(rf'{job_name}_\((\d+)\)$', job_dict['job_name'])
            if job_name == job_dict['job_name']:
                does_job_name_exist = True

            if match_job_number:
                does_job_name_exist = True
                job_number = int(match_job_number.group(1))
                max_job_number = max(job_number, max_job_number)

        if max_job_number == 0:
            if does_job_name_exist:
                return job_name + '_(1)'
            return job_name
        return job_name + '_(' + str(max_job_number + 1) + ')'

    def deleteOldJobs(self):
        ''' Delete the old jobs from tracker and file system. '''

        self.readTrackerFile()

        # remove old jobs
        n_old_jobs = 0

        for job_key, job_dict in self.tracker_dict.items():
            created_on_date_object = datetime.strptime(job_dict['created_on_date'], "%d-%m-%Y")
            current_date_object = datetime.now()
            date_difference = current_date_object - created_on_date_object


            if date_difference.days > self.gv['DAYS_TO_KEEP_JOBS'] and job_dict['status'] != 'WACHTRIJ':
                n_old_jobs += 1
                self.deleteJob(job_key)

        if n_old_jobs > 0:
            TimedMessage(parent=self.parent, gv=self.gv, text=f'Removed {str(n_old_jobs)} old jobs')

        self.writeTrackerFile()

    def deleteNonExitentJobsFromTrackerFile(self):
        ''' Delete the jobs from tracker file that cannot be found on the file system. '''

        self.readTrackerFile()

        # find non existent jobs
        non_existent_job_keys = []
        for job_key, job_dict in self.tracker_dict.items():
            if not os.path.exists(job_dict['job_folder_global_path']):
                non_existent_job_keys.append(job_key)

        # delete non existent jobs from tracker file
        for key in non_existent_job_keys:
            self.tracker_dict.pop(key) 

        self.writeTrackerFile()

    def deleteNonExitentFilesFromTrackerFile(self):
        ''' Delete job files from tracker file that cannot be found on the file system. '''
        self.readTrackerFile()

        for job_dict in self.tracker_dict.values():
            temp_remove_keys = []
            # find non existent make files
            for file_key, file_dict in job_dict['make_files'].items():
                if not os.path.exists(file_dict['file_global_path']):
                    temp_remove_keys.append(file_key)

            # delete non existent make files from tracker file
            for key in temp_remove_keys:
                job_dict['make_files'].pop(key) 

        self.writeTrackerFile()

    def addNewJobstoTrackerFile(self, create_jobs_from_file_system_dialog): # pylint: disable=too-complex
        '''
        Synchronize job on file system and tracker file by either:
            * adding the job to the tracker file.
            or
            * removing the job folder from file system.
         '''

        self.readTrackerFile()

        # find job on file system that are not in the tracker file
        job_folder_not_in_tracker_global_paths = []
        for job_folder_global_path in os.listdir(self.gv['JOBS_DIR_HOME']):
            if not any([job_dict['job_folder_global_path'] == os.path.join(self.gv['JOBS_DIR_HOME'], job_folder_global_path) for job_dict in self.tracker_dict.values()]): # pylint: disable=use-a-generator

                job_folder_not_in_tracker_global_paths.append(os.path.join(self.gv['JOBS_DIR_HOME'], job_folder_global_path))

        if len(job_folder_not_in_tracker_global_paths) > 0:

            # remove date from the job folder names
            job_names_str = ''
            job_names_no_dates = []
            for job_folder_global_path in job_folder_not_in_tracker_global_paths:
                job_names_str += os.path.basename(job_folder_global_path) + '\n'
                match = re.search(r'^\d{2}-\d{2}_(.*)$', os.path.basename(job_folder_global_path))

                if match:
                    job_names_no_dates.append(match.group(1))
                else:
                    job_names_no_dates.append(os.path.basename(job_folder_global_path))

            if len(job_folder_not_in_tracker_global_paths) <= 1:
               is_or_are = 'is'
               folder_s = 'folder'
            else:
               is_or_are = 'are'
               folder_s = 'folders'

            if YesOrNoMessageBox(parent=self.parent,
                  text=f'OH NO, SYNCHRONIZE ISSUES!\nThere {is_or_are} {len(job_folder_not_in_tracker_global_paths)} job '\
                      f'{folder_s} that are not in the Job Tracker.\n\nHow do you want to to sync: \n{job_names_str}',
                  yes_button_text='Add files to Job Tracker',
                             no_button_text='Remove files from File System').answer():

                file_global_path_list = []
                job_dict_list = []

                for job_name, job_folder_global_path in zip(job_names_no_dates, job_folder_not_in_tracker_global_paths):

                    file_global_path_list.append(os.listdir(job_folder_global_path))

                    job_dict = {'job_name': job_name,
                                'job_folder_global_path': job_folder_global_path,
                                'make_files': {},
                                'status': 'WACHTRIJ',
                                'created_on_date': str(datetime.now().strftime("%d-%m-%Y")),
                                'dynamic_job_name': str(datetime.now().strftime("%d-%m"))+'_'+job_name}

                    mail_item_list = [os.path.join(job_folder_global_path, file) for file in os.listdir(job_folder_global_path) if file.lower().endswith(('.eml', '.msg'))]
                    if len(mail_item_list) > 0:

                        job_dict['sender_name'] = MailManager(self.gv).getSenderName(mail_item_list[0])
                        job_dict['sender_mail_adress'] = MailManager(self.gv).getEmailAddress(mail_item_list[0])
                        job_dict['sender_mail_receive_time'] = MailManager(self.gv).getSenderMailReceiveTime(mail_item_list[0])

                    job_dict_list.append(job_dict)

                    if job_dict['job_name'] not in self.tracker_dict:
                        self.tracker_dict[job_dict['job_name']] = job_dict

                self.writeTrackerFile()

                # check for jobs with no make files, add them.
                job_names_no_make_files = []
                job_names_no_make_files_str = ''

                for counter, (job_name, files_global_paths, job_dict) in enumerate(
                        zip(copy.copy(job_names_no_dates), copy.copy(file_global_path_list), copy.copy(job_dict_list))):

                    make_files_global_paths = [file_path for file_path
                                           in files_global_paths if file_path.lower().endswith(self.gv['ACCEPTED_EXTENSIONS'])]

                    if len(make_files_global_paths) == 0:
                        self.addJob(job_name, None, None, job_dict=job_dict)
                        job_names_no_dates.remove(job_name)
                        file_global_path_list.remove(files_global_paths)
                        job_dict_list.remove(job_dict)
                        job_names_no_make_files.append(job_name)
                        job_names_no_make_files_str += f'\n{job_name}'

                    else:
                        file_global_path_list[counter] = make_files_global_paths


                if len(job_names_no_make_files) > 0:
                    if len(job_names_no_make_files) == 1:
                        job_or_jobs = 'job'
                    else:
                        job_or_jobs = 'jobs'

                    InfoQMessageBox(parent=self.parent,
                             text=f'Added {len(job_names_no_make_files)} {job_or_jobs} to the Job Tracker that contain no files to make: {job_names_no_make_files_str}')

                if len(job_names_no_dates) > 0:


                    dialog = create_jobs_from_file_system_dialog(self.parent,
                                              job_names_no_dates,
                                              file_global_path_list,
                                              update_existing_job=True,
                                              job_dict_list=job_dict_list)

                    if dialog.exec() == 1:
                        InfoQMessageBox(parent=self.parent,
                                text=f'Added {len(job_folder_not_in_tracker_global_paths)} jobs to the Job Tracker.')

                    else:
                         WarningQMessageBox(parent=self.parent, gv=self.gv, text='System not healthy 😟!')
                         self.system_healthy = False


            else:
                for job_folder_global_path in job_folder_not_in_tracker_global_paths:
                    delete_item(self.parent, self.gv, job_folder_global_path)

                InfoQMessageBox(parent=self.parent,
                             text=f'Deleted {len(job_folder_not_in_tracker_global_paths)} job folders from File System.')


    def addNewFilestoTrackerFile(self, create_jobs_from_file_system_dialog): # pylint: disable=too-complex
        '''
        Synchronize job files on file system and tracker file by either:

            * adding the job files to the tracker file.
            or
            * removing the job files from file system.
         '''
        self.readTrackerFile()

        for job_folder_name in os.listdir(self.gv['JOBS_DIR_HOME']):
            job_folder_global_path = os.path.join(self.gv['JOBS_DIR_HOME'], job_folder_name)

            job_dict = self.getJobDict(self.fileGlobalPathToJobName(job_folder_global_path))

            if job_dict is None:
                continue

            # check if jobs are incomplete and must be repaired
            if not self.IsJobDictAndFileSystemInSync(job_dict, job_folder_global_path):

                valid_file_names = [file_name for file_name in os.listdir(
                    job_folder_global_path) if file_name.lower().endswith(self.gv['ACCEPTED_EXTENSIONS'])]

                new_make_files = []
                for file in valid_file_names:

                    # for make_file_dict in job_dict['make_files'].values():
                        # print(make_file_dict['file_global_path'])

                    if not any([os.path.basename( # pylint: disable=use-a-generator
                        make_file_dict['file_global_path'])==file for make_file_dict in job_dict['make_files'].values()]):
                        new_make_files.append(os.path.join(job_folder_global_path, file))

                        # print(f'appending this file now {file}')

                # add/delete new files
                if len(new_make_files) > 0:

                    if len(new_make_files)==1:
                        file_or_files = 'file'
                        this_or_these = 'this'
                    else:
                        file_or_files = 'files'
                        this_or_these = 'these'

                    yes_or_no_text = f'New {file_or_files} detected for job {job_dict["job_name"]}:\n'
                    for file in new_make_files:
                        yes_or_no_text += f'{os.path.basename(file)}\n'

                    yes_or_no_text += f'\nWhat do you want with {this_or_these} {file_or_files}?'

                    yes_or_no = YesOrNoMessageBox(parent=self.parent,
                                                  text=yes_or_no_text,
                                                  yes_button_text='Add to Job Tracker',
                                                  no_button_text='Remove from File System')
                    if yes_or_no.answer():


                        dialog = create_jobs_from_file_system_dialog(self.parent,
                                                        [job_dict['job_name']],
                                                        [new_make_files],
                                                        update_existing_job=True,
                                                        job_dict_list=[job_dict])

                        if dialog.exec() == 1:
                            InfoQMessageBox(parent=self.parent,
                                        text=f'Added {len(new_make_files)} new {file_or_files} to Job:  {job_dict["job_name"]}.')

                        else:
                             WarningQMessageBox(parent=self.parent, gv=self.gv, text='System not healthy 😟!')
                             self.system_healthy = False


                    else:
                        for file in new_make_files:
                            delete_item(self.parent, self.gv,
                                        os.path.join(job_folder_global_path, file))

                        InfoQMessageBox(parent=self.parent, 
                             text=f'Removed {len(new_make_files)} {file_or_files} from File System')



    def IsJobDictAndFileSystemInSync(self, job_dict, job_folder_global_path):
        ''' Check for a job if all files are in both the tracker and the file system. '''

        file_system_file_names = [file_name for file_name in os.listdir(
            job_folder_global_path) if file_name.lower().endswith(self.gv['ACCEPTED_EXTENSIONS'])]

        tracker_file_names = [os.path.basename(
            file_dict['file_global_path']) for file_dict in job_dict['make_files'].values()]

        if len(file_system_file_names) != len(tracker_file_names):
            return False
        if not any(file_system_file_name==tracker_file_name for 
                   file_system_file_name, tracker_file_name in zip(file_system_file_names, tracker_file_names)):
            return False
        return True
