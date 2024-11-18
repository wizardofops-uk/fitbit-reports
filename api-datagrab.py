#!/usr/bin/env python3

# Importing required libraries
import requests, argparse, json
from datetime import datetime, timedelta

# Define Functions
def get_access_token(client_id, redirect_uri):
  import secrets, base64, hashlib, webbrowser
  # Fitbit OAuth2 Application Specific URLs
  # Fitbit URLs
  auth_url = "https://www.fitbit.com/oauth2/authorize"
  token_url = "https://api.fitbit.com/oauth2/token"

  # Generate a code verifier and code challenge
  code_verifier = secrets.token_urlsafe(60)
  code_challenge = base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest()).decode("utf-8")[:-1]
  code_state = secrets.token_hex(16)

  # Redirect the user to the authorization URL
  auth_params = {
    "client_id": client_id,
    "redirect_uri": redirect_uri,
    "response_type": "code",
    "scope": "profile nutrition weight activity",
    "code_challenge_method": "S256",
    "code_challenge": code_challenge,
    "state": code_state
  }
  auth_response_url = requests.Request("GET", auth_url, params=auth_params).prepare().url
  webbrowser.open(auth_response_url)

  # User authenticates and is redirected back to your app with an authorization code
  # TEMP: Copy and paste the URL when prompted
  redirect_url = input("Redirect URL: ")
  authorization_code = redirect_url.split("code=")[1].split("state=")[0].strip("&&")
  # code_state_ret = redirect_url.split("code=")[1].split("state=")[1].strip("#_=_") # Unused

  # Exchange the authorization code for an access token
  token_params = {
    "client_id": client_id,
    "code": authorization_code,
    "code_verifier": code_verifier,
    "grant_type": "authorization_code",
    "redirect_uri": redirect_uri,
    "state": code_state
  }
  token_req = requests.Request("POST", token_url, data=token_params)
  token_prep = token_req.prepare()
  token_resp = requests.Session().send(token_prep)
  if token_resp.status_code == 200:
      access_token = token_resp.json().get("access_token")
  else:
      raise ConnectionError(f"Failed to obtain access token: {token_resp.status_code}")
  return access_token

def get_endpoint(access_token, url):
  headers = { 
    "Authorization": f"Bearer {access_token}"
  } 
  req = requests.Request("GET", url, headers)
  prep = req.prepare()
  print(prep.url)
  resp = requests.Session().send(prep)
  return resp.text

# Begin Execution
parser = argparse.ArgumentParser()
parser.add_argument("-t", "--token", help="A current access token")
parser.add_argument("-d", "--days", type=int, default=7, help="The number of days to show data for")
parser.add_argument("-u", "--user", default="-", help="the user ID of the user to report on")
parser.add_argument("-c", "--client-id", default="", help="the client ID of the Fitbit Application")
parser.add_argument("-r", "--redirect-uri", default="https://localhost", help="The redirect URI specified in the Fitbit Application")
args = parser.parse_args()

# Get today's date
today = datetime.now()
days_list = [(today - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(args.days)]

if not args.token:
  access_token = get_access_token(args.client_id, args.redirect_uri)
else:
  access_token = args.token

# Get Profile Data
profile = get_endpoint(access_token,f"https://api.fitbit.com/1/user/{args.user}/profile.json")
with open("dataset/api/profile.json", "w") as prof_f:
	prof_f.write(profile)
    
# Get Food Log Data
nutri_dict = {}
for date in days_list:
  nutri_day = get_endpoint(access_token,f"https://api.fitbit.com/1/user/{args.user}/foods/log/date/{date}.json")
  nutri_dict[date] = json.loads(nutri_day)
with open("dataset/api/nutrition.json", "w") as nutri_f:
	json.dump(nutri_dict, nutri_f)
   
# Get Water Log Data
water_dict = {}
for date in days_list:
  water_day = get_endpoint(access_token,f"https://api.fitbit.com/1/user/{args.user}/foods/log/water/date/{date}.json")
  water_dict[date] = json.loads(water_day)
with open("dataset/api/water.json", "w") as water_f:
	json.dump(water_dict, water_f)

# Get Weight Data
weight_dict = {}
for date in days_list:
  weight_day = get_endpoint(access_token,f"https://api.fitbit.com/1/user/{args.user}/body/log/weight/date/{date}.json")
  weight_dict[date] = json.loads(weight_day)
with open("dataset/api/weight.json", "w") as weight_f:
	json.dump(weight_dict, weight_f)
    
# Get Activity Data
activ_dict = {}
for date in days_list:
  activ_day =  get_endpoint(access_token,f"https://api.fitbit.com/1/user/{args.user}/activities/date/{date}.json")
  activ_dict[date] = json.loads(activ_day)
with open("dataset/api/activity.json", "w") as activ_f:
	json.dump(activ_dict, activ_f)