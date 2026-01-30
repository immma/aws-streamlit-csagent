# Attention
Please read this documentation correctly. Some folder structure may confuse you. 

`core` folder is contains `backend.py`. That is the core of the logic 🖖 

`simple` folder is for simple version chatbot application to understand how Streamlit and Strands work. So it's educational only.

`test` folder is for experiment only. That's all.

> This code was run on EC2 instance and use AmazonLinux2023

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
> ***Latest per 30 Jan 2026 🚀***  
The best version of customer agent app is in the `app-history` folder:  
`2app.py + agent_backend.py`


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

