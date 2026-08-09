import os

from dotenv import load_dotenv


os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")


def main() -> None:
    load_dotenv()

    # Configure tracing before importing modules that use LlamaIndex.
    from app.observability import setup_observability

    setup_observability()

    from app.ui import run_app

    run_app()


if __name__ == "__main__":
    main()
