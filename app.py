import gradio as gr
from dotenv import load_dotenv

from src.auth.youtube_auth import get_credentials
from src.logger import setup_logger
from src.ui.app import create_ui

logger = setup_logger(__name__)


def main():
    load_dotenv()

    creds = get_credentials()
    if creds is None:
        logger.warning(
            "YouTube not authenticated. Run 'python setup_oauth.py' first."
        )
    else:
        logger.info("YouTube authentication valid.")

    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
