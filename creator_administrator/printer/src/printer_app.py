import sys
import os
from typing import List

from PyQt6 import QtWidgets

sys.path.append(os.path.abspath('')) # to find gv and prevent ModuleNotFoundError
sys.path.append(os.path.abspath('creator_administrator')) # to find gv and prevent ModuleNotFoundError

from creator_administrator.printer.src.global_variables import gv

from src.app import MainWindow
from src.qmessagebox import WarningQMessageBox
from src.threaded_mail_manager import ThreadedMailManager
from src.qdialog import FilesSelectQDialog, FolderSelectQDialog

from printer_job_tracker import PrintJobTracker
from printer_settings_dialog import PrintSettingsQDialog

from printer_qdialog import (
        CreatePrintJobsFromMailQDialog,
        CreatePrintJobsFromFileSystemQDialog,
        PrintSearchJobDialog)

class PrintMainWindow(MainWindow):
    def __init__(self, *args, **kwargs):
        ui_global_path = os.path.join(gv['LOCAL_UI_DIR'], 'printer_main_window.ui')
        super().__init__(ui_global_path, gv, *args, **kwargs)

        self.valid_msgs = []
        self.threadpool = gv['THREAD_POOL']

        self.job_tracker = PrintJobTracker(parent=self)
        self.job_tracker.checkHealth()
        self.refreshAllWidgets()


        # menu bar actions
        self.importFromMailAction.triggered.connect(self.handleNewValidMails)
        self.selectFilesAction.triggered.connect(self.openSelectFilesDialog)
        self.selectFoldersAction.triggered.connect(self.openSelectFolderDialog)


        self.menuSettings.setToolTipsVisible(True)
        self.editSettingsAction.triggered.connect(self.openEditSettingsDialog)
        self.checkHealthAction.triggered.connect(self.checkHealth)


    def handleNewValidMails(self):
        ''' Handle the new mails in the inbox. '''
        
        self.threaded_mail_manager = ThreadedMailManager(self, gv, dialog=CreatePrintJobsFromMailQDialog)
        # getValidmails gets mail and triggers openImportFromMailDialog
        self.threaded_mail_manager.getValidMailsFromInbox()
        


    def openSelectFilesDialog(self):
        ''' Open dialog to select multiple files. ''' 
        dialog = FilesSelectQDialog(self, gv)

        if dialog.exec() == 1:
            files_global_paths = dialog.selectFilesButton.files_global_paths
            job_name = dialog.projectNameQLineEdit.text()

            if len(files_global_paths) > 0:
                CreatePrintJobsFromFileSystemQDialog(self, [job_name], [files_global_paths]).exec()
            
        self.refreshAllWidgets()

    def openSelectFolderDialog(self):
        ''' Open dialog to select folder with multiple subfolders. ''' 
        dialog = FolderSelectQDialog(self, gv)

        if dialog.exec() == 1:
            folder_global_path = dialog.selectFolderButton.folder_global_path
            project_name = dialog.projectNameQLineEdit.text()
            folders_global_paths_list = []
            jobs_names_list = []

            if not os.path.exists(folder_global_path):
                WarningQMessageBox(self, gv, text='<Folder> does not exist')
                return

            for subfolder in os.listdir(folder_global_path):
                subfolder_global_path = os.path.join(folder_global_path, subfolder)

                if os.path.isdir(subfolder_global_path):
                    files_in_subfolder_global_paths = []
                    subfolder_contains_print_file = False

                    for item in os.listdir(subfolder_global_path):
                        item_global_path = os.path.join(subfolder_global_path, item)
                        if os.path.isdir(item_global_path):
                            WarningQMessageBox(self, gv, text=f'{subfolder_global_path} contains a folder '\
                                f'{item_global_path} which is skipped' )
                            continue

                        if item_global_path.lower().endswith(gv['ACCEPTED_EXTENSIONS']):
                            files_in_subfolder_global_paths.append(item_global_path)
                            subfolder_contains_print_file = True

                    if subfolder_contains_print_file:
                        folders_global_paths_list.append(files_in_subfolder_global_paths)
                        jobs_names_list.append(project_name+'_'+os.path.basename(subfolder))
                    else:
                        WarningQMessageBox(self, gv, text=f'No print file found in {subfolder_global_path}'\
                                f' skip this subfolder')
            
            if len(jobs_names_list) > 0:
                CreatePrintJobsFromFileSystemQDialog(self, jobs_names_list, folders_global_paths_list).exec()


    def openEditSettingsDialog(self):
        ''' Open dialog to edit the settings. '''
        PrintSettingsQDialog(self).exec()

    def openSearchJobDialog(self):
        ''' Open the search job dialog. '''
        PrintSearchJobDialog(self).exec()


class PrinterMainApp(QtWidgets.QApplication):

    def __init__(self, argv: List[str]) -> None:
        super().__init__(argv)

    def build(self):
        main_window = PrintMainWindow()
        main_window.show()
        return main_window
        
    def run(self):
        self.exec()

if __name__ == '__main__':

    printer_app = PrinterMainApp(sys.argv)
    printer_app.build()
    printer_app.run()
