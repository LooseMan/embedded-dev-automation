import logging
import subprocess

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

logger = logging.getLogger(__name__)


def write_log(api, phase, result, message):

    text = f"{api} {phase} {result} {message}"

    logger.info(text)

    # sql = f"""
    # INSERT INTO api_log(api_name, phase, result, message)
    # VALUES('{api}','{phase}','{result}','{message}');
    # """

    # subprocess.run(
    #     [
    #         "psql",
    #         "-U", "postgres",
    #         "-d", "device",
    #         "-c", sql
    #     ],
    #     check=False
    # )