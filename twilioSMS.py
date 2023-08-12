# Download the helper library from https://www.twilio.com/docs/python/install
import os
from dotenv import load_dotenv
from twilio.rest import Client

import postgreData as db

# Load environment variables from .env file
load_dotenv()


users = ['<insert_phoneNo>']#db.userSMS()

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = os.getenv('TWILIO_ACCOUNT_SID')
auth_token = os.getenv('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)



def sendSMS(msg):
    for user in users:
        message = client.messages \
                        .create(
                            body=msg,
                            from_='<your_twilio_number>',
                            to=f'{user}'
                        )

        print(message.sid)

