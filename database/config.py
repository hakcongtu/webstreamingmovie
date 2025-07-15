import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - Tương thích với webstreamingmovie project
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./data/movie_streaming.db')

# CSV file paths
CSV_FILES = {
    'movies': 'movies.csv',
    'ratings': 'ratings.csv', 
    'tags': 'tags.csv',
    'links': 'links.csv'
}

# Webstreamingmovie project paths
WEBSTREAMING_PROJECT_PATH = "C:/Users/Asus/OneDrive/Desktop/webstreamingmovie"
WEBSTREAMING_DATA_PATH = os.path.join(WEBSTREAMING_PROJECT_PATH, "data") 