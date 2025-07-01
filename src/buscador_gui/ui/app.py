import os
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

"""
Módulo que define a classe principal App da aplicação buscador_gui,
baseada em PySide6, além de utilitários para localizar recursos
compatíveis com execução via PyInstaller.
"""

def get_base_path():
    if getattr(sys, 'frozen', False):  # PyInstaller modo .exe
        return Path(sys._MEIPASS)
    else:
        return Path(__file__).resolve().parents[3]

def resource_path(relative_path):
    """Retorna o caminho absoluto para recursos, compatível com PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class App(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self.setApplicationName("Buscardor GUI")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("edwDev Inc.")
        self.setWindowIcon(QIcon(resource_path('resources/icons/icon_white.ico')))  # Ensure you have an icon at this path        

        self.run()

    def run(self):
        from buscador_gui.view.main_window import MainWindow
        main_window = MainWindow()
        main_window.show()
        return self.exec()