from bs4 import BeautifulSoup as bs
import requests
import json

HOMEPAGE = "https://familyportal.renweb.com/school/index"
url = "https://accounts.renweb.com/Account/Login"
session = requests.session()

with open('config.json') as file:
    config = json.load(file)

print("Logging in to Renweb...", end="")

response = session.get(url)
soup = bs(response.content, "html.parser")
token = soup.find("input", {"name": "__RequestVerificationToken"})["value"]

payload = {
    "District": config['District'],
    "Username": config['Username'],
    "Password": config['Password'],
    "signIn": "LOG IN",
    "__RequestVerificationToken": token}

response = session.post(response.url, data=payload)
if not response.status_code == 200:
    raise Exception(f"Failed to POST to {url} with code {response.status_code}")

response = session.get(HOMEPAGE)

soup = bs(response.content, "html.parser")
code = soup.find("input", {"name": "code"})["value"]
scope = soup.find("input", {"name": "scope"})["value"]
state = soup.find("input", {"name": "state"})["value"]
session_state = soup.find("input", {"name": "session_state"})["value"]
iss = soup.find("input", {"name": "iss"})["value"]

payload = {"code": code,
           "scope": scope,
           "state": state,
           "session_state": session_state,
           "iss": iss}
url = "https://familyportal.renweb.com/signin-oidc"
response = session.post(url, data=payload)
if not response.status_code == 200:
    raise Exception(f"Failed to POST to {url} with code {response.status_code}")
response = session.get("https://familyportal.renweb.com/school/index")
if response.status_code == 200 and response.url == HOMEPAGE:
    print("Success!")
else:
    print("Failed")
    raise Exception(f"Got code {response.status_code} at {response.url}")
