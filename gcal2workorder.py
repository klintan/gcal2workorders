# -*- coding: utf-8 -*-
import gflags
import httplib2

from apiclient.discovery import build
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.tools import run

import json
import requests
import sys
import urllib

reload(sys)
sys.setdefaultencoding("utf-8")

def init_seventime():
	#create Seventime connection
	url = 'https://app.seventime.se/loginFromApp'
	data = {'username': '', 'password': ''}
	headers = {'content-type': 'application/json'}
	#create session
	session=requests.Session()
	ra=session.post(url, data=json.dumps(data), headers=headers)
	return session

def createWorkorder(gcal, session):
	headers = {'content-type': 'application/json'}
	url = "https://app.seventime.se/workorders"
	ra = init_seventime()
	workorder_data = gcal
	ra=session.post(url, data=json.dumps(gcal), headers=headers)
	return ra

def getCustomerID(customer,session):
	headers = {'content-type': 'application/json'}
	url = "https://app.seventime.se/customers?"
	customer_enc = urllib.quote_plus(customer)
	params = {"queryValue": customer_enc}
	data=session.get(url+"queryValue="+customer_enc, headers=headers)
	customerid = json.loads(data.text)[0]['_id']
	return customerid

FLAGS = gflags.FLAGS

# Set up a Flow object to be used if we need to authenticate. This
# sample uses OAuth 2.0, and we set up the OAuth2WebServerFlow with
# the information it needs to authenticate. Note that it is called
# the Web Server Flow, but it can also handle the flow for native
# applications
# The client_id and client_secret can be found in Google Developers Console

FLOW = OAuth2WebServerFlow(
    client_id='',
    client_secret='',
    scope='https://www.googleapis.com/auth/calendar',
    user_agent='')

# To disable the local server feature, uncomment the following line:
FLAGS.auth_local_webserver = False

# If the Credentials don't exist or are invalid, run through the native client
# flow. The Storage object will ensure that if successful the good
# Credentials will get written back to a file.
storage = Storage('calendar.dat')
credentials = storage.get()
if credentials is None or credentials.invalid == True:
  credentials = run(FLOW, storage)

# Create an httplib2.Http object to handle our HTTP requests and authorize it
# with our good Credentials.
http = httplib2.Http()
http = credentials.authorize(http)

# Build a service object for interacting with the API. Visit
# the Google Developers Console
# to get a developerKey for your own application.
service = build(serviceName='calendar', version='v3', http=http,
       developerKey='')

events = service.events().list(calendarId='').execute()

session = init_seventime()

for event in events['items']:
	try:
		end_date = event['end']['dateTime']
		description = event['description']
		link = event['htmlLink']
		event_id = event['id']
		start_date = event['start']['dateTime']
		customer = event['summary']
		address = event['location']
	except Exception, e:
		print e
		continue
	

	print start_date
	print end_date

	print description
	print customer

	print event_id
	print link

customerid = getCustomerID('',session)
gcal_dict = {"title":description, "description":link, "startDate":start_date, "endDate":end_date,"status":100, "customer":customerid,"customerName":customer}
print createWorkorder(gcal_dict, session)
