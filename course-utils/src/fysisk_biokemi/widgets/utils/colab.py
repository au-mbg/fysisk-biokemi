# Context Manager for Colab
from contextlib import contextmanager

def enable_custom_widget_colab():
    try:  # For bedre brug af widgets i Google Colab.
        from google.colab import output

        output.enable_custom_widget_manager()
    except ImportError:
        pass


def disable_custom_widget_colab():
    try:  # For bedre brug af widgets i Google Colab.
        from google.colab import output

        output.disable_custom_widget_manager()
    except ImportError:
        pass

@contextmanager
def colab_context():
    enable_custom_widget_colab()
    try:
        yield
    finally:
        disable_custom_widget_colab()
