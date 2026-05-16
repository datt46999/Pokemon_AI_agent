import logging
import os
import sys
import time
import shutil
import subprocess

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_cmd(cmd, cwd=None, check=True):
    logger.info("Running: %s", " ".join(cmd))
    # Use shell=True on Windows ONLY if it's not a direct executable (like npm.cmd)
    # But for safety and simplicity with npm, shell=True is reliable on Windows.
    subprocess.run(cmd, cwd=cwd, check=check, shell=False)


def setup():
    # Setup Server
    if not os.path.exists("server"):
        logger.info("Setup: Cloning Pokémon Showdown Server...")
        run_cmd(
            ["git", "clone", "https://github.com/smogon/pokemon-showdown.git", "server"]
        )

    if not os.path.exists("server/node_modules"):
        logger.info("Setup: Installing Server Dependencies...")
        run_cmd(["npm", "install"], cwd="server")

    if not os.path.exists("server/config/config.js"):
        shutil.copy("server/config/config-example.js", "server/config/config.js")

    # Setup Client
    if not os.path.exists("client"):
        logger.info("Setup: Cloning Pokémon Showdown Client...")
        run_cmd(
            [
                "git",
                "clone",
                "https://github.com/smogon/pokemon-showdown-client.git",
                "client",
            ]
        )

    if not os.path.exists("client/node_modules"):
        logger.info("Setup: Installing Client Dependencies...")
        # Client install sometimes warns/errors but still works, so check=False
        run_cmd(["npm", "install"], cwd="client", check=False)

    if not os.path.exists("client/config/config.js"):
        shutil.copy("client/config/config-example.js", "client/config/config.js")

    # Build client if battle.js doesn't exist
    if not os.path.exists("client/play.pokemonshowdown.com/js/battle.js"):
        logger.info("Setup: Building Client...")
        run_cmd(["node", "build"], cwd="client", check=False)


def main():
    logger.info("==========================================")
    logger.info("      Pokémon AI Agent Local Startup      ")
    logger.info("==========================================")

    setup()

    logger.info("Starting Pokémon Showdown Server...")
    # Start server in background. No shell=True so we can easily terminate it.
    server_process = subprocess.Popen(
        ["node", "pokemon-showdown", "start", "--no-security"], cwd="server"
    )

    time.sleep(3)  # Give server a moment to start

    logger.info("Starting Gradio App...")
    os.environ["PYTHONUNBUFFERED"] = "1"

    try:
        # We run it directly in the same process
        import app

        gradio_app, custom_css, elite_theme = app.main_app()
        gradio_app.launch(
            server_name="127.0.0.1",
            server_port=7860,
            share=True,
            css=custom_css,
            theme=elite_theme,
        )
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    finally:
        logger.info("Terminating Showdown Server...")
        server_process.terminate()
        server_process.wait()


if __name__ == "__main__":
    main()