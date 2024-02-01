import sys
from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import traceback
from src.qmessagebox import InfoQMessageBox, WarningQMessageBox, ErrorQMessageBox, TimedMessage
from src.worker import Worker, WorkerSignals
from src.mail_manager import MailManager


class ThreadedMailManager():
    ''' 
    Worker specific for threaded mail operations such 
    as sending mail, retrieving mail, or moving mail to a seperate folder. 
    '''

    def __init__(self, parent_widget, gv:dict):
        self.gv=gv
        self.thread_pool = gv['THREAD_POOL']
        self.parent_widget = parent_widget
        self.signals = WorkerSignals()

    def sendConfirmationMail(self,
                                success_message: str,
                                error_message: str,
                                job_folder_global_path: str,
                                template_content: dict,
                                msg,
                                *args,
                                **kwargs):
        """ Send a confirmation mail. """
        self.success_message = success_message
        self.error_message = error_message
        self.msg = msg
        self.args = args
        self.kwargs = kwargs

        self.displaySuccessMessage()

        mail_manager = MailManager(self.gv)

        msg_file_path = mail_manager.getMailGlobalPathFromFolder(job_folder_global_path)
        
        self.worker = Worker(mail_manager.replyToEmailFromFileUsingTemplate,
                                msg_file_path=msg_file_path,
                                template_file_name="RECEIVED_MAIL_TEMPLATE",
                                template_content=template_content,
                                popup_reply=False)

        self.worker.signals.finished.connect(self.displaySuccessMessage)
        self.worker.signals.result.connect(self.displaySuccessMessageData)
        self.worker.signals.error.connect(self.handleMailError)

        print('start woker')
        self.thread_pool.start(self.worker)
        print(f'sucecss message??')

    def displaySuccessMessage(self):
        ''' Display a confirmation message to the user. '''
        print(f'display success message please {self.success_message}')
        TimedMessage(self.gv, parent=self.parent_widget, text=self.success_message)

    def displaySuccessMessageData(self, data):
        ''' Display a confirmation message to the user. '''
        print(f'display {data} success message please {self.success_message}')
        TimedMessage(self.gv, parent=self.parent_widget, text=self.success_message)

    def handleMailError(self, exc: Exception):
        ''' Handle the mail Error. '''
        assert isinstance(exc, Exception), f'Expected type Exception, received type: {type(exc)}'

        if isinstance(exc, ConnectionError):
            ErrorQMessageBox(self.parent_widget, text=f'Connection Error {self.error_message}: {str(exc)}')
        else:
            raise exc
            # ErrorQMessageBox(self.parent_widget, text=f'Error Occured: {str(exc)}')
