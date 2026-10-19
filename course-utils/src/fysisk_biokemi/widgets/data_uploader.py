import ipywidgets as widgets
from IPython.display import display
from pathlib import Path
import io

import pandas as pd
from dataclasses import dataclass
from fysisk_biokemi.widgets.utils.colab import disable_custom_widget_colab

@dataclass
class Reader:
    func: callable
    description: str
    name: str


SUFFIX_TO_FUNC = {
    '.csv': Reader(func=pd.read_csv, description='Comma-separated values', name='pd.read_csv'),
    '.xlsx': Reader(func=pd.read_excel, description='Excel spreadsheet', name='pd.read_excel'),
    '.xls': Reader(func=pd.read_excel, description='Excel spreadsheet', name='pd.read_excel'),
    '.txt': Reader(func=pd.read_csv, description='Text file', name='pd.read_csv'),
}


class DataUploader:

    def __init__(self):
        disable_custom_widget_colab()
        self.uploader = widgets.FileUpload(accept='', multiple=False)
        self.uploader.observe(self._on_upload_change, names='value')
        self.output = widgets.Output()

    def _on_upload_change(self, change):
    
        self.output.clear_output()

        uploaded = self.uploader.value

        if not uploaded:
            return

        # Support older and newer ipywidgets upload formats
        if isinstance(uploaded, dict):
            files = uploaded.items()
        else:
            files = (
                (file_info["name"], file_info)
                for file_info in uploaded
            )

        for filename, file_info in files:
            content = file_info["content"]

            # Convert the content to bytes if needed
            if hasattr(content, "tobytes"):
                content = content.tobytes()

            with self.output:
                print(f"Uploaded file: {filename}")
                print(f"File extension: {Path(filename).suffix}")

                suffix = Path(filename).suffix.lower()

                if suffix in SUFFIX_TO_FUNC:
                    print("Using function:", SUFFIX_TO_FUNC[suffix].name)

                    content = io.BytesIO(content)
                    self.df = SUFFIX_TO_FUNC[suffix].func(content)

                    print("DataFrame shape:", self.df.shape)
                else:
                    print(f"Unsupported file extension: {suffix}")



    def get_dataframe(self):
        if hasattr(self, 'df'):
            return self.df
        else:
            raise ValueError("No file has been uploaded yet.")


    def display(self):
        display(self.uploader, self.output)


    


