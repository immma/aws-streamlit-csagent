# Attention
Please read this documentation correctly. Some folder structure may confuse you. 

1. `app-history` folder is the most updated. To run this app only need 2 files:  
`1app.py + agent_backend.py`
or 
`2app.py + agent_backend.py`.  

`2app.py` offers more simple UI.

`backend-history-test.py` is the file to test your chat history based on session ID. 

*backend-history-test.py*: 
```
    ...
        session_manager=session_manager,
        system_prompt="You are a helpful AWS expert assistant."
    )

print(create_aws_agent('<put-your-session-here>').messages)
```

2. `core` folder is contains `backend.py`. That is the core of the logic 🖖 

3. `simple` folder is for simple version chatbot application to understand how Streamlit and Strands work. So it's educational only.

4. `test` folder is for experiment only. That's all.  

> **Note:⚠️**  
This code was run on `EC2 instance` and use `AmazonLinux2023`.  
Python version used is `Python 3.11`.  
This instance use instance role with sufficient `BedrockInvoke, S3Access, EC2Access`.

## 👌 In case you don't know - Python documentation for beginner
### Update python 3.11
```
sudo dnf update -y

sudo dnf search python3

sudo dnf install python3.11 -y

python3.11 --version

sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
```

### Deactivate last session of venv if exists  
Deactivate .venv (Python virtual environment)
```
deactivate
```

Delete .venv folder if needed
```
rm -rf .venv
```

Recreate or create .venv  
```
python3 -m venv .venv

source .venv/bin/activate
```
Download multiple library in one file.  
*Every python library need to be listed in `requirements.txt` file.*
```
pip install -r requirements.txt
```

Sneak into requirements.txt 
```
strands-agents
strands-agents-tools
bedrock-agentcore
boto3
streamlit
streamlit-authenticator
```

## BEST PRACTICE
> ***Latest per 31 Jan 2026 🚀***  
The best version of customer agent app is in the `app-history` folder:  
`1app.py + agent_backend.py`

#### New Features:  
* Delete chat history
* Pointer active chat
* Export full chat DB as JSON
* Export current chat as TXT


#### How to run the app?
```
streamlit run 2app.py
```
---
***UPDATE per 28 Jan 2026 👇***  
If you want to run with simple logic (folder: `simple`), you can use:  
`app.py + agent_backend.py`

But if you want to add some login mechanism, you can use:  
`login.py + agent_backend.py`

## Note
Everything in `test` folder is for experiment only. Some code contains error. Do your own risk. 😊

