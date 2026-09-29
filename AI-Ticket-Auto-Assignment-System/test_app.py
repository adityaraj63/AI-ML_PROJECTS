import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ticket_system.settings')
django.setup()

from django.test import Client
from tickets.models import Ticket

client = Client()

print("Testing Dashboard...")
response = client.get('/')
print("Dashboard Status:", response.status_code)

print("\nTesting Ticket Creation (Valid Input)...")
response = client.post('/create/', {'description': 'I forgot my account password and cannot log in.'})
print("Create Ticket Status:", response.status_code)
if 'ticket' in response.context:
    t = response.context['ticket']
    print(f"Created Ticket: Category={t.category}, Team={t.assigned_team}, Confidence={t.confidence}%")

print("\nTesting Ticket Creation (Empty Input)...")
response = client.post('/create/', {'description': ''})
print("Create Ticket Empty Status:", response.status_code)
print("Error:", response.context.get('error'))

print("\nTesting Ticket Creation (Short Input)...")
response = client.post('/create/', {'description': 'help me'})
print("Create Ticket Short Status:", response.status_code)
print("Error:", response.context.get('error'))

print("\nTesting Ticket History...")
response = client.get('/history/')
print("Ticket History Status:", response.status_code)
print("Tickets found:", len(response.context['tickets']))

print("\nAll tests completed.")
