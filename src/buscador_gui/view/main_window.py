import os
import subprocess
import configparser
from pathlib import Path
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QFileDialog
)
from PySide6.QtGui import QDesktopServices
from PySide6.QtCore import QUrl

"""Função temporária para que eu possa executar alguns testes
"""
def config_text_edit(CONFIG_PATH, config, layout_central):
    text_edit = QTextEdit()
    if CONFIG_PATH.exists():
        path = str(CONFIG_PATH)
        config.read(CONFIG_PATH)
        if 'App' in config:
            ultima_pasta = config['App']['ultima_pasta']
            text_edit.setText(f'{path}\n{ultima_pasta}')
    layout_central.addWidget(text_edit)       

class Project:
    def __init__(self, name, path, summary):
        self.name = name
        self.path = path
        self.summary = summary

    def __str__(self):
        return f'{self.name}\n{self.summary}' if self.summary else self.name

def load_projects2(path: Path, padrao='README.md', ingorar={'.venv', '__pycache__', '.git', 'dist', 'build', 'resources'}):
    projects = []
    readmes = [
        d for d in path.rglob(padrao)
        if not any(part.lower() in ingorar for part in d.parts)
    ]

    for readme in readmes:
        path = readme.parent
        project_name = readme.parent.name
        summary = ''
        with readme.open(encoding='utf-8') as f:
            for i in range(5):
                linha = f.readline()
                if not linha:
                    break
                summary += f'\n{linha.strip()}'    

        projects.append(Project(project_name, path, summary))

    return projects

def load_projects(base_directory: Path):
    projects = []
    for dir in base_directory.iterdir():
        if dir.is_dir():
            readme = dir / 'README.md'
            summary = ''
            if readme.exists():
                with readme.open(encoding='utf-8') as f:
                    summary = ''.join(f.readlines()[:5]).strip()
            projects.append(Project(dir.name, str(dir.resolve()), summary))
    return projects

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Buscador GUI')
        self.setMinimumSize(1000, 600)

        # Define o path para o config.ini no diretório APPDATA do usuário
        app_data_path = Path(os.getenv('APPDATA')) if os.name == 'nt' else Path.home() / '.config'
        self.app_config_dir = app_data_path / 'BuscadorDeProjetos'
        self.app_config_dir.mkdir(parents=True, exist_ok=True)
        self.CONFIG_PATH = self.app_config_dir / 'config.ini'
        self.config = configparser.ConfigParser()

        self.projects = []
        self.base_directory = None
        self.selected_path = None

        self.init_ui()
        self.select_initial_directory()
    
    def init_ui(self):
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout_central = QVBoxLayout(central_widget)

        """ Esta parte só existe para teste da função temporária
        """
        # config_text_edit(self.CONFIG_PATH, self.config, layout_central)

        self.label_directory = QLabel('📁 Diretório atual:')
        self.label_busca = QLabel('🔎 Busca por nome ou conteúdo do README:')

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('🔎Informe o termo de pesquisa e pressione Enter para buscar...')
        self.search_input.returnPressed.connect(self.filter_projects)

        self.list_widget = QListWidget()
        self.list_widget.itemClicked.connect(self.update_selected_path)
        self.list_widget.itemDoubleClicked.connect(self.open_project_in_explorer)

        #%% buttons upper
        buttons_list_and_directory = QHBoxLayout()
        
        self.list_button = QPushButton('🔁 Listar todos')
        self.list_button.clicked.connect(self.list_all)

        self.directory_button = QPushButton('📂 Selecionar outra pasta')
        self.directory_button.clicked.connect(self.select_new_directory)

        buttons_list_and_directory.addWidget(self.list_button)
        buttons_list_and_directory.addWidget(self.directory_button)

        #%% button down
        buttons_explorer_and_vscode = QHBoxLayout()

        self.explorer_button = QPushButton('🗂️ Abrir no Explorer')
        self.explorer_button.clicked.connect(self.open_project_in_explorer)
        self.explorer_button.setEnabled(False)

        self.vscode_button = QPushButton('🧠 Abrir no VSConde')
        self.vscode_button.clicked.connect(self.open_project_in_vscode)
        self.vscode_button.setEnabled(False)

        buttons_explorer_and_vscode.addWidget(self.explorer_button)
        buttons_explorer_and_vscode.addWidget(self.vscode_button)


        #%% add widgets and layouts 
        layout_central.addWidget(self.label_directory)
        layout_central.addWidget(self.label_busca)
        layout_central.addWidget(self.search_input)
        layout_central.addWidget(self.list_widget)
        layout_central.addLayout(buttons_list_and_directory)
        layout_central.addLayout(buttons_explorer_and_vscode)

    def select_initial_directory(self):
        if self.CONFIG_PATH.exists():
            self.config.read(self.CONFIG_PATH)
            saved_path = self.config.get("App", "ultima_pasta", fallback=None)
            if saved_path and Path(saved_path).exists():
                self.base_directory = Path(saved_path)
                self.update_projects()
                return
            
        self.select_new_directory()

    def select_new_directory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Selecione a nova pasta de projetos')
        if directory:
            self.base_directory = Path(directory)
            self.config['App'] = {'ultima_pasta': str(self.base_directory)}
            with open(self.CONFIG_PATH, 'w') as configfile:
                self.config.write(configfile)
            self.update_projects()
        else:
            if not self.base_directory:
                QMessageBox.warning(self, 'Aviso', 'Nenhum diretório foi selecionado. O programa será encerrado.')

    def update_projects(self):
        self.projects = load_projects2(self.base_directory)
        self.label_directory.setText(f'📁 Diretório atual: {self.base_directory}')
        self.list_all()
        self.selected_path = None
        self.explorer_button.setEnabled(False)
        self.vscode_button.setEnabled(False)
        
    def list_all(self):
        self.list_widget.clear()
        for p in self.projects:
            item = QListWidgetItem(str(p))
            item.setData(32, p.path)
            self.list_widget.addItem(item)

    def filter_projects(self):
        search_term = self.search_input.text().lower()
        self.list_widget.clear()

        for p in self.projects:
            if search_term in p.name.lower() or search_term in p.summary.lower():
                item = QListWidgetItem(str(p))
                item.setData(32, p.path)
                self.list_widget.addItem(item)

        if self.list_widget.count() == 0:
            QMessageBox.information(self, 'Nada encontrado', 'Nenhum projeto corresponde à busca.')                            

    def update_selected_path(self, item):
        self.selected_path = item.data(32)
        self.explorer_button.setEnabled(True)
        self.vscode_button.setEnabled(True)

    def open_project_in_explorer(self, item=None):
        if not self.selected_path:
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.selected_path))

    def open_project_in_vscode(self):
        if not self.selected_path:
            return
        try:
            subprocess.run(f'code "{self.selected_path}"', shell=True, check=True)
        except FileNotFoundError:
            QMessageBox.critical(self, "Erro", "VSCode não encontrado no PATH. Verifique se o comando \'code\' está disponível")
        except subprocess.CalledProcessError:
            QMessageBox.critical(self, "Erro", "Erro ao tentar abrir o VSCode.")
