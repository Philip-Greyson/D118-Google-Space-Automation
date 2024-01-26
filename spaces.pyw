"""Script to add members of a specific email group to Google Chat Spaces automatically.

https://github.com/Philip-Greyson/D118-Google-Space-Automation

First finds all the members of a specified Gmail group, storing their emails in a list.
Then goes through the predefined list of Chat spaces and gets their member lists.
Any currently suspended account is removed from the space, and any emails in the Gmail group that are not already a member of the space are added.

See the following API references and guides that are used in this project:
https://googleapis.github.io/google-api-python-client/docs/dyn/chat_v1.spaces.html
https://googleapis.github.io/google-api-python-client/docs/dyn/chat_v1.spaces.members.html
https://googleapis.github.io/google-api-python-client/docs/dyn/admin_directory_v1.users.html
https://developers.google.com/chat/api/guides/v1/members/create
https://developers.google.com/chat/api/guides/v1/members/delete
https://developers.google.com/admin-sdk/directory/reference/rest/v1/members/list
"""

# importing module
import datetime  # needed to get current date to check what term we are in
import os  # needed to get environment variables
from datetime import *

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

EMAIL_GROUP = os.environ.get('TECH_GROUP')  # the email of the group whose members will be added to the spaces
SPACE_IDS =['spaces/AAAAPhybgs0','spaces/AAAAI275-Ps','spaces/AAAAQfD6OvU','spaces/AAAAplRUjYU','spaces/AAAADktlgBE','spaces/AAAAkh4SdI0','spaces/AAAA0adnGm0','spaces/AAAAMm3BpU8','spaces/AAAAW0b9Nwo','spaces/AAAAWK20uIk','spaces/AAAAy0tsnzQ', 'spaces/AAAA4Vu28Fs','spaces/AAAAKoZF7IQ','spaces/AAAAx2y6BrI','spaces/AAAAVibi7q0','spaces/AAAAs8JCdL0','spaces/AAAACRnDL10','spaces/AAAAO_v44Ng','spaces/AAAAuu0GhY0','spaces/AAAA7vuf72Y','spaces/AAAA01Rwg50',]
REMOVE_SUSPENDED = True

# Google API Scopes that will be used. If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.user', 'https://www.googleapis.com/auth/admin.directory.group', 'https://www.googleapis.com/auth/admin.directory.group.member', 'https://www.googleapis.com/auth/admin.directory.orgunit', 'https://www.googleapis.com/auth/admin.directory.userschema', 'https://www.googleapis.com/auth/chat.memberships', 'https://www.googleapis.com/auth/chat.spaces']

# Get credentials from json file, ask for permissions on scope or use existing token.json approval, then build the "service" connection to Google API
creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

chat = build('chat', 'v1', credentials=creds)
directory = build('admin', 'directory_v1', credentials=creds)

def getgroups() -> None:
    """Prints out a list of current chat spaces the running user is a member of."""
    groups = chat.spaces().list(filter='spaceType = "SPACE"').execute()  # gets a list of the chat spaces, filtering to only spaces, not direct/group chats
    groups = groups.get('spaces', [])  # get the values of spaces from the result
    for group in groups:
        # print(group)
        print(str(group.get('displayName')) + ": " + str(group.get('name')))  # prints out the display name (what you see as a user in chat) as well as the spaces/xxxxxx ID, which can be used to populate the SPACE_IDS list

if __name__ == '__main__':  # main file execution
    with open('spaces_log.txt', 'w', encoding='utf-8') as log:  # open logging file
        # print(EMAIL_GROUP)  # debug
        startTime = datetime.now()
        startTime = startTime.strftime('%H:%M:%S')
        print(f'INFO: Execution started at {startTime}')
        print(f'INFO: Execution started at {startTime}', file=log)

        try:
            emailGroupMembers = []  # empty list that will contain the emails in our email group
            results = directory.members().list(groupKey=EMAIL_GROUP).execute().get('members', [])  # call the directory API to get a list of the members of the email group, then just get the member item from the returned dict
            for result in results:  # go through each user result from the group
                emailGroupMembers.append(result.get('email', []))  # add the email of the group member to our list
            print(f'DBUG: Current members of {EMAIL_GROUP}: {emailGroupMembers}')
            print(f'DBUG: Current members of {EMAIL_GROUP}: {emailGroupMembers}', file=log)
        except Exception as er:
            print(f'ERROR getting the members of the email group: {er}')
            print(f'ERROR getting the members of the email group: {er}', file=log)

        # check the members of each group initially
        for spaceID in SPACE_IDS:
            try:
                spaceName = chat.spaces().get(name=spaceID).execute().get('displayName')
                print(f'INFO: Proccessing space "{spaceName}"')
                print(f'INFO: Proccessing space "{spaceName}"', file=log)
                memberList = []  # create a blank list of members for each space
                members = chat.spaces().members().list(parent = spaceID, filter='member.type="HUMAN"').execute().get('memberships', [])  # use the chat API to get the human-only member list for the current space ID, then get just the memberships value from the dict result
                for member in members:  # process each member
                    try:
                        # the members result from the space membership gives a format users/xxxxxxxxxx userKey, so we want to convert it to an email for easier readability and processing. It could be done the other way around and convert
                        # emails to the users/xxxxxxxx userKey, but I chose to do it this way in case I want to be able to check by specific emails or something later
                        name = member.get('member', []).get('name', [])  # get their "name", which is in the format users/xxxxxxxxxxxxxxx
                        userKey = name.split('/')[1]  # split the name by the slash, which breaks into users and the string of numbers, so we only want the numbers which is the user key
                        user = directory.users().get(userKey=userKey).execute()  # do a query using the directory API to find the user account based on the user key
                        userEmail = user.get('primaryEmail', [])  # get just the primaryEmail field from the dict
                        if (user.get('suspended') == True) and REMOVE_SUSPENDED:  # get whether they are suspended, if they are we will remove them from the group if the REMOVE_SUSPENDED constant is set to true
                            try:
                                print(f'ACTION: {userEmail} is currently a member of "{spaceName}" while suspended, they will be removed from the space')
                                print(f'ACTION: {userEmail} is currently a member of "{spaceName}" while suspended, they will be removed from the space', file=log)
                                chat.spaces().members().delete(name=member.get('name', [])).execute()  # gets the full space + member name from the member dict, then calls the delete member function from the chat API with that info
                            except Exception as er:
                                print(f'ERROR while removing {userEmail} from space "{spaceName}": {er}')
                                print(f'ERROR while removing {userEmail} from space "{spaceName}": {er}', file=log)
                        else:
                            memberList.append(userEmail)  # if they are not suspended, add the email to the list of members of that space so we can compare to the emails in our email group
                    except Exception as er:  # catch errors that happen when trying to reference an invalid Google user. Should not happen since we filter to member.type=HUMAN but here just in case
                        print(f'ERROR processing space member {member.get("member", [])}: {er}')
                        print(f'ERROR processing space member {member.get("member", [])}: {er}', file=log)
                # print(f'Current members of {spaceName}: {memberList}')  # debug
                for email in emailGroupMembers:
                    if email not in memberList:  # if an email found in the target email group is not found in the space, we need to add it
                        try:
                            print(f'ACTION: {email} is a member of {EMAIL_GROUP} but is not currently in "{spaceName}", they will be added')
                            print(f'ACTION: {email} is a member of {EMAIL_GROUP} but is not currently in "{spaceName}", they will be added', file=log)
                            chat.spaces().members().create(parent=spaceID,body={'member': {'name': f'users/{email}', 'type':'HUMAN'}}).execute()  # call the create membership function from the chat API with the user email as the user argument
                        except Exception as er:
                            print(f'ERROR while trying to add {email} to space "{spaceName}": {er}')
                            print(f'ERROR while trying to add {email} to space "{spaceName}": {er}', file=log)
            except Exception as er:
                print(f'ERROR while processing group {spaceID}: {er}')
                print(f'ERROR while processing group {spaceID}: {er}', file=log)

        endTime = datetime.now()
        endTime = endTime.strftime('%H:%M:%S')
        print(f'INFO: Execution ended at {endTime}')
        print(f'INFO: Execution ended at {endTime}', file=log)
