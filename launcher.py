import os
import sys

from streamlit.web.cli import main


def resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    print("Current working directory:", os.getcwd())
    if getattr(sys, 'frozen', False):
        os.environ['STREAMLIT_SERVER_PORT'] = '8501'
        os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
        sys.argv = [
            "streamlit",
            "run",
            resource_path("app/Home.py"),
            "--global.developmentMode=false",
            "--server.enableStaticServing=true"
        ]
    else:
        sys.argv = ["streamlit", "run", "app/Home.py"]

    main()
