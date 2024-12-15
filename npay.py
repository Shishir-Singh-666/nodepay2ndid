import requests as reqs
import asyncio
import time
import uuid
from curl_cffi import requests
from loguru import logger
from fake_useragent import UserAgent
from utils.banner import banner
from colorama import Fore, Style, init
from datetime import datetime

init()

PING_INTERVAL = 60
RETRIES = 60
TOKEN_FILE = 'tokens.txt'
PROXY_FILE = 'proxy.txt'
DOMAIN_API = {
    "SESSION": "http://api.nodepay.ai/api/auth/session",
    "PING": "https://nw.nodepay.org/api/network/ping",
    "DAILY_CLAIM": "https://api.nodepay.org/api/mission/complete-mission"
}

CONNECTION_STATES = {
    "CONNECTED": 1,
    "DISCONNECTED": 2,
    "NONE_CONNECTION": 3
}

status_connect = CONNECTION_STATES["NONE_CONNECTION"]
browser_id = None
account_info = {}
last_ping_time = {}

def uuidv4():
    return str(uuid.uuid4())

def show_banner():
    print(Fore.MAGENTA + banner + Style.RESET_ALL)

def show_copyright():
    print(Fore.MAGENTA + Style.BRIGHT + banner + Style.RESET_ALL)

def valid_resp(resp):
    if not resp or "code" not in resp or resp["code"] < 0:
        raise ValueError("Invalid response")
    return resp

def load_tokens_from_file(filename):
    try:
        with open(filename, 'r') as file:
            tokens = file.read().splitlines()
        return tokens
    except Exception as e:
        logger.error(f"Failed to load tokens: {e}")
        raise SystemExit("Exiting due to failure in loading tokens")

def load_proxies(proxy_file):
    try:
        with open(proxy_file, 'r') as file:
            proxies = file.read().splitlines()
        return proxies
    except Exception as e:
        logger.error(f"Failed to load proxies: {e}")
        raise SystemExit("Exiting due to failure in loading proxies")

def dailyclaim(token):
    url = DOMAIN_API["DAILY_CLAIM"]
    headers = {
        "Authorization": f"Bearer {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "Origin": "https://app.nodepay.ai",
        "Referer": "https://app.nodepay.ai/",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept": "*/*",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    data = {
        "mission_id": "1"
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
        if response.status_code != 200:
            log_message("Daily Claim FAILED, maybe it's already claimed?", Fore.RED)
            return False

        response_json = response.json()
        if response_json.get("success"):
            log_message("Daily Claim SUCCESSFUL", Fore.GREEN)
            return True
        else:
            log_message("Daily Claim FAILED, maybe it's already claimed?", Fore.RED)
            return False
    except Exception as e:
        log_message(f"Error in dailyclaim: {e}", Fore.RED)
        return False

def is_valid_proxy(proxy):
    return True

def load_session_info(proxy):
    return {}

def save_session_info(proxy, data):
    pass

def save_status(proxy, status):
    pass

def handle_logout(proxy):
    global status_connect, account_info
    status_connect = CONNECTION_STATES["NONE_CONNECTION"]
    account_info = {}
    save_status(proxy, None)
    log_message(f"Logged out and cleared session info for proxy {proxy}", Fore.RED)

async def start_ping(proxy, token):
    try:
        while True:
            await ping(proxy, token)
            await asyncio.sleep(PING_INTERVAL)
    except asyncio.CancelledError:
        log_message(f"Ping task for proxy {proxy} was cancelled", Fore.YELLOW)
    except Exception as e:
        log_message(f"Error in start_ping for proxy {proxy}: {e}", Fore.RED)

async def ping(proxy, token):
    global last_ping_time, RETRIES, status_connect

    current_time = time.time()

    if proxy in last_ping_time and (current_time - last_ping_time[proxy]) < PING_INTERVAL:
        log_message(f"Skipping ping for proxy {proxy}, not enough time elapsed", Fore.YELLOW)
        return

    last_ping_time[proxy] = current_time

    try:
        data = {
            "id": account_info.get("uid"),
            "browser_id": browser_id,
            "timestamp": int(time.time()),
            "version": "2.2.7"
        }

        response = await call_api(DOMAIN_API["PING"], data, proxy, token)
        if response["code"] == 0:
            log_message(f"Ping SUCCESSFUL for {proxy} - IP Score {response['data']['ip_score']}", Fore.GREEN)
            RETRIES = 0
            status_connect = CONNECTION_STATES["CONNECTED"]
        else:
            handle_ping_fail(proxy, response)
    except Exception as e:
        log_message(f"Ping failed via proxy {proxy}: {e}", Fore.RED)
        handle_ping_fail(proxy, None)

async def call_api(url, data, proxy, token):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Origin": "chrome-extension://lgmpfmgeabnnlemejacfljbmonaomfmm",
        "Accept": "*/*",
        "Accept-Language": "en-US,en;q=0.5",
    }

    try:
        response = requests.post(url, json=data, headers=headers, impersonate="safari15_5", proxies={
            "http": proxy, "https": proxy}, timeout=15)

        response.raise_for_status()
        return valid_resp(response.json())
    except Exception as e:
        log_message(f"Error during API call to {url} via proxy {proxy}: {e}", Fore.RED)
        raise ValueError(f"Failed API call to {url}")

async def render_profile_info(proxy, token):
    global browser_id, account_info

    try:
        np_session_info = load_session_info(proxy)

        if not np_session_info:
            browser_id = uuidv4()
            response = await call_api(DOMAIN_API["SESSION"], {}, proxy, token)
            valid_resp(response)
            account_info = response["data"]
            if account_info.get("uid"):
                save_session_info(proxy, account_info)
                await start_ping(proxy, token)
            else:
                handle_logout(proxy)
        else:
            account_info = np_session_info
            await start_ping(proxy, token)
    except Exception as e:
        log_message(f"Error in render_profile_info for proxy {proxy}: {e}", Fore.RED)
        error_message = str(e)
        if any(phrase in error_message for phrase in [
            "sent 1011 (internal error) keepalive ping timeout; no close frame received",
            "500 Internal Server Error"
        ]):
            log_message(f"Removing error proxy from the list: {proxy}", Fore.RED)
            remove_proxy_from_list(proxy)
            return None
        else:
            log_message(f"Connection error: {e}", Fore.RED)
            return proxy

async def main():
    all_proxies = load_proxies(PROXY_FILE)

    tokens = load_tokens_from_file(TOKEN_FILE)
    if not tokens:
        log_message("Token cannot be empty. Exiting the program.", Fore.RED)
        exit()
    if not all_proxies:
        log_message("Proxies cannot be empty. Exiting the program.", Fore.RED)
        exit()

    for token in tokens:
        log_message("Performing daily claim...", Fore.YELLOW)
        dailyclaim(token)

    while True:
        for token in tokens:
            active_proxies = [
                proxy for proxy in all_proxies if is_valid_proxy(proxy)][:100]
            tasks = {asyncio.create_task(render_profile_info(
                proxy, token)): proxy for proxy in active_proxies}

            done, pending = await asyncio.wait(tasks.keys(), return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                failed_proxy = tasks[task]
                if task.result() is None:
                    log_message(f"Removing and replacing failed proxy: {failed_proxy}", Fore.RED)
                    active_proxies.remove(failed_proxy)
                    if all_proxies:
                        new_proxy = all_proxies.pop(0)
                        if is_valid_proxy(new_proxy):
                            active_proxies.append(new_proxy)
                            new_task = asyncio.create_task(
                                render_profile_info(new_proxy, token))
                            tasks[new_task] = new_proxy
                tasks.pop(task)

            for proxy in set(active_proxies) - set(tasks.values()):
                new_task = asyncio.create_task(
                    render_profile_info(proxy, token))
                tasks[new_task] = proxy
            await asyncio.sleep(3)
    await asyncio.sleep(10)

def log_message(message, color):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(color + f"[{timestamp}] {message}" + Style.RESET_ALL)

if __name__ == '__main__':
    show_copyright()
    log_message("RUNNING WITH PROXIES", Fore.WHITE)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        log_message("Program terminated by user.", Fore.RED)
