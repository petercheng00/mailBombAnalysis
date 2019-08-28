import csv
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

DEBUG = False

def epochMsToDateTime(epoch_ms):
    return datetime.datetime.fromtimestamp(epoch_ms/1000).strftime('%Y-%m-%d %H:%M:%S.%f')


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


    # The data we will gather
    data = [['epoch_ms', 'from', 'reply-to', 'subject']]

    # The callback for each message
    def getMsgData(rid, message, exception):
        if exception is not None:
            return
        epoch_ms = int(message['internalDate'])
        fromx = ''
        reply_to = ''
        subject = ''
        headers = message['payload']['headers']
        for h in headers:
            if h['name'] == 'From':
                fromx = h['value']
            elif h['name'] == 'Reply-To':
                reply_to = h['value']
            elif h['name'] == 'Subject':
                subject = h['value']
                data.append([epoch_ms, fromx, reply_to, subject])

    # Batching requests is faster
    batcher = service.new_batch_http_request()
    for i, mm in enumerate(min_messages):
        if (i % 100 == 0 and i != 0):
            print(f'\rRequesting msg {i}', end='')
            batcher.execute()
            batcher = service.new_batch_http_request()
        batcher.add(service.users().messages().get(userId='me', id=mm['id'], format='metadata'), callback=getMsgData)
    print() # new line after carriage returns
    # Handle last set
    batcher.execute()

    with open('data.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)

if __name__ == '__main__':
    main()
