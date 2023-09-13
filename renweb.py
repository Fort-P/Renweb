# Import libraries
from bs4 import BeautifulSoup as bs
import requests
import json

# Define functions
def POST(url, data):
    """
    Tries 5 times to sends a POST request to {url} with the data of {data}
    If every try fails, raise an exception
    Returns a requests object containing the POST
    """
    for i in range(0,5):
        r = session.post(url, data=data)
        if not r.status_code == 200 and i < 4: # It failed, but we haven't tried 5 times yet
            pass
        elif not r.status_code == 200: # We have failed everytime, and we are on the last try
            raise Exception(f"Failed to POST to {url} with code {r.status_code}")
        else: # We are all good, and the data was POSTed
            break
        return r # Return the POST request for external processing

# Declare a few variables
HOMEPAGE = "https://familyportal.renweb.com/school/index"
url = "https://accounts.renweb.com/Account/Login"
session = requests.session()

# Load config
with open('config.json') as file:
    config = json.load(file)

print("Logging in to Renweb...", end="") # Inform the user what we are doing

# Get token to bypass antibot
response = session.get(url)
soup = bs(response.content, "html.parser")
token = soup.find("input", {"name": "__RequestVerificationToken"})["value"]

# Create the initial payload
payload = {
    "District": config['District'],
    "Username": config['Username'],
    "Password": config['Password'],
    "signIn": "LOG IN",
    "__RequestVerificationToken": token}

response = POST(response.url, payload)

# We have to submit another form with some verification values since our "browser" doesn't support JavaScript
response = session.get(HOMEPAGE) # This actually redirrects us to another webpage for verification
soup = bs(response.content, "html.parser")
code = soup.find("input", {"name": "code"})["value"]
scope = soup.find("input", {"name": "scope"})["value"]
state = soup.find("input", {"name": "state"})["value"]
session_state = soup.find("input", {"name": "session_state"})["value"]
iss = soup.find("input", {"name": "iss"})["value"]

# Craft the second payload
payload = {"code": code,
           "scope": scope,
           "state": state,
           "session_state": session_state,
           "iss": iss}

# POST the new payload
url = "https://familyportal.renweb.com/signin-oidc" # New form submision URL
response = POST(url, payload)

# Go to homepage to confirm login
response = session.get("https://familyportal.renweb.com/school/index")
if response.status_code == 200 and response.url == HOMEPAGE:
    print("Success!")
else:
    print("Failed")
    raise Exception(f"Got code {response.status_code} at {response.url}")
