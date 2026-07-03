# Discord Custom Status Changer (Experimental)

A lightweight Python script to periodically update your Discord custom status.

> [!WARNING]
> **Use at your own risk.** Automated user accounts (self-botting) are a direct violation of [Discord's Terms of Service](https://discord.com/terms). Using this script can result in your Discord account being permanently banned.

## Disclaimer
This repository is for educational and research purposes only. The author takes no responsibility for any consequences, including account suspension, data loss, or other actions taken by Discord, arising from the use of this software.

## How It Works
The script runs an infinite loop that:
1. Verifies if you are currently online (active, idle, or Do Not Disturb) on Discord by making a `GET` request. If you are offline or invisible, it skips updating to keep the activity natural.
2. Rotates through a pre-configured list of status messages using `PATCH` requests to the Discord settings API.
3. Automatically halts execution if it encounters a `401 Unauthorized` response (indicating the token is no longer valid).

---

## Installation & Setup Tutorial

### Prerequisites
* **Python 3.x** installed.
* A Discord user token (retrieved from your browser's Local Storage).

### 1. Clone & Navigate to the Project
```bash
git clone https://github.com/fofola1/Discord-Custom-Status-Changer.git
cd Discord-Custom-Status-Changer
```

### 2. Install Dependencies
Install the required libraries using pip:
```bash
pip install -r requirements.txt
```

### 3. Configure the Environment
Create a file named `.env` in the root directory, you can use `example.env` as a template:
```bash
mv example.env .env
```
Open `.env` in a text editor and add your token and set the frequency (in seconds) for status updates:
```env
DC_TOKEN=your_actual_token_here
FREQUENCY=300
```
Open `statuses.json` and add your desired status messages in a JSON array format:
```json
[
    "My custom status 1",
    "My custom status 2",
    "My custom status 3"
]
```

> [!IMPORTANT]
> **How to get your token:**
> 1. Open Discord in your web browser (e.g., Chrome, Firefox).
> 2. Open Developer Tools (`F12` or `Ctrl + Shift + I`).
> 3. Go to the **Application** (Chrome) or **Storage** (Firefox) tab.
> 4. Expand **Local Storage** -> `https://discord.com`.
> 5. Look for the key named `token` and copy the value (without quotes).

---

## Running the Application

### Running Interactively
To start the script directly in your terminal:
```bash
python3 main.py
```

### Running Detached on a Server (Tmux)
To keep the script running in the background after closing your console:

1. **Start a new session**:
   ```bash
   tmux new -s discord-status
   ```
2. **Run the script**:
   ```bash
   python3 main.py
   ```
3. **Detach** by pressing `Ctrl + B`, then releasing and pressing `D`.
4. **Reattach** to view or control the process later:
   ```bash
   tmux attach -t discord-status
   ```
