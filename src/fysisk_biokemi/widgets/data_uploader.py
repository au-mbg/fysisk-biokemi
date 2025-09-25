import ipywidgets as widgets
from IPython.display import display
from pathlib import Path
import io

import pandas as pd
from dataclasses import dataclass

@dataclass
class Reader:
    func: callable
    description: str
    name: str


SUFFIX_TO_FUNC = {
    '.csv': Reader(func=pd.read_csv, description='Comma-separated values', name='pd.read_csv'),
    '.xlsx': Reader(func=pd.read_excel, description='Excel spreadsheet', name='pd.read_excel'),
    '.xls': Reader(func=pd.read_excel, description='Excel spreadsheet', name='pd.read_excel'),
}


class DataUploader:

    def __init__(self):
        self.uploader = widgets.FileUpload(accept='', multiple=False)

        self.uploader.observe(self._on_upload_change, names='value')
        self.output = widgets.Output()

    def _on_upload_change(self, change):
        self.output.clear_output()
        for filename, file_info in self.uploader.value.items():
            content = file_info['content']
            with self.output:
                print(f"Uploaded file: {filename}")
                print(f"File extension: {Path(filename).suffix}")
                # Here you can add code to process the file content as needed
                suffix = Path(filename).suffix
                if suffix in SUFFIX_TO_FUNC:
                    print("Using function:", SUFFIX_TO_FUNC[suffix].name)
                    content = io.BytesIO(content)
                    self.df = SUFFIX_TO_FUNC[suffix].func(content)
                    print("DataFrame shape:", self.df.shape)

    def get_dataframe(self):
        if hasattr(self, 'df'):
            return self.df
        else:
            raise ValueError("No file has been uploaded yet.")


    def display(self):
        display(self.uploader, self.output)


    


