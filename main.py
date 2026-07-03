from time import sleep
from requests import get, patch, Response
from os import getenv
from os.path import join, dirname, abspath, exists
from json import load
from dotenv import load_dotenv
from logging import basicConfig, getLogger, INFO, Logger
from random import shuffle

load_dotenv()

basicConfig(level=INFO, filename='status_changer.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger: Logger = getLogger(__name__)

FREQUENCY_RAW: str | None = getenv('FREQUENCY')
if not FREQUENCY_RAW or FREQUENCY_RAW == "<frequency_in_seconds>":
    logger.error("FREQUENCY must be set in the .env file.")
    raise ValueError("FREQUENCY must be set in the .env file.")
if not FREQUENCY_RAW.isdigit() or int(FREQUENCY_RAW) <= 0:
    logger.error("FREQUENCY must be a positive integer.")
    raise ValueError("FREQUENCY must be a positive integer.")
FREQUENCY: int = int(FREQUENCY_RAW)

DC_TOKEN: str | None = getenv('DC_TOKEN')
if not DC_TOKEN:
    logger.error("DC_TOKEN must be set in the .env file.")
    raise ValueError("DC_TOKEN must be set in the .env file.")

API_URL: str = "https://discord.com/api/v8/users/@me/settings"

def load_status_messages() -> list[str]:
    json_path = join(dirname(abspath(__file__)), "statuses.json")
    if not exists(json_path):
        logger.error(f"statuses.json not found at {json_path}.")
        raise FileNotFoundError(f"statuses.json not found at {json_path}.")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            return load(f)
    except Exception as e:
        logger.error(f"Error loading statuses.json: {e}.")
        raise Exception(f"Error loading statuses.json: {e}.")

shuffled_lines: list[str] = []

def reshuffle() -> None:
    global shuffled_lines
    lines = load_status_messages()
    shuffled_lines = lines.copy()
    shuffle(shuffled_lines)

def check_user_status(token: str) -> tuple[str | None, int | None]:
    headers: dict[str, str] = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    try:
        response = get(API_URL, headers=headers)
        if response.status_code == 200:
            data: dict[str, str] = response.json()
            return data.get("status"), response.status_code
        return None, response.status_code
    except Exception as e:
        logger.error(f"Error checking status: {e}")
        return None, None

def change_status(message: str, token: str) -> Response | None:
    headers: dict[str, str] = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    data: dict[str, dict[str, str]] = {
        "custom_status": {
            "text": message
        }
    }
    try:
        response = patch(API_URL, headers=headers, json=data)
        return response
    except Exception as e:
        logger.error(f"Error changing status: {e}")
        return None

def main() -> None:
    global DC_TOKEN

    if not DC_TOKEN or DC_TOKEN == "<my_token>":
        logger.info("Please configure your DC_TOKEN in the .env file.")
        return

    while True:
        reshuffle()
        logger.info("Starting status change loop...")
        logger.info(f"Shuffled status messages: {shuffled_lines}")
        for line in shuffled_lines:
            status, status_code = check_user_status(DC_TOKEN)
            while status in ["offline", "invisible"]:
                logger.info(f"Current status is '{status}'. Waiting for it to change before updating...")
                sleep(FREQUENCY)
                status, status_code = check_user_status(DC_TOKEN)

            if status_code == 401:
                logger.info("Unauthorized: Your user token is invalid or has expired. You need to grab a new one from your browser.")
                return

            if status is None:
                logger.info("Could not retrieve user status. Sleeping before retry...")
                sleep(10)
                continue

            logger.info(f"Current user status: {status}")

            response = change_status(line, DC_TOKEN)
            if response is not None:
                if response.status_code == 200:
                    logger.info(f"Status changed to: {line}")
                elif response.status_code == 401:
                    logger.info("Unauthorized error when updating status. Stopping.")
                    return
                else:
                    logger.info(f"Failed to change status: {response.status_code} - {response.text}")

            sleep(FREQUENCY)

if __name__ == "__main__":
    main()