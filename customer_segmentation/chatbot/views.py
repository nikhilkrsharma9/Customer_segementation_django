# chatbot/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from .models import ChatMessage
import re

# Initialize NLTK data with error handling
def initialize_nltk():
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords')
    
    try:
        nltk.data.find('sentiment/vader_lexicon')
    except LookupError:
        nltk.download('vader_lexicon')

# Run initialization when module loads
initialize_nltk()

# Initialize analyzers
sia = SentimentIntensityAnalyzer()
stop_words = set(stopwords.words('english'))

# Knowledge base for segmentation questions
KNOWLEDGE_BASE = {
    r'upload|file|csv': "Go to the upload page and select your CSV file containing customer data with columns like 'Annual Income' and 'Spending Score'.",
    r'cluster|how many groups': "Use the elbow method plot to determine optimal clusters. Look for the point where the line bends sharply (usually 3-5 clusters).",
    r'income|spending': "The tool analyzes relationships between annual income and spending scores to group similar customers.",
    r'result|interpret': "Each color represents a customer segment. Centroids (★) show the average characteristics of each group.",
    r'start|begin': "1. Upload your CSV 2. View the elbow plot 3. Select cluster count 4. Analyze results"
}

@csrf_exempt
@require_POST
def chat_api(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_message = data.get('message', '').strip().lower()
        session_key = request.session.session_key or 'anonymous'

        if not user_message:
            return JsonResponse({'response': "Please type a message."})

        # Ensure NLTK resources are available
        try:
            # Preprocess message
            tokens = word_tokenize(user_message)
            filtered_tokens = [word for word in tokens if word not in stop_words]
            
            # 1. Sentiment analysis
            sentiment = sia.polarity_scores(user_message)
            
            # 2. Pattern matching
            response = None
            for pattern, reply in KNOWLEDGE_BASE.items():
                if re.search(pattern, user_message, re.IGNORECASE):
                    response = reply
                    break
            
            # 3. Default responses
            if not response:
                if sentiment['compound'] < -0.5:
                    response = "I notice you might be frustrated. The segmentation process is simple: upload data → choose clusters → view results."
                elif sentiment['compound'] > 0.5:
                    response = "Glad you're excited! Would you like help with uploading data or interpreting results?"
                else:
                    response = "I can help with: 1) File uploads 2) Cluster selection 3) Result interpretation. What do you need?"

            # 4. Save conversation
            ChatMessage.objects.create(
                user_message=user_message,
                bot_response=response,
                session_key=session_key
            )

            return JsonResponse({'response': response})
        
        except LookupError as e:
            # Auto-download missing NLTK data
            missing_resource = str(e).split("'")[1]
            nltk.download(missing_resource.split('/')[0])
            return JsonResponse({
                'response': "Please try your question again. I needed to load some additional language resources."
            })
    
    except Exception as e:
        return JsonResponse({
            'response': "Sorry, I encountered an error. Please try a different question or try again later.",
            'error': str(e)
        }, status=500)