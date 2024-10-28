import os
import abc
import webbrowser
from functools import partial
# import qdarktheme

from PyQt6 import QtGui
from PyQt6.QtGui import QShortcut, QKeySequence 
from PyQt6.QtWidgets import QMainWindow, QListWidget
from PyQt6.uic import loadUi
import qdarkstyle
from qdarkstyle.dark.palette import DarkPalette


from src.qdialog import AboutDialog
from src.qmessagebox import TimedMessage

class MainWindow(QMainWindow):

    def __init__(self, ui_global_path: str, gv: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loadUi(ui_global_path, self)

        # well that does not really work
        self.setStyleSheet(
            qdarkstyle.load_stylesheet(
                qt_api="pyqt6",
                palette=DarkPalette,
                # palette=LightPalette if darkdetect.isLight() else DarkPalette
            )
        )

        self.setWindowIcon(QtGui.QIcon(os.path.join(gv['FIGURES_DIR_HOME'], 'logo.ico')))
        if gv['DARK_THEME']:
            # qdarktheme.setup_theme()
            self.setStyleSheet('''QToolTip { 
                           background-color: black; 
                           color: white; 
                           border: black solid 1px
                           }''')
            
        self.gv = gv


        self.openDocumentationAction.triggered.connect(
                partial(webbrowser.open, 'https://gijsgroote.github.io/creator_administrator/docs/intro/'))

        self.reportaBugAction.triggered.connect(partial(webbrowser.open, 'https://github.com/GijsGroote/creator_administrator/issues'))
        self.actionAbout.triggered.connect(self.openAboutDialog)
        self.searchJobsAction.triggered.connect(self.openSearchJobDialog)
        self.refreshJobsAction.triggered.connect(self.refreshAllWidgets)


        # shortcut to close the application
        QShortcut(QKeySequence('Ctrl+Q'), self).activated.connect(self.close)

    def checkHealth(self):
        ''' Check health with tracker file. '''
        self.job_tracker.checkHealth()
        self.refreshAllWidgets()
        if self.job_tracker.system_healthy:
            TimedMessage(self, self.gv, 'System Healthy 😊!')

    @abc.abstractmethod
    def openSearchJobDialog(self):
        ''' Open the search job dialog. '''

    def refreshAllWidgets(self):
        ''' Refresh the widgets. '''
        qlist_widgets = self.findChildren(QListWidget)
        for list_widget in qlist_widgets:
            list_widget.refresh()

    def openAboutDialog(self):
        ''' Open About Dialog. '''
        AboutDialog(self, self.gv).exec()
