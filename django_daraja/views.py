# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django_daraja.mpesa import utils
import requests
import time
import base64

from django.http import HttpResponse, JsonResponse
from django.views.generic import View
from django_daraja.mpesa.core import MpesaClient
from decouple import config
from datetime import datetime
from .models import AccessToken, StkPushResponse

cl = MpesaClient()
stk_push_callback_url = 'https://api.darajambili.com/express-payment'
b2c_callback_url = 'https://api.darajambili.com/b2c/result'
production_B2C_POST_request_url = 'https://sandbox.safaricom.co.ke/mpesa/b2c/v3/paymentrequest'

def index(request):

	return HttpResponse('Welcome to the home of daraja APIs')

def oauth_success(request):
	r = cl.access_token()
	return JsonResponse(r, safe=False)

def stk_push_success(request):
	phone_number = config('LNM_PHONE_NUMBER')
	amount = 41
	account_reference = 'ABC001'
	transaction_desc = 'STK Push Description'
	callback_url = stk_push_callback_url
	r = cl.stk_push(phone_number, amount, account_reference, transaction_desc, callback_url)

	StkPushResponse.objects.create(
		phone_number=phone_number,
		amount=amount,
		account_reference=account_reference,
		transaction_desc=transaction_desc,
		callback_url=callback_url,
		response_description=r.response_description,
	)
	return JsonResponse(r.response_description, safe=False)

def business_payment_success(request):
	phone_number = config('B2C_PHONE_NUMBER')
	amount = 2
	transaction_desc = 'Business Payment Description'
	occassion = 'Test business payment occassion'
	callback_url = b2c_callback_url
	r = cl.business_payment(phone_number, amount, transaction_desc, callback_url, occassion)
	return JsonResponse(r.response_description, safe=False)

def salary_payment_success(request):
	phone_number = config('B2C_PHONE_NUMBER')
	amount = 1
	transaction_desc = 'Salary Payment Description'
	occassion = 'Test salary payment occassion'
	callback_url = b2c_callback_url
	r = cl.salary_payment(phone_number, amount, transaction_desc, callback_url, occassion)
	return JsonResponse(r.response_description, safe=False)

def promotion_payment_success(request):
	phone_number = config('B2C_PHONE_NUMBER')
	amount = 1
	transaction_desc = 'Promotion Payment Description'
	occassion = 'Test promotion payment occassion'
	callback_url = b2c_callback_url
	r = cl.promotion_payment(phone_number, amount, transaction_desc, callback_url, occassion)
	return JsonResponse(r.response_description, safe=False)


def generate_access_token():
    consumer_key = "QNPrSFcGYOFvksGnhaIclphR5MAIYUNZ"
    consumer_secret = "uPx8AtgvSGGyYcuf"
    
	# Concatenate the consumer key and secret, and encode to base64
    credentials = f"{consumer_key}:{consumer_secret}"
    base64_credentials = base64.b64encode(credentials.encode()).decode('utf-8')
    
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    
    # concatenate the consumer key:secret then convert to base64
    
    headers = {'Authorization': f'Basic {base64_credentials}'}
    
    try:
        r = requests.request("GET", url, headers=headers)
        r.raise_for_status()  # Raise an error for bad responses (e.g., 4xx or 5xx)
        mpesa_access_token = r.json()  # Try to parse the response as JSON
        
        # Check if the expected key 'access_token' is present
        if 'access_token' in mpesa_access_token:
            return mpesa_access_token['access_token']
        else:
            raise ValueError("Access token not found in the response")

    except requests.RequestException as e:
        # Handle network or HTTP-related errors
        print(f"Request error: {e}")
        print(f"Response text: {r.text}")
        print(f"Response content: {r.content}")
        raise ValueError("Error in accessing M-Pesa API")

    except (json.JSONDecodeError, ValueError) as e:
        # Handle JSON decoding errors or missing access token in the response
        print(f"JSON decoding error: {e}")
        print(f"Response content: {r.text}")
        raise ValueError("Error in parsing JSON response")

    except Exception as e:
        # Handle other unexpected errors
        print(f"Unexpected error: {e}")
        raise ValueError("Unexpected error")


def make_b2c_payment(request):
    validated_mpesa_access_token = generate_access_token()
    
	# Generate a unique OriginatorConversationID using a high-precision timestamp
    originator_conversation_id = f"{int(time.time() * 1000)}"
    
    headers = {
	    'Content-Type': 'application/json',
	    'Authorization': f'Bearer {validated_mpesa_access_token}'
    }

    payload = {    
        "OriginatorConversationID": originator_conversation_id,
        "InitiatorName": "MICHAEL MURIITHI",
        "SecurityCredential":"R0zGSc+cKZgQGEccvpWy2ijQqQsuCaL7nFt11xAC5kgdluuKWgJdz/8A1DEqJVgEzEq0dJAUVLarJ7lpdDFm26Ew3K/+xqNnltoijbyKkUyeUo1YZXbRlGniedx3x76/V+Q1Kgeq2RHLktdlK0W93t53nP5Y0USLBIXkPIxYqCia9alQEFVmv5jcHrH0gRiSKpSe0Nmgy6Zxa3uSZ83xiMz3ltsAQbishCXgua94fspI6OWnXPeivLeMJsM11U6d9slFWKiZ/qWwVviJYSWXaShoRzNiNw1XOzggC2K63BYYkqzB5W1/QByIJIDtVHj0uGxlHjbARtRm83lK4SMjGA==",
        "CommandID":"BusinessPayment",
        "Amount":"10",
        "PartyA":"3036771",
        "PartyB":"254702628912",
        "Remarks":"here are my remarks",
        "QueueTimeOutURL":"https://portal.usoniai.com/b2c/queue",
        "ResultURL":"https://portal.usoniai.com/b2c/result",
        "Occassion":"Christmas"
    }

    url = 'https://sandbox.safaricom.co.ke/mpesa/b2c/v3/paymentrequest'
    response = requests.post(url, headers=headers, json=payload)

    # Process the response or log it as needed
    print(response.text)

    return JsonResponse({'status': 'success'}) 