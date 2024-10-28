import sys
import pytest
from printer.src.printer_app import PrinterMainApp, PrintMainWindow

# from creator_administrator.printer.src.printer_app import PrinterMainApp


@pytest.fixture(scope="module")
def app():
    """Fixture for creating a QApplication instance."""
    application = PrinterMainApp(sys.argv)
    yield application
    application.quit()

@pytest.fixture
def main_window(app):
    """Fixture for creating a main window instance."""
    window = PrintMainWindow()
    yield window
    window.close()


def test_initialization(main_window):
    """Test case to ensure main window initialization."""
    assert main_window is not None


# def test_click_buttons(main_window):
#     """Test selecting all sessions."""
#     hlayout = main_window.pushButtonHBoxLayout
#
#     for idx in range(hlayout.count()):
#         if widget := hlayout.itemAt(idx).widget():
#             widget.click()
