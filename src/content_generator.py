""" For Generating engaging scripts from data """
import os
# import logging
import openai
import random
from typing import Dict, List, Any

# logging.basicConfig(level=logging.INFO)


class ContentGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        
        # Title templates for viral appeal
        self.title_templates = {
            'geography': [
                "10 Countries That Technically Don't Exist",
                "Mind-Blowing Facts About {} Countries",
                "Countries With the Weirdest Laws You Won't Believe",
                "10 Places on Earth That Look Like Another Planet"
            ],
            'history': [
                "Historical Events That Changed Everything",
                "10 Mysteries From History We Still Can't Solve", 
                "Shocking Facts About {} That Schools Don't Teach",
                "Historical Figures Who Were Actually Terrible People"
            ],
            'science': [
                "Scientific Facts That Will Blow Your Mind",
                "10 Scientific Discoveries That Shocked the World",
                "Science Facts That Sound Fake But Are True",
                "Mind-Bending Scientific Phenomena Explained"
            ]
        }
        
        # Hook templates to grab attention
        self.hooks = [
            "You won't believe what I discovered about {}...",
            "Most people have no idea that {}...",
            "This is going to completely change how you think about {}...",
            "I spent hours researching this, and what I found shocked me...",
            "Number 3 on this list will absolutely blow your mind..."
        ]
    
    def create_list_content(self, raw_data: Dict, category: str) -> Dict[str, Any]:
        """Generate complete content from raw data"""
        
        # Generate engaging title
        title = self.generate_title(raw_data, category)
        
        # Generate script with hook, list items, and conclusion
        script = self.generate_script(raw_data, title, category)
        
        # Generate metadata for SEO
        metadata = self.generate_metadata(title, category)
        
        return {
            'title': title,
            'script': script,
            'category': category,
            'metadata': metadata,
            'raw_data': raw_data,
            'estimated_duration': self.estimate_duration(script)
        }
    
    def generate_title(self, data: Dict, category: str) -> str:
        """Generate viral-friendly title"""
        templates = self.title_templates.get(category, ["10 Amazing Facts About {}"])
        template = random.choice(templates)
        
        if category == 'geography':
            return template.format(random.choice(['Amazing', 'Incredible', 'Shocking']))
        elif category == 'history':  
            return template.format(random.choice(['Ancient Times', 'The Past', 'World History']))
        else:
            return template
    
    def generate_script(self, data: Dict, title: str, category: str) -> Dict[str, str]:
        """Generate complete video script"""
        
        # Hook (first 5 seconds)
        hook = random.choice(self.hooks).format(category)
        
        # Introduction
        intro = f"Welcome back to the channel! Today we're diving into {title.lower()}. Make sure to subscribe and hit that notification bell because this content is absolutely mind-blowing!"
        
        # Main content (list items)
        list_items = self.generate_list_items(data['data'])
        
        # Conclusion and CTA
        conclusion = "Which fact surprised you the most? Let me know in the comments below! And if you enjoyed this video, smash that like button and subscribe for more incredible content like this!"
        
        return {
            'hook': hook,
            'intro': intro,
            'list_items': list_items,
            'conclusion': conclusion,
            'full_script': f"{hook} {intro} {list_items} {conclusion}"
        }
    
    def generate_list_items(self, data_items: List[Dict]) -> str:
        """Generate list items with engaging narration"""
        list_script = ""
        
        for i, item in enumerate(data_items[:10], 1):  # Top 10 list
            if isinstance(item, dict):
                item_script = self.format_list_item(i, item)
                list_script += item_script + " "
        
        return list_script
    
    def format_list_item(self, number: int, item: Dict) -> str:
        """Format individual list item"""
        if 'name' in item:  # Geography item
            return f"Number {number}: {item['name']}. {item.get('interesting_fact', 'This country has unique features.')} With a population of {self.format_number(item.get('population', 0))}, it's truly fascinating."
        
        elif 'topic' in item:  # History/Science item  
            return f"Number {number}: {item['topic']}. {item.get('summary', 'This topic is incredibly important.')} {item.get('importance', '')}"
        
        else:
            return f"Number {number}: {str(item)}"
    
    def format_number(self, num: int) -> str:
        """Format large numbers for readability"""
        if num >= 1_000_000:
            return f"{num/1_000_000:.1f} million"
        elif num >= 1_000:
            return f"{num/1_000:.1f} thousand"
        else:
            return str(num)
    
    def generate_metadata(self, title: str, category: str) -> Dict[str, Any]:
        """Generate SEO metadata"""
        tags = {
            'geography': ['countries', 'geography', 'world facts', 'travel', 'educational'],
            'history': ['history', 'historical facts', 'ancient', 'past events', 'educational'],
            'science': ['science', 'scientific facts', 'discoveries', 'research', 'educational'],
            'space': ['space', 'astronomy', 'nasa', 'universe', 'cosmos'],
            'technology': ['technology', 'tech facts', 'innovation', 'future', 'gadgets']
        }
        
        description = f"Discover amazing facts in this educational video about {category}. {title} - Subscribe for more incredible content!"
        
        return {
            'description': description,
            'tags': tags.get(category, ['educational', 'facts', 'top 10']),
            'thumbnail_text': f"TOP 10\n{category.upper()}\nFACTS"
        }
    
    def estimate_duration(self, script: Dict) -> int:
        """Estimate video duration in seconds"""
        # Rough estimation: 150 words per minute
        word_count = len(script['full_script'].split())
        return int((word_count / 150) * 60)