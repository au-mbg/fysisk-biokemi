import contextlib
import datetime
import io
import json
import locale
import os
import pathlib
import re
import subprocess
import urllib
import warnings

import IPython
import IPython.display
import ipywidgets
import nbformat
import requests
import werkzeug.utils
import yaml


def _install_dependencies():
    """Install required system dependencies for PDF conversion."""
    # Check if rsvg-convert (from librsvg2-bin) is available
    result = subprocess.run('which rsvg-convert', shell=True, capture_output=True)
    if result.returncode != 0:
        print("📦 Installing librsvg2-bin...")
        subprocess.run(
            'apt-get install -yqq --no-install-recommends librsvg2-bin>/dev/null',
            shell=True,
            check=False
        )
    
    
    if not pathlib.Path('/usr/local/bin/quarto').exists():
        print("📦 Installing Quarto...")
        subprocess.run(
            "wget -q 'https://quarto.org/download/latest/quarto-linux-amd64.deb' && "
            "dpkg -i quarto-linux-amd64.deb>/dev/null && "
            "rm quarto-linux-amd64.deb",
            shell=True,
            check=True
        )
        print("✅ Installation complete!")


def colab2pdf():
    """Convert current Colab notebook to PDF and download it."""
    # Check if running in Colab
    try:
        import google.colab
    except ImportError:
        print("⚠️  This function is only available in Google Colab environments.")
        return None
    
    print("🚀 Starting PDF conversion...")
    _install_dependencies()
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    warnings.filterwarnings('ignore', category=nbformat.validator.MissingIDFieldWarning)
    IPython.get_ipython().run_line_magic('matplotlib', 'inline')
    
    # Get notebook name
    print("📓 Retrieving notebook...")
    n = pathlib.Path(werkzeug.utils.secure_filename(urllib.parse.unquote(
        requests.get(f'http://{os.environ["COLAB_JUPYTER_IP"]}:{os.environ["KMP_TARGET_PORT"]}/api/sessions').json()[0]['name']
    )))
    
    # Create output directory
    p = pathlib.Path('/content/pdfs') / f'{datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")}_{n.stem}'
    p.mkdir(parents=True, exist_ok=True)
    
    # Get notebook content
    nb = nbformat.reads(
        json.dumps(google.colab._message.blocking_request('get_ipynb', timeout_sec=600)['ipynb']), 
        as_version=4
    )
    
    # Validate image URLs
    print("🔍 Validating images...")
    u = [
        u for c in nb.cells 
        if c.get('cell_type') == 'markdown' 
        for u in re.findall(r'!\[.*?\]\((https?://.*?)\)', c['source']) 
        if requests.head(u, timeout=5).status_code != 200
    ]
    if u:
        raise Exception(f"Bad Image URLs: {','.join(u)}")
    
    # Remove Colab2PDF cells and prepare notebook
    print("📝 Preparing notebook...")
    nb.cells = [cell for cell in nb.cells if '--Colab2PDF' not in cell.source]
    nb = nbformat.v4.new_notebook(cells=nb.cells or [nbformat.v4.new_code_cell('#')])
    nbformat.validator.normalize(nb)
    
    # Write notebook
    nbformat.write(nb, (p / f'{n.stem}.ipynb').open('w', encoding='utf-8'))
    
    # Render to PDF
    print("🔨 Rendering PDF with Typst...")
    subprocess.run(
        f'quarto render {p}/{n.stem}.ipynb --to typst '  
        f'-M margin={{top=1in,bottom=1in,left=1in,right=1in}} --quiet',
        shell=True,
        check=True
    )
    
    # Download PDF
    print("⬇️  Downloading PDF...")
    google.colab.files.download(str(p / f'{n.stem}.pdf'))
    print(f"✅ Done! PDF saved as: {n.stem}.pdf")
    
    return str(p / f'{n.stem}.pdf')


def colab2pdf_widget():
    """Display an interactive widget to convert and download the current notebook as PDF."""
    # @title Download Notebook in PDF Format{display-mode:'form'}
    
    def convert(b):
        try:
            s.value = '🔄 Converting'
            b.disabled = True
            pdf_path = colab2pdf()
            s.value = f'✅ Downloaded: {pathlib.Path(pdf_path).name}'
        except Exception as e:
            s.value = f'❌ {str(e)}'
        finally:
            b.disabled = False
    
    b = ipywidgets.widgets.Button(description='⬇️ Download')
    s = ipywidgets.widgets.Label()
    b.on_click(lambda b: convert(b))
    IPython.display.display(ipywidgets.widgets.HBox([b, s]))
