# Fitbit Reporting Tools
A collection of scripts to retrieve and report on data from the Fitbit API, requires a dev application to be registered, see the "Setting up an application" link below.

## Documentation
Swagger Docs
https://dev.fitbit.com/build/reference/web-api/explore/#/

OAuth Tutorial
https://dev.fitbit.com/build/reference/web-api/troubleshooting-guide/oauth2-tutorial/

## Setting up an application
A dev application with FitBit must be setup to this application to function, up-to-date tutorials can be found here:
https://dev.fitbit.com/build/reference/web-api/developer-guide/getting-started/

## Install dependancies
```
sudo apt update && upgrade
sudo apt install pip pipx wkhtmltopdf
pip install pandas matplotlib nbconvert PyPDF2 requests
```
## Install Dependancies for WSL
```
sudo add-apt-repository ppa:wslutilities/wslu
sudo apt update
sudo apt install wslu
```
## Grabbing the data
```
python3 ./api-datagrab.py --client-id MYCLIENTID --redirect-uri https://localhost --days 7 
```
The first run will require an interactive session for the user to log into Fitbit via the default browser
Subsequent runs can be ran with the access token that is returned
```
python3 ./api-datagrab.py --client-id MYCLIENTID --redirect-uri https://localhost --days 7 --token your_access_token
```