import pandas as pd
import random
import os

categories = ['Technical', 'Billing', 'Account', 'Network', 'General']

# Templates for each category to generate somewhat realistic text
templates = {
    'Technical': [
        "My {} is crashing every time I open it.",
        "I'm getting an error code {} when I try to run the software.",
        "The application freezes during {}.",
        "I need help installing {} on my computer.",
        "How do I update the {} drivers?",
        "The software won't start after the latest {} update.",
        "I keep getting a blue screen when I use {}.",
        "Can't install the latest patch for {}.",
        "The system is running very slow when {} is open.",
        "There is a bug in the {} feature."
    ],
    'Billing': [
        "I was charged twice for my {} subscription.",
        "My invoice for {} is incorrect.",
        "I want to cancel my {} plan.",
        "I haven't received a refund for {} yet.",
        "Why is there an extra fee on my {} bill?",
        "How do I update my payment method for {}?",
        "My credit card was declined for {}.",
        "I need a receipt for my {} purchase.",
        "Can I get a discount on my {} renewal?",
        "The pricing for {} on my bill doesn't match the website."
    ],
    'Account': [
        "I forgot my password and cannot login to my {} account.",
        "My account is locked out after trying to access {}.",
        "How do I change my email address for my {} profile?",
        "I need to delete my {} account permanently.",
        "I'm not receiving the verification email for {}.",
        "Can you merge my two accounts for {}?",
        "My profile information for {} is not updating.",
        "I want to update my security questions for {}.",
        "Someone hacked my {} account.",
        "I need to add a new user to my {} account."
    ],
    'Network': [
        "My internet is not working even though my {} is connected.",
        "I have a very slow connection speed on {} network.",
        "The Wi-Fi drops frequently when I'm using {}.",
        "I can't connect to the VPN for {}.",
        "Router is not responding after {} restart.",
        "I'm getting high ping when connected to {}.",
        "My IP address seems to be blocked by {}.",
        "The {} server is timing out.",
        "How do I configure the firewall for {}?",
        "No internet access on my {} device."
    ],
    'General': [
        "What are your business hours for {} support?",
        "I have a question about your {} policy.",
        "How do I contact the {} team?",
        "Where is your {} office located?",
        "Can you send me more information about {}?",
        "I'm just leaving some feedback about {}.",
        "Do you offer support in {} language?",
        "Is there a manual available for {}?",
        "When will the new {} feature be released?",
        "Thank you for helping with my {} issue earlier."
    ]
}

fillers = [
    "the app", "the system", "Windows", "Mac", "my phone", "the dashboard", 
    "my portal", "the service", "this product", "my workspace", "the latest version",
    "my desktop", "the tool", "my server", "the platform"
]

data = []

# Generate 500 tickets
for _ in range(500):
    category = random.choice(categories)
    template = random.choice(templates[category])
    filler = random.choice(fillers)
    description = template.format(filler)
    
    # Add some randomness to descriptions to avoid exact duplicates
    prefix = random.choice(["Hi, ", "Hello, ", "URGENT: ", "Please help, ", "Issue: ", ""])
    suffix = random.choice([" Thanks.", " Please resolve.", " ASAP.", " Can someone check?", ""])
    description = prefix + description + suffix
    
    data.append({'ticket_description': description.strip(), 'category': category})

# Create dataset folder
os.makedirs('dataset', exist_ok=True)

df = pd.DataFrame(data)
# Shuffle the dataset
df = df.sample(frac=1, random_state=42).reset_index(drop=True)
df.to_csv('dataset/tickets.csv', index=False)
print("Dataset created successfully at dataset/tickets.csv with 500 records.")
