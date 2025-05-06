

# How to run a Flask service using waitress and NSSM

- Install waitress: ```pip install waitress```
- Downlaod NSSM from: https://nssm.cc/download
- Extract it to ```C:\nssm```
- Open CMD as administrator
    - ```cd C:\nssm```
    - ```nssm install MyFlaskBot``` (GUI will be opend)
        - Application path: Path to python.exe
            - For example: ```E:\FlaskApplication\Flask_Demo\env\Scripts\python.exe```
        - Startup directory: Folder containing app.py
            - For example: ```E:\FlaskApplication\Flask_Demo\```
        - Arguments: Path to your app.py
            - For example: ```E:\FlaskApplication\Flask_Demo\my_app.py```

    - nssm install MyFlaskBot
    - nssm restart MyFlaskBot