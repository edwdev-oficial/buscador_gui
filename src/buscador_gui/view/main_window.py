import os
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit
)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Buscador GUI')
        self.setMinimumSize(1000, 600)

        # Define o caminho para o config.ini no diretório APPDATA do usuário
        app_data_path = Path(os.getenv('APPDATA')) if os.name == 'nt' else Path.home() / '.config'
        self.app_config_dir = app_data_path / 'BuscadorDeProjetos'
        self.app_config_dir.mkdir(parents=True, exist_ok=True)
        self.CONFIG_PATH = self.app_config_dir / 'config.ini'

        self.config = configparser.ConfigParser()

        self.setup_ui()
        # self.selecionar_diretorio_inicial()
    
    def setup_ui(self):
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_central = QVBoxLayout(central_widget)

        result = str(self.CONFIG_PATH)

        text_edit = QTextEdit()
        text_edit.setText(result)


        if self.CONFIG_PATH.exists():
            self.config.read(self.CONFIG_PATH)

            if 'App' in self.config:
                ultima_pasta = self.config['App']['ultima_pasta']
                print(ultima_pasta)
                text_edit.setText(f'{result}\n{ultima_pasta}')

        layout_central.addWidget(text_edit)
