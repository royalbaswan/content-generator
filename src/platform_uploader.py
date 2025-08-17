# platform_uploader.py - Handles uploading content to various platforms
import os
import logging
from typing import Dict, Any
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from instagram_private_api import Client
import requests

class PlatformUploader:
    def __init__(self):
        # YouTube API credentials
        self.youtube_scopes = [
            'https://www.googleapis.com/auth/youtube.upload',
            'https://www.googleapis.com/auth/youtube'
        ]
        self.youtube_credentials_file = 'credentials/youtube_credentials.json'
        self.youtube_token_file = 'credentials/youtube_token.json'
        
        # Instagram API credentials
        self.instagram_username = os.getenv('INSTAGRAM_USERNAME')
        self.instagram_password = os.getenv('INSTAGRAM_PASSWORD')
        
        # Create credentials directory
        os.makedirs('credentials', exist_ok=True)
        
        # Initialize APIs
        self.youtube = self.initialize_youtube()
        self.instagram = self.initialize_instagram()
    
    def initialize_youtube(self):
        """Initialize YouTube API client"""
        try:
            credentials = None
            
            # Load existing credentials
            if os.path.exists(self.youtube_token_file):
                credentials = Credentials.from_authorized_user_file(
                    self.youtube_token_file, self.youtube_scopes
                )
            
            # If no valid credentials, get new ones
            if not credentials or not credentials.valid:
                if credentials and credentials.expired and credentials.refresh_token:
                    credentials.refresh(requests.Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.youtube_credentials_file, self.youtube_scopes
                    )
                    credentials = flow.run_local_server(port=0)
                
                # Save credentials
                with open(self.youtube_token_file, 'w') as token:
                    token.write(credentials.to_json())
            
            # Build YouTube API client
            return build('youtube', 'v3', credentials=credentials)
            
        except Exception as e:
            logging.error(f"Error initializing YouTube API: {str(e)}")
            return None
    
    def initialize_instagram(self):
        """Initialize Instagram API client"""
        try:
            if self.instagram_username and self.instagram_password:
                return Client(
                    username=self.instagram_username,
                    password=self.instagram_password
                )
            return None
            
        except Exception as e:
            logging.error(f"Error initializing Instagram API: {str(e)}")
            return None
    
    def upload_to_platforms(self, video_files: Dict[str, str], content: Dict) -> Dict[str, str]:
        """Upload videos to multiple platforms"""
        upload_results = {}
        
        # Upload long-form to YouTube
        if video_files.get('long_form'):
            youtube_url = self.upload_to_youtube(
                video_files['long_form'],
                content['title'],
                content['metadata']['description'],
                content['metadata']['tags']
            )
            upload_results['youtube_url'] = youtube_url
        
        # Upload short-form to Instagram/YouTube Shorts
        if video_files.get('short_form'):
            instagram_url = self.upload_to_instagram(
                video_files['short_form'],
                content['title'],
                content['metadata']['description']
            )
            upload_results['instagram_url'] = instagram_url
            
            # Also upload to YouTube Shorts
            shorts_url = self.upload_to_youtube_shorts(
                video_files['short_form'],
                content['title'],
                content['metadata']['description'],
                content['metadata']['tags']
            )
            upload_results['youtube_shorts_url'] = shorts_url
        
        return upload_results
    
    def upload_to_youtube(self, video_file: str, title: str, description: str, tags: list) -> str:
        """Upload video to YouTube"""
        try:
            if not self.youtube:
                raise Exception("YouTube API client not initialized")
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'tags': tags,
                    'categoryId': '27'  # Education category
                },
                'status': {
                    'privacyStatus': 'private',  # Start as private, can be changed later
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create video insert request
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(
                    video_file,
                    chunksize=-1,
                    resumable=True
                )
            )
            
            # Execute upload
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    logging.info(f"Uploaded {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://youtu.be/{video_id}"
            
            logging.info(f"Video uploaded successfully to YouTube: {video_url}")
            return video_url
            
        except Exception as e:
            logging.error(f"Error uploading to YouTube: {str(e)}")
            return None
    
    def upload_to_instagram(self, video_file: str, title: str, description: str) -> str:
        """Upload video to Instagram"""
        try:
            if not self.instagram:
                raise Exception("Instagram API client not initialized")
            
            # Prepare caption
            caption = f"{title}\n\n{description}\n\n#educationalcontent #facts #learning"
            
            # Upload video
            response = self.instagram.video_upload(
                video_file,
                caption=caption,
                title=title
            )
            
            # Get video URL
            if response.get('media'):
                video_url = f"https://instagram.com/p/{response['media']['code']}"
                logging.info(f"Video uploaded successfully to Instagram: {video_url}")
                return video_url
            
            return None
            
        except Exception as e:
            logging.error(f"Error uploading to Instagram: {str(e)}")
            return None
    
    def upload_to_youtube_shorts(self, video_file: str, title: str, description: str, tags: list) -> str:
        """Upload video as YouTube Short"""
        try:
            if not self.youtube:
                raise Exception("YouTube API client not initialized")
            
            # Modify title and description for Shorts
            shorts_title = f"{title} #Shorts"
            shorts_description = f"{description}\n\n#Shorts #EducationalShorts #LearnOnShorts"
            
            # Add Shorts-specific tags
            shorts_tags = tags + ['shorts', 'educational shorts', 'learning']
            
            # Prepare video metadata
            body = {
                'snippet': {
                    'title': shorts_title,
                    'description': shorts_description,
                    'tags': shorts_tags,
                    'categoryId': '27'  # Education category
                },
                'status': {
                    'privacyStatus': 'private',  # Start as private, can be changed later
                    'selfDeclaredMadeForKids': False
                }
            }
            
            # Create video insert request
            insert_request = self.youtube.videos().insert(
                part=','.join(body.keys()),
                body=body,
                media_body=MediaFileUpload(
                    video_file,
                    chunksize=-1,
                    resumable=True
                )
            )
            
            # Execute upload
            response = None
            while response is None:
                status, response = insert_request.next_chunk()
                if status:
                    logging.info(f"Uploaded {int(status.progress() * 100)}%")
            
            video_id = response['id']
            video_url = f"https://youtube.com/shorts/{video_id}"
            
            logging.info(f"Short uploaded successfully to YouTube: {video_url}")
            return video_url
            
        except Exception as e:
            logging.error(f"Error uploading to YouTube Shorts: {str(e)}")
            return None
    
    def verify_upload(self, platform: str, url: str) -> bool:
        """Verify if upload was successful by checking URL"""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                logging.info(f"Successfully verified upload on {platform}: {url}")
                return True
            
            logging.warning(f"Could not verify upload on {platform}: {url}")
            return False
            
        except Exception as e:
            logging.error(f"Error verifying upload on {platform}: {str(e)}")
            return False
