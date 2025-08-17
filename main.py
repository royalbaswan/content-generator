# Complete YouTube & Instagram Automation System for List-Based Educational Content
# Main orchestrator file: main.py
import schedule
import time
import logging
from datetime import datetime
from typing import Dict
import sqlite3

from src.content_generator import ContentGenerator
from src.video_creator import VideoCreator
from src.platform_uploader import PlatformUploader
from src.data_collector import DataCollector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

class YouTubeAutomationSystem:
    def __init__(self):
        self.setup_database()
        self.data_collector = DataCollector()
        self.content_generator = ContentGenerator()
        self.video_creator = VideoCreator()
        self.uploader = PlatformUploader()
        
        # Content calendar
        self.content_schedule = {
            'monday': 'geography',
            'tuesday': 'history', 
            'wednesday': 'science',
            'thursday': 'technology',
            'friday': 'psychology',
            'saturday': 'space',
            'sunday': 'trending'
        }
    
    def setup_database(self):
        """Initialize SQLite database for tracking content"""
        self.conn = sqlite3.connect('content_tracking.db')
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY,
                title TEXT UNIQUE,
                topic_category TEXT,
                created_date TEXT,
                youtube_url TEXT,
                instagram_url TEXT,
                views INTEGER DEFAULT 0,
                engagement_rate REAL DEFAULT 0.0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS topics_used (
                id INTEGER PRIMARY KEY,
                topic TEXT,
                last_used TEXT,
                usage_count INTEGER DEFAULT 1
            )
        ''')
        
        self.conn.commit()
    
    def generate_daily_content(self):
        """Main function to generate and upload daily content"""
        try:
            today = datetime.now()
            day_name = today.strftime('%A').lower()
            topic_category = self.content_schedule.get(day_name, 'general')
            
            logging.info(f"Generating content for {day_name} - Category: {topic_category}")
            
            # 1. Collect data for the topic
            raw_data = self.data_collector.get_topic_data(topic_category)
            
            # 2. Generate content script
            content = self.content_generator.create_list_content(raw_data, topic_category)
            
            # 3. Create videos (long-form + short-form)
            video_files = self.video_creator.create_videos(content)
            
            # 4. Upload to platforms
            upload_results = self.uploader.upload_to_platforms(video_files, content)
            
            # 5. Save to database
            self.save_video_record(content, upload_results)
            
            logging.info("Daily content generation completed successfully!")
            
        except Exception as e:
            logging.error(f"Error in daily content generation: {str(e)}")
    
    def save_video_record(self, content: Dict, upload_results: Dict):
        """Save video information to database"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO videos (title, topic_category, created_date, youtube_url, instagram_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            content['title'],
            content['category'],
            datetime.now().isoformat(),
            upload_results.get('youtube_url', ''),
            upload_results.get('instagram_url', '')
        ))
        self.conn.commit()
    
    def start_automation(self):
        """Start the automated scheduling system"""
        # Schedule daily content generation
        schedule.every().day.at("09:00").do(self.generate_daily_content)
        
        # Schedule performance analysis
        schedule.every().week.do(self.analyze_performance)
        
        logging.info("Automation system started. Scheduled daily content generation at 9:00 AM")
        
        while True:
            schedule.run_pending()
            time.sleep(3600)  # Check every hour
    
    def analyze_performance(self):
        """Analyze video performance and optimize"""
        # Implementation for performance analysis
        logging.info("Running weekly performance analysis...")

if __name__ == "__main__":
    # Initialize and start the automation system
    system = YouTubeAutomationSystem()
    import ipdb; ipdb.set_trace()
    # For testing, run once
    system.generate_daily_content()
    
    # For production, start automation
    # system.start_automation()
    # source "C:/Users/Royal Baswan/anaconda3/Scripts/activate" opencv_env