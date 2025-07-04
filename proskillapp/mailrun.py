from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/gmail.send'],
    redirect_uri='http://localhost:62932/'
)
auth_url, _ = flow.authorization_url(access_type='offline')
print(auth_url)
