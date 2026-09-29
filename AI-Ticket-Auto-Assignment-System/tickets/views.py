from django.shortcuts import render, redirect
from django.db.models import Count
from .models import Ticket
import joblib
import os
from django.conf import settings

# Load ML model and vectorizer
# In production, these should ideally be loaded once when the app starts.
try:
    model_path = os.path.join(settings.BASE_DIR, 'models', 'ticket_classifier.pkl')
    vectorizer_path = os.path.join(settings.BASE_DIR, 'models', 'tfidf_vectorizer.pkl')
    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)
except Exception as e:
    model = None
    vectorizer = None
    print(f"Error loading models: {e}")

TEAM_MAPPING = {
    'Technical': 'Technical Support',
    'Billing': 'Billing Support',
    'Account': 'Account Support',
    'Network': 'Network Support',
    'General': 'General Support',
}

def dashboard(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    
    total_tickets = tickets.count()
    category_counts = tickets.values('category').annotate(count=Count('category'))
    
    counts = {item['category']: item['count'] for item in category_counts if item['category']}
    
    context = {
        'total_tickets': total_tickets,
        'technical_count': counts.get('Technical', 0),
        'billing_count': counts.get('Billing', 0),
        'account_count': counts.get('Account', 0),
        'network_count': counts.get('Network', 0),
        'general_count': counts.get('General', 0),
        'recent_tickets': tickets[:10]
    }
    return render(request, 'dashboard.html', context)

def create_ticket(request):
    context = {}
    if request.method == 'POST':
        description = request.POST.get('description', '').strip()
        
        if not description:
            context['error'] = "Ticket description cannot be empty."
            return render(request, 'create_ticket.html', context)
        
        if len(description) < 10:
            context['error'] = "Ticket description is too short. Please provide more details."
            return render(request, 'create_ticket.html', context)
            
        if not model or not vectorizer:
            context['error'] = "Machine Learning model is not loaded. Cannot process ticket."
            return render(request, 'create_ticket.html', context)
            
        try:
            # ML Prediction
            text_features = vectorizer.transform([description])
            prediction = model.predict(text_features)[0]
            probabilities = model.predict_proba(text_features)[0]
            
            confidence = max(probabilities) * 100
            assigned_team = TEAM_MAPPING.get(prediction, 'General Support')
            
            # Save to Database
            ticket = Ticket.objects.create(
                description=description,
                category=prediction,
                assigned_team=assigned_team,
                confidence=round(confidence, 2)
            )
            
            context['success'] = True
            context['ticket'] = ticket
        except Exception as e:
            context['error'] = f"An error occurred during prediction: {str(e)}"
            
    return render(request, 'create_ticket.html', context)

def ticket_history(request):
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'ticket_history.html', {'tickets': tickets})
