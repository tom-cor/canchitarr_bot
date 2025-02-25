To run the code:
1. Create .venv folder inside the prokect folder.
2. Read [this guide to setup and activate the virtual environment](https://docs.python.org/3/library/venv.html)
    - Pay close attention to the way you have to activate the virtual environment. It depends on the terminal you're using (Powershell, Bash, CMD, etc.)
    - If the virtual environment was correctly activated, you should see the command promt starting with a (.venv) like so:
        - PS: 
        ```
        (.venv) PS C:\current_working_directory>
        ```
        - Git Bash:
        ```
        (.venv)
        user@machine MINGW64 ~/current_working_directory (branch)`
        ```
3. With the virtual environment activated, run the following command:
```
pip install -r requirements.txt
```
4. Create the `secrets.json` file with the following contents:
```json
{
    "TELEGRAM_BOT_TOKEN": "input the token value"
}
```
5. Run the code!
6. If you happen to install new libraries, run the following command so that the requirements list gets updated:
```
pip freeze > requirements.txt
```