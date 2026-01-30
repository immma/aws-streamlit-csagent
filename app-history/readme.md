## Update python 3.11
`sudo dnf update -y`

`sudo dnf search python3`

`sudo dnf install python3.11 -y`

`python3.11 --version`

`sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1`

### Deactivate last session of venv if exists  
`deactivate`

Delete .venv folder  
`rm -rf .venv`

Recreate .venv  
`python3 -m venv .venv`

`source .venv/bin/activate`

Download multiple library in one file
`pip install -r requirements.txt`

## BEST PRACTICE
Latest per 30 Jan 2026
The best version of customer agent app is in the `app-history` folder:
`2app.py + agent_backend.py`

If you want to run with simple term, you can use:  
`app.py + agent_backend.py`

But if you want to add some login mechanism, you can use:  
`login.py + agent_backend.py`

# Note
Chat with history is not perfect yet, anyway if you still insist to test, you can use:  
`login-chat-history.py + agent_backend.py`  
They would create .json file as db to store history. 