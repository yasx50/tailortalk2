from google_auth_oauthlib.flow import InstalledAppFlow
import pickle

# Step 1: Define the scopes (calendar access)
SCOPES = ['https://www.googleapis.com/auth/calendar']

# Step 2: Load client_secret.json and start the OAuth flow
flow = InstalledAppFlow.from_client_secrets_file(
    'token.json', SCOPES)

creds = flow.run_local_server(port=0)

# Step 3: Save the credentials (contains refresh_token)
with open('token.pkl', 'wb') as token:
    pickle.dump(creds, token)

print("✅ Auth complete. Token saved.")
