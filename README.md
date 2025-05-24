

# How to run a Flask service using waitress, NSSM and ngrok

### ngrok
- Download ngrok: https://dashboard.ngrok.com/get-started/setup/windows
- Extract to a directory and open Command Prompt as adimistrator
- run ngrok to get a link. for example: ```ngrok http http://localhost:9090```
- Put this link in set_webhook.py file as ```DOMAIN``` 

### Waiters
- Install waitress: ```pip install waitress```

### NSSM - the Non-Sucking Service Manager
- Downlaod NSSM from: https://nssm.cc/download
- Extract it to ```C:\nssm```
- Run CMD as administrator
    - ```C:\nssm\win64```
    - ```nssm install MyFlaskBot``` (GUI will be opend)
        - Application path: Path to python.exe
            - For example: ```E:\FlaskApplication\Flask_Demo\env\Scripts\python.exe```
        - Startup directory: Folder containing app.py
            - For example: ```E:\FlaskApplication\Flask_Demo\```
        - Arguments: Path to your app.py
            - For example: ```E:\FlaskApplication\Flask_Demo\my_app.py```

    - nssm install MyFlaskBot
    - nssm restart MyFlaskBot

    To stop a service:
        - nssm stop MyFlaskBot

### To get a list of running services using nssm:
    - run powershell as administrator:
        - ```Get-WmiObject Win32_Service | Where-Object { $_.PathName -match "nssm.exe" } | Select-Object Name, DisplayName, State, StartMode, PathName
        ```
