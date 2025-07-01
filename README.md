# Para empacotar o programa e criar o executável e instalador .msi

### Se estiver usando poetry
#### 📌 Passo 1: Instale o PyInstaller dentro do ambiente Poetry
```bash
poetry add --group dev pyinstaller
```
#### 📌 Passo 2: Rode o PyInstaller com o Poetry
Normalmente poderia ser executado algo como:
```bash
poetry run pyinstaller --noconsole --onefile --icon=icon_white.ico --add-data "icon_white.ico;." buscador_gui.py

```
Mas como seu main.py está em src/buscador_gui/main.py, e os ícones estão em resources/icons/, você pode rodar:
```bash
poetry run pyinstaller src/buscador_gui/main.py --name buscador_gui --icon=resources/icons/icone.ico --noconfirm --onefile --noconsole --add-data "resources/icons;resources/icons" --paths=src
```

🧠 Dica: automatize com script no pyproject.toml
Você pode adicionar um script personalizado no pyproject.toml:
```toml
[tool.poetry.scripts]
build-exe = "buscador_gui:build_exe"
```
E no seu buscador_gui.py, crie essa função:
```python
def build_exe():
    import subprocess
    subprocess.run([
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--icon=icone.ico",
        "buscador_gui.py"
    ])
```
Aí você roda assim:
```bash
poetry run build-exe
```

Depois que criar o arquivo 📄 installer.wxs

Rodar
```bash
candle installer.wxs
```
e
```bash
light installer.wixobj -o buscador_instalador.msi
```
## ⚠️ Atenção
Este processo gera o arquivo .msi e o arquivo cab1.cab
É possível criar um .msi "auto-contido" (single-file installer) que não precisa de .cab
VERIFICAR

# Continuando

🎯 Perfeito! Agora é transformar o instalador .msi em um auto-contido (self-contained) — ou seja, tudo compactado dentro de um único arquivo .msi, sem necessidade de um .cab externo como o cab1.cab.

## ✅ Etapas para gerar um .msi único com WiX Toolset

### 📁 Estrutura atual (exemplo)
```txt
installer.wxs
dist/
  buscador_gui5.exe
icon_white.ico
```
## 🛠️ Passo 1 – Atualize o installer.wxs (caso necessário)
Se seu .wxs já estiver funcionando corretamente, não é necessário modificar.
Mas, para garantir que o .cab seja embutido no .msi, é essencial garantir:
```xml
<MediaTemplate EmbedCab="yes" />
```
⚠️ No seu caso, basta alterar esta linha:
```xml
<MediaTemplate />
```
🔁 Para esta:
```xml
<MediaTemplate EmbedCab="yes" />
```
## 🛠️ Passo 2 – Compile usando candle e light com opção correta
Execute os comandos a seguir no terminal, na pasta onde está o .wxs:
```bash
candle installer.wxs
light installer.wixobj -o buscador_instalador.msi
```
🔹 Como já está com EmbedCab="yes", o light irá embutir tudo no .msi.

## 📦 Resultado
Você terá somente:
```txt
buscador_instalador.msi
```
📌 Esse arquivo agora pode ser distribuído sozinho. Ao rodar em qualquer máquina (incluindo VMs sem Python), ele instalará corretamente.
