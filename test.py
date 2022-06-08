import requests
import json

bearer_token = '123abc'

url = 'http://localhost:8080?a=b'

params = {'key': 'val'} # adds to GET queries
head   = { 'Authorization': f'Bearer {bearer_token}' }

response = requests.get( url = url, params = params, headers=head, timeout = 0.2 )
# https://www.w3schools.com/python/ref_requests_response.asp

print( response.status_code )
print( response.headers )
print( response.text )