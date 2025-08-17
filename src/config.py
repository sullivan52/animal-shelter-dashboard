import os
from dotenv import load_dotenv

# Load environment variables from .env file for secure configuration management
load_dotenv()

# MongoDB Database Configuration
# Uses environment variables with fallback defaults for development
MONGO_CONFIG = {
   'USER': os.getenv('MONGO_USER', 'aacuser'),
   'PASS': os.getenv('MONGO_PASS', 'SNHU1234'),
   'HOST': os.getenv('MONGO_HOST', 'nv-desktop-services.apporto.com'),
   'PORT': int(os.getenv('MONGO_PORT', 33683)),
   'DB': os.getenv('MONGO_DB', 'AAC'),
   'COL': os.getenv('MONGO_COL', 'animals')
}

# Dashboard Application Configuration
DASHBOARD_CONFIG = {
   'debug': True,  # Enable debug mode for development
   'port': 8050    # Default port for Dash application
}

# Legacy Rescue Operation Criteria
# Maintained for backward compatibility with specialized rescue filtering
# Age values are in weeks (26 weeks = 6 months, 52 weeks = 1 year)
RESCUE_CRITERIA = {
   'Water Rescue': {
       'breeds': ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland"],
       'sex': "Intact Female",
       'age_min': 26,   # 6 months minimum
       'age_max': 156   # 3 years maximum
   },
   'Mountain or Wilderness Rescue': {
       'breeds': ["German Shepherd", "Alaskan Malamute", "Old English Sheepdog",
                 "Siberian Husky", "Rottweiler"],
       'sex': "Intact Male"
   },
   'Disaster or Individual Tracking': {
       'breeds': ["Doberman Pinscher", "German Shepherd", "Golden Retriever",
                 "Bloodhound", "Rottweiler"],
       'sex': "Intact Male",
       'age_min': 20,   # 5 months minimum
       'age_max': 300   # ~6 years maximum
   },
   'All Preferred Breeds': {
       'breeds': ["Labrador Retriever Mix", "Chesapeake Bay Retriever", "Newfoundland",
                 "German Shepherd", "Alaskan Malamute", "Old English Sheepdog",
                 "Siberian Husky", "Rottweiler", "Doberman Pinscher", "Golden Retriever",
                 "Bloodhound"]
   }
}