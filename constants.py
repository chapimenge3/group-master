import os
from mongoengine import connect
from chapa import Chapa

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
MONGO_URL = os.getenv('MONGO_URL')
TOKEN = os.getenv('TOKEN')
CHAPA_SECRET = os.getenv('CHAPA_SECRET')
STRIPE_SECRET= os.getenv('STRIPE_SECRET')
INVITE_LINK = os.getenv('INVITE_LINK')

chapa = Chapa(CHAPA_SECRET)

if MONGO_PASSWORD and MONGO_URL:
    MONGO_URL = MONGO_URL.replace('<password>', MONGO_PASSWORD)
    connect(host=MONGO_URL)

PAYMENT_METHODS = [
    ['Chapa', 'chapa'],
    ['Stripe', 'stripe'],
]

WELCOME_MESSAGE = '''Welcome to Group Master Bot {user}

Send /help to get help

Please choose the group you want to join from the list below:
'''

GROUP_DETAIL_MESSAGE = '''You have selected {group_name}

Price: {price}
Duration: {duration} days

Select payment method below:
'''

PAY_MESSAGE = '''Please precede with your payment either by clicking the pay button or click the below link

<a href="{link}">CLICK HERE</a>
'''

INVITE_MESSAGE = '''Your payment has been received. 

You can now invite your friends to join the group by clicking the below link

{link}
'''

PAYMENT_FAILED_MESSAGE = '''Your payment has failed. Please try again later'''