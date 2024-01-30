
# D118-Google-Space-Automation

Script using the Chat and Directory APIs to add an email group members into multiple Google Chat Spaces and remove any suspended users.

## Overview

The script first finds all the current members of a specified Google email group, adding them to a list to use later.
Then it goes through each space which is pre-defined with a space ID in the format 'spaces/xxxxxxxxxxx', and gets the current members of that space and their account status, removing any users whose account is suspended.
Then the list of group members is iterated over and checked against the space membership list, and any users who are in the email group but not the space are added.

## Requirements

**Please read this whole section, as the setup is fairly complex and all parts are required in order for it to work correctly.**

The following Python libraries must be installed on the host machine (links to the installation guide):

- [Python-Google-API](https://github.com/googleapis/google-api-python-client#installation)

In addition, an OAuth credentials.json file must be in the same directory as the overall script. This is the credentials file you can download from the Google Cloud Developer Console under APIs & Services > Credentials > OAuth 2.0 Client IDs. Download the file and rename it to credentials.json. When the program runs for the first time, it will open a web browser and prompt you to sign into a Google account that has the permissions used in the script. Based on this login it will generate a token.json file that is used for authorization. When the token expires it should auto-renew unless you end the authorization on the account or delete the credentials from the Google Cloud Developer Console. One credentials.json file can be shared across multiple similar scripts if desired. There are full tutorials on getting these credentials from scratch available online. But as a quickstart, you will need to create a new project in the Google Cloud Developer Console, and follow [these](https://developers.google.com/workspace/guides/create-credentials#desktop-app) instructions to get the OAuth credentials, and then enable APIs in the project (the Admin SDK API and Google Chat API are used in this project).

In order for the Chat API to be able to interact with the spaces and add/remove users, you will need to set up an [App](https://developers.google.com/chat) through the Google Cloud Developer Console in the Chat API section. From the GCDC project, go to Enabled APIs & Services > Google Chat API > click on Configuration in the middle top navigation area which should lead you [here](https://console.cloud.google.com/apis/api/chat.googleapis.com/hangouts-chat?).
Then an app name, avatar, description, and connection type must be configured. I used fairly generic names for mine so I can re-use it in multiple projects, but if you want to have dedicated apps for different processes you can, you will just need to create new GCDC projects to house a new Chat API app each time. I also selected Cloud Pub/Sub for the connection settings, which I am not utilizing so I chose a generic topic name.

You must have a Google account that has the proper roles and privileges to view the user directory and groups, and is a member of the chat spaces you wish to synchronize (or the app must be added to those spaces - I have not tested this as I did not use this method). This is the account that the script will run against, and it will need to be signed into the first time the script is run after the credentials.json file is added. It should pop up a web browser automatically and prompt you to sign in.

The following Environment Variables must be set on the machine running the script:

- TECH_GROUP

This is just an environment variable containing the email group to use, in my case it is for our technology group. If  you wish, you can directly include this group by just defining `EMAIL_GROUP = "email@xyz.com"` instead of the environment variable lookup, or rename it to a different environment variable name that contains the email group.

You must populate the constant `SPACE_IDS` with the list of Chat Space IDs that you wish the email group members to be added to. These are unique per domain and each space/chat group will have its own. There are 2 quick ways to find these, the first method is to just open chat.google.com and navigate to a space on the left hand bar. The URL will change to something that resembles `"mail.google.com/chat/u/0/#chat/space/xxxxxxxxxxx"` with the x's being unique for each space. You can copy and paste the space/xxxxxxxxxxx into the list in the program, but you need to pluralize "space/" to "spaces/" for each one.
The second method is to edit the script to run the getgroups() function, which will print out a list of spaces the Google account that is authorized and running the script is a member of, as well as their display names so you can pick and choose which ones to include. This will output to the local console so a IDE is recommended.

## Customization

There is not much you should need to customize after you have done the steps in the setup. As mentioned above, you must define the `SPACE_IDS` which are specific to your use case. You must also set the environment variable `TECH_GROUP`, or define `EMAIL_GROUP` directly.

The only other thing you might want to change is to choose whether suspended users are removed from the chat spaces. By default `REMOVE_SUSPENDED` is True, but you can set to False in order for them to be kept in the space even when suspended.
