from time import sleep
from requests import get, patch, Response
from os import getenv
from os.path import join, dirname, abspath, exists
from json import load
from dotenv import load_dotenv
from logging import basicConfig, getLogger, INFO, Logger, FileHandler, StreamHandler, Formatter
from random import shuffle

load_dotenv()


logger = getLogger(__name__)
logger.setLevel(INFO)

file_formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_formatter = Formatter('%(levelname)s - %(message)s')

file_handler = FileHandler('status_changer.log')
file_handler.setLevel(INFO)
file_handler.setFormatter(file_formatter)

console_handler = StreamHandler()
console_handler.setLevel(INFO)
console_handler.setFormatter(console_formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)

logger.propagate = False


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

    logger.info("Starting status change loop...")

    if not DC_TOKEN or DC_TOKEN == "<my_token>":
        logger.info("Please configure your DC_TOKEN in the .env file.")
        return

    json_path = join(dirname(abspath(__file__)), "statuses.json")
    if not exists(json_path):
        logger.error(f"statuses.json not found at {json_path}.")
        raise FileNotFoundError(f"statuses.json not found at {json_path}.")
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            LINES: list[str] = load(f)
    except Exception as e:
        logger.error(f"Error loading statuses.json: {e}.")
        raise Exception(f"Error loading statuses.json: {e}.")

    last_status: str = "offline"

    while True:
        shuffle(LINES)
        logger.info(f"Shuffled status messages: {LINES}")
        for line in LINES:
            status, status_code = check_user_status(DC_TOKEN)
            while status in ["offline", "invisible"]:
                if status != last_status:
                    last_status = status
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

            if status != last_status:
                logger.info(f"Status changed from '{last_status}' to '{status}'.")

            response = change_status(line, DC_TOKEN)
            if response is not None:
                if response.status_code == 200:
                    logger.info(f"Status changed to: {line}")
                elif response.status_code == 401:
                    logger.info("Unauthorized error when updating status. Stopping.")
                    return
                else:
                    logger.info(f"Failed to change status: {response.status_code} - {response.text}")

            last_status = status
            sleep(FREQUENCY)

if __name__ == "__main__":
    main()