import base64
import csv
import datetime
import pickle
import os.path
from html.parser import HTMLParser
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

DEBUG = False

class UnsubLinkParser(HTMLParser):
    a_href = ''
    unsub_links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href':
                    self.a_href = attr[1]
                    break

    def handle_endtag(self, tag):
        if tag == 'a':
            self.a_href = ''

    def handle_data(self, data):
        if self.a_href != '' and 'unsubscribe' in data.lower():
            self.unsub_links.append(self.a_href)
            self.a_href = ''

def getMessagesWithLabels(service, user_id, label_ids):
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
        messages.extend(response['messages'])
        while 'nextPageToken' in response and not DEBUG:
            print('\rFound %d messages' % len(messages), end='')
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                                                       labelIds=label_ids,
                                                       pageToken=page_token).execute()
            messages.extend(response['messages'])
    print() # new line after carriage returns
    return messages

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    spam_label_id = None
    for label in labels:
        if label['name'] == 'SPAM':
            spam_label_id = label['id']
    if not spam_label_id:
        print('SPAM label not found')
        return

    # Returns just message id and threadId for each message
    min_messages = getMessagesWithLabels(service, 'me', [spam_label_id])


    parser = UnsubLinkParser()

    # The callback for each message
    def getMsgData(rid, message, exception):
        if exception is not None:
            return
        try:
            msg = next(m for m in message['payload']['parts'] if m['mimeType'] == 'text/html')
        except:
            return
        msg_data = msg['body']['data']
        msg_html = base64.urlsafe_b64decode(msg_data.encode('ASCII')).decode('utf-8')
        parser.feed(msg_html)

    # Batching requests is faster
    batcher = service.new_batch_http_request()
    for i, mm in enumerate(min_messages):
        if (i % 100 == 0 and i != 0):
            print(f'\rRequesting msg {i}', end='')
            batcher.execute()
            batcher = service.new_batch_http_request()
        batcher.add(service.users().messages().get(userId='me', id=mm['id'], format='full'), callback=getMsgData)
    print() # new line after carriage returns
    # Handle last set
    batcher.execute()



    with open('unsub_links.txt', 'w') as f:
        f.writelines("%s\n" % ul for ul in parser.unsub_links)

if __name__ == '__main__':
    main()
