import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Configuration
    PORT = int(os.getenv('PORT', 8000))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Google AI Configuration
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Tavily Configuration  
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    
    # CORS Configuration
    FRONTEND_URLS = [
        'http://localhost:3000',
        'https://your-app.vercel.app'  # Update with your actual frontend URL
    ]
    
    @staticmethod
    def validate_config():
        """Validate required environment variables"""
        required_vars = ['GOOGLE_API_KEY', 'TAVILY_API_KEY']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")