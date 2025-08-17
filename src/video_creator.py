# video_creator.py - Automated video creation with MoviePy
import os
from moviepy import (
    VideoClip, ImageClip, AudioFileClip, CompositeVideoClip, 
    concatenate_videoclips, CompositeAudioClip, afx
)
from PIL import Image, ImageDraw, ImageFont
import textwrap
import random
from gtts import gTTS
import logging
from typing import Dict, List

logging.basicConfig(level=logging.INFO)

class VideoCreator:
    def __init__(self):
        self.output_dir = "generated_videos"
        self.assets_dir = "assets"
        self.temp_dir = "temp"
        
        # Create directories
        for directory in [self.output_dir, self.assets_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)
        
        # Video specifications
        self.youtube_long_specs = {
            'resolution': (1920, 1080),
            'fps': 30,
            'duration_target': 480  # 8 minutes
        }
        
        self.shorts_specs = {
            'resolution': (1080, 1920),  # Vertical for Shorts/Reels
            'fps': 30,
            'duration_target': 45  # 45 seconds
        }
    
    def create_videos(self, content: Dict) -> Dict[str, str]:
        """Create both long-form and short-form videos"""
        try:
            # Generate voiceover
            audio_file = self.create_voiceover(content['script'])
            
            # Create long-form YouTube video
            long_form_video = self.create_long_form_video(content, audio_file)
            
            # Create short-form video for Shorts/Reels
            short_form_video = self.create_short_form_video(content, audio_file)
            
            return {
                'long_form': long_form_video,
                'short_form': short_form_video,
                'audio': audio_file
            }
            
        except Exception as e:
            logging.error(f"Error creating videos: {str(e)}")
            return {}
    
    def create_voiceover(self, script: Dict) -> str:
        """Generate AI voiceover from script"""
        try:
            full_text = script['full_script']
            
            # Use gTTS for basic TTS (can upgrade to ElevenLabs later)
            tts = gTTS(text=full_text, lang='en', tld='co.in', slow=False)
            
            audio_file = os.path.join(self.temp_dir, f"voiceover_{random.randint(1000, 9999)}.mp3")
            tts.save(audio_file)
            
            return audio_file
            
        except Exception as e:
            logging.error(f"Error creating voiceover: {str(e)}")
    
    def create_long_form_video(self, content: Dict, audio_file: str) -> str:
        """Create 8-12 minute YouTube video"""
        try:
            # Get audio duration to match video length
            if audio_file:
                audio_clip = AudioFileClip(audio_file)
                video_duration = audio_clip.duration
            else:
                video_duration = 480  # 8 minutes fallback
            
            # Create video clips
            clips = []
            
            # Title screen (5 seconds)
            title_clip = self.create_title_screen(content['title'], 5)
            clips.append(title_clip)
            
            # Main content with facts and visuals
            content_clips = self.create_content_clips(content, video_duration - 10)
            clips.extend(content_clips)
            
            # Subscribe reminder screen (5 seconds)
            outro_clip = self.create_outro_screen(5)
            clips.append(outro_clip)
            
            # Combine all clips
            final_video = concatenate_videoclips(clips)
            
            # Add audio
            if audio_file:
                final_video = final_video.set_audio(audio_clip)
            
            # Add background music (optional)
            final_video = self.add_background_music(final_video)
            
            # Export video
            output_file = os.path.join(self.output_dir, f"long_form_{content['category']}_{random.randint(1000, 9999)}.mp4")
            final_video.write_videofile(
                output_file,
                fps=self.youtube_long_specs['fps'],
                codec='libx264',
                audio_codec='aac'
            )
            
            # Cleanup
            final_video.close()
            if audio_file:
                audio_clip.close()
            
            return output_file
            
        except Exception as e:
            logging.error(f"Error creating long-form video: {str(e)}")
            return None
    
    def create_short_form_video(self, content: Dict, audio_file: str) -> str:
        """Create 30-60 second vertical video for Shorts/Reels"""
        try:
            # Create condensed script for short form
            short_script = self.condense_script_for_shorts(content)
            
            # Create short voiceover
            if short_script:
                short_tts = gTTS(text=short_script, lang='en', slow=False)
                short_audio_file = os.path.join(self.temp_dir, f"short_audio_{random.randint(1000, 9999)}.mp3")
                short_tts.save(short_audio_file)
                
                short_audio = AudioFileClip(short_audio_file)
                video_duration = min(short_audio.duration, 60)  # Max 60 seconds
            else:
                video_duration = 45  # Fallback duration
                short_audio = None
            
            # Create vertical video clips
            clips = []
            
            # Hook + top 3 facts only for shorts
            hook_clip = self.create_vertical_text_clip(content['script']['hook'], 3)
            clips.append(hook_clip)
            
            # Top 3 facts with quick visuals
            for i in range(min(3, len(content['raw_data']['data']))):
                fact_clip = self.create_vertical_fact_clip(content['raw_data']['data'][i], i+1, 10)
                clips.append(fact_clip)
            
            # Quick CTA
            cta_clip = self.create_vertical_text_clip("Follow for more amazing facts!", 5)
            clips.append(cta_clip)
            
            # Combine clips
            final_video = concatenate_videoclips(clips)
            
            # Resize to vertical format
            final_video = final_video.resize(self.shorts_specs['resolution'])
            
            # Add audio if available
            if short_audio:
                final_video = final_video.set_audio(short_audio)
            
            # Export
            output_file = os.path.join(self.output_dir, f"short_form_{content['category']}_{random.randint(1000, 9999)}.mp4")
            final_video.write_videofile(
                output_file,
                fps=self.shorts_specs['fps'],
                codec='libx264',
                audio_codec='aac'
            )
            
            # Cleanup
            final_video.close()
            if short_audio:
                short_audio.close()
            
            return output_file
            
        except Exception as e:
            logging.error(f"Error creating short-form video: {str(e)}")
            return None
    
    def create_title_screen(self, title: str, duration: int) -> VideoClip:
        """Create animated title screen"""
        # Create background
        bg_color = (20, 25, 40)  # Dark blue background
        img = Image.new('RGB', self.youtube_long_specs['resolution'], bg_color)
        
        # Add title text
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("assets/fonts/arial-bold.ttf", 72)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        wrapped_title = textwrap.fill(title, width=25)
        
        # Calculate text position (center)
        bbox = draw.textbbox((0, 0), wrapped_title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.youtube_long_specs['resolution'][0] - text_width) // 2
        y = (self.youtube_long_specs['resolution'][1] - text_height) // 2
        
        # Add text with shadow effect
        draw.text((x+3, y+3), wrapped_title, font=font, fill=(0, 0, 0))  # Shadow
        draw.text((x, y), wrapped_title, font=font, fill=(255, 255, 255))  # Main text
        
        # Save temporary image
        temp_img_path = os.path.join(self.temp_dir, f"title_{random.randint(1000, 9999)}.png")
        img.save(temp_img_path)
        
        # Create video clip
        title_clip = ImageClip(temp_img_path, duration=duration)
        
        # Add fade in/out effects
        title_clip = title_clip.fadein(0.5).fadeout(0.5)
        
        return title_clip
    
    def create_content_clips(self, content: Dict, total_duration: float) -> List[VideoClip]:
        """Create main content clips with facts and visuals"""
        clips = []
        data_items = content['raw_data']['data'][:10]  # Top 10 items
        
        clip_duration = total_duration / len(data_items)  # Equal time per fact
        
        for i, item in enumerate(data_items):
            # Create fact clip
            fact_clip = self.create_fact_clip(item, i+1, clip_duration)
            clips.append(fact_clip)
        
        return clips
    
    def create_fact_clip(self, fact_data: Dict, number: int, duration: float) -> VideoClip:
        """Create individual fact clip with visuals"""
        # Background image (stock photo or solid color)
        bg_image = self.get_background_image(fact_data)
        
        if bg_image:
            background = ImageClip(bg_image, duration=duration)
        else:
            # Create colored background
            bg_color = random.choice([(50, 70, 100), (70, 50, 100), (100, 70, 50)])
            bg_img = Image.new('RGB', self.youtube_long_specs['resolution'], bg_color)
            bg_path = os.path.join(self.temp_dir, f"bg_{random.randint(1000, 9999)}.png")
            bg_img.save(bg_path)
            background = ImageClip(bg_path, duration=duration)
        
        # Resize to fit screen
        background = background.resize(self.youtube_long_specs['resolution'])
        
        # Create text overlay
        fact_text = self.format_fact_for_display(fact_data, number)
        text_clip = self.create_text_overlay(fact_text, duration)
        
        # Combine background and text
        final_clip = CompositeVideoClip([background, text_clip])
        
        return final_clip
    
    def get_background_image(self, fact_data: Dict) -> str:
        """Get relevant background image (placeholder - can integrate with Unsplash API)"""
        # This is a placeholder - you can integrate with Unsplash API for relevant images
        return None
    
    def format_fact_for_display(self, fact_data: Dict, number: int) -> str:
        """Format fact data for on-screen display"""
        if 'name' in fact_data:
            return f"#{number} {fact_data['name']}\n\n{fact_data.get('interesting_fact', '')}"
        elif 'topic' in fact_data:
            return f"#{number} {fact_data['topic']}\n\n{fact_data.get('summary', '')[:200]}..."
        else:
            return f"#{number}\n\n{str(fact_data)}"

    def create_text_overlay(self, text: str, duration: float) -> VideoClip:
        """Create text overlay for facts"""
        img = Image.new('RGBA', self.youtube_long_specs['resolution'], (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("assets/fonts/arial-bold.ttf", 48)
            body_font = ImageFont.truetype("assets/fonts/arial.ttf", 36)
        except:
            title_font = body_font = ImageFont.load_default()
        
        # Split into title and body
        parts = text.split('\n\n')
        title = parts[0]
        body = '\n\n'.join(parts[1:]) if len(parts) > 1 else ''
        
        # Calculate positions
        padding = 20
        title_y = 50
        body_y = title_y + 100
        
        # Draw title with shadow
        draw.text((padding+2, title_y+2), title, font=title_font, fill=(0, 0, 0, 200))
        draw.text((padding, title_y), title, font=title_font, fill=(255, 255, 255, 255))
        
        # Draw body text with shadow
        wrapped_body = textwrap.fill(body, width=50)
        draw.text((padding+2, body_y+2), wrapped_body, font=body_font, fill=(0, 0, 0, 200))
        draw.text((padding, body_y), wrapped_body, font=body_font, fill=(255, 255, 255, 255))
        
        # Save temporary image
        temp_img_path = os.path.join(self.temp_dir, f"text_{random.randint(1000, 9999)}.png")
        img.save(temp_img_path)
        
        # Create video clip
        text_clip = ImageClip(temp_img_path, duration=duration)
        
        # Add subtle animations
        text_clip = text_clip.fadein(0.5).fadeout(0.5)
        
        return text_clip

    def create_outro_screen(self, duration: int) -> VideoClip:
        """Create outro screen with subscribe reminder"""
        img = Image.new('RGB', self.youtube_long_specs['resolution'], (20, 25, 40))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("assets/fonts/arial-bold.ttf", 60)
        except:
            font = ImageFont.load_default()
        
        # Add subscribe text
        text = "Subscribe for more amazing facts!"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.youtube_long_specs['resolution'][0] - text_width) // 2
        y = (self.youtube_long_specs['resolution'][1] - text_height) // 2
        
        draw.text((x+3, y+3), text, font=font, fill=(0, 0, 0))
        draw.text((x, y), text, font=font, fill=(255, 255, 255))
        
        # Save temporary image
        temp_img_path = os.path.join(self.temp_dir, f"outro_{random.randint(1000, 9999)}.png")
        img.save(temp_img_path)
        
        # Create video clip with fade effects
        outro_clip = ImageClip(temp_img_path, duration=duration)
        outro_clip = outro_clip.fadein(0.5).fadeout(0.5)
        
        return outro_clip

    def create_vertical_text_clip(self, text: str, duration: float) -> VideoClip:
        """Create text clip for vertical short-form videos"""
        img = Image.new('RGB', self.shorts_specs['resolution'], (20, 25, 40))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("assets/fonts/arial-bold.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Wrap text for vertical format
        wrapped_text = textwrap.fill(text, width=20)
        
        # Center text
        bbox = draw.textbbox((0, 0), wrapped_text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.shorts_specs['resolution'][0] - text_width) // 2
        y = (self.shorts_specs['resolution'][1] - text_height) // 2
        
        # Add text with shadow
        draw.text((x+2, y+2), wrapped_text, font=font, fill=(0, 0, 0))
        draw.text((x, y), wrapped_text, font=font, fill=(255, 255, 255))
        
        # Save temporary image
        temp_img_path = os.path.join(self.temp_dir, f"vertical_text_{random.randint(1000, 9999)}.png")
        img.save(temp_img_path)
        
        # Create video clip
        text_clip = ImageClip(temp_img_path, duration=duration)
        text_clip = text_clip.fadein(0.3).fadeout(0.3)
        
        return text_clip

    def create_vertical_fact_clip(self, fact_data: Dict, number: int, duration: float) -> VideoClip:
        """Create vertical fact clip for short-form videos"""
        # Create background
        img = Image.new('RGB', self.shorts_specs['resolution'], (20, 25, 40))
        draw = ImageDraw.Draw(img)
        
        try:
            title_font = ImageFont.truetype("assets/fonts/arial-bold.ttf", 36)
            body_font = ImageFont.truetype("assets/fonts/arial.ttf", 30)
        except:
            title_font = body_font = ImageFont.load_default()
        
        # Format text
        title = f"#{number}"
        fact_text = self.format_fact_for_display(fact_data, number).split('\n\n')[1]
        wrapped_fact = textwrap.fill(fact_text, width=25)
        
        # Position text
        title_y = 50
        fact_y = 150
        
        # Draw title with shadow
        draw.text((20+2, title_y+2), title, font=title_font, fill=(0, 0, 0))
        draw.text((20, title_y), title, font=title_font, fill=(255, 255, 255))
        
        # Draw fact with shadow
        draw.text((20+2, fact_y+2), wrapped_fact, font=body_font, fill=(0, 0, 0))
        draw.text((20, fact_y), wrapped_fact, font=body_font, fill=(255, 255, 255))
        
        # Save temporary image
        temp_img_path = os.path.join(self.temp_dir, f"vertical_fact_{random.randint(1000, 9999)}.png")
        img.save(temp_img_path)
        
        # Create video clip
        clip = ImageClip(temp_img_path, duration=duration)
        clip = clip.fadein(0.3).fadeout(0.3)
        
        return clip

    def add_background_music(self, video_clip: VideoClip) -> VideoClip:
        """Add background music to video"""
        try:
            # Load background music from assets
            bg_music_path = os.path.join(self.assets_dir, 'background_music.mp3')
            if os.path.exists(bg_music_path):
                bg_music = AudioFileClip(bg_music_path)
                
                # Loop music if needed
                if bg_music.duration < video_clip.duration:
                    bg_music = afx.audio_loop(bg_music, duration=video_clip.duration)
                else:
                    bg_music = bg_music.subclip(0, video_clip.duration)
                
                # Reduce volume for background
                bg_music = bg_music.volumex(0.1)
                
                # Combine with existing audio
                if video_clip.audio is not None:
                    final_audio = CompositeAudioClip([video_clip.audio, bg_music])
                    video_clip = video_clip.set_audio(final_audio)
                else:
                    video_clip = video_clip.set_audio(bg_music)
            
        except Exception as e:
            logging.warning(f"Could not add background music: {str(e)}")
        
        return video_clip

    def condense_script_for_shorts(self, content: Dict) -> str:
        """Create condensed script version for short-form video"""
        try:
            script_parts = []
            
            # Add hook
            script_parts.append(content['script']['hook'])
            
            # Add first 3 facts
            data_items = content['raw_data']['data'][:3]
            for i, item in enumerate(data_items, 1):
                if isinstance(item, dict):
                    if 'name' in item:
                        fact = f"Number {i}: {item['name']}. {item.get('interesting_fact', '')}"
                    elif 'topic' in item:
                        fact = f"Number {i}: {item['topic']}. {item.get('summary', '')[:100]}..."
                    else:
                        fact = f"Number {i}: {str(item)}"
                    script_parts.append(fact)
            
            # Add quick CTA
            script_parts.append("Follow for more amazing facts!")
            
            return " ".join(script_parts)
            
        except Exception as e:
            logging.error(f"Error creating short script: {str(e)}")
            return None