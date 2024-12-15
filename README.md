# NODEPAY FARMING USING PROXIES
- Daily Claim
- Multi Account Keep-Alive Support.

# [GET RESIDENTIAL PROXIES FROM HERE](https://proxy-sale.com/?partner_link=k1Vs6WMuON)

# NOTE

- **Paste your proxies inside ```proxy.txt``` and the token inside ```tokens.txt```**
- **To use multiple accounts, in which case one proxy from each line will be assigned to one token in each line (1 token = 1 proxy), paste all your tokens in the ```token.txt``` file and make sure there are matching number of proxies in the ```proxy.txt``` file.**

# PC (WINDOWS)
## How to Get Nodepay Token -

1. Open your browser and login to the NODEPAY dashboard.
2. Press `F12` to open the **Inspect Elements** panel.
3. Go to the **Console** tab and paste the following code:
```
localStorage.getItem('np_webapp_token') 
```

4. You will receive your user ID, which looks like this: `"eyJhbG........"`
5. If you can't paste, type `allow pasting` and press Enter.

## Recommended Python Version

It is recommended to use **Python 3.10**.  
[Download Python 3.10 here](https://www.python.org/downloads/release/python-3100/).

## Install Requirements

Run the following command to install the necessary packages:

```
pip install -r requirements.txt
```

## Running the Script

```
python npay.py
```
# FOR ANDROID

## How to Get NODEPAY User ID Using Android Device

1. Download and install [Kiwi Browser](https://play.google.com/store/apps/details?id=com.kiwibrowser.browser&hl=en).
2. Login to the NODEPAY web and go to the dashboard.
3. Open the **Developer Tools** in the Kiwi browser.
4. Go to the **Console** tab and paste this code:
```
localStorage.getItem('np_webapp_token') 
```

5. If you can't paste, type `allow pasting` and press Enter, then paste the line above.

## Configure Termux

After installing Termux, ensure you have allowed storage permission for Termux (device app) settings.  
Alternatively, run this command in Termux and give it storage permission:

```
termux-setup-storage
```

## Install Python 3.10

Run the following commands:

```
pkg update && upgrade
```
```
pkg install tur-repo
```
```
pkg install python-is-python3.10
```
```
pkg install -y rust binutils
```
```
CARGO_BUILD_TARGET="$(rustc -Vv | grep "host" | awk '{print $2}')" pip install maturin
```

## Clone This Script
```
pkg install git
```
```
git clone https://github.com/Mittyadav/nodepaybot.git
```
## Install Requirements
```
pip3.10 install -r requirements.txt
```
## Put your token(s) inside ```token.txt``` file and proxies inside ```proxy.txt``` file
```
pkg install nano
```
```
nano tokens.txt
```
```
nano proxy.txt
```
## Download this [FILE](https://github.com/ylasgamers/nodepay/raw/refs/heads/main/libcurl-impersonate-chrome.so.4) and put it inside - "/data/data/com.termux/files/usr/lib"
Example Command - ```cp libcurl-impersonate-chrome.so.4 /data/data/com.termux/files/usr/lib```
## Run the Script
```
python npay.py
```
