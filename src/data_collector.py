# data_collector.py - Data collection from various sources
import os, logging
import requests
import wikipedia
import random
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)


class DataCollector:
    def __init__(self):
        self.wikipedia_api = "https://en.wikipedia.org/api/rest_v1/"
        self.countries_api = "https://restcountries.com/v3.1/"
        self.nasa_api_key = os.getenv('NASA_API_KEY', 'DEMO_KEY')
        
    def get_topic_data(self, category: str) -> Dict[str, Any]:
        """Get data based on topic category"""
        if category == 'geography':
            return self.get_geography_data()
        elif category == 'history':
            return self.get_history_data()
        elif category == 'science':
            return self.get_science_data()
        elif category == 'space':
            return self.get_space_data()
        elif category == 'technology':
            return self.get_technology_data()
        elif category == 'psychology':
            return self.get_psychology_data()
        else:
            return self.get_trending_data()
    
    def get_geography_data(self) -> Dict[str, Any]:
        """Collect geography and country facts"""
        try:
            # Get all countries
            response = requests.get(f"{self.countries_api}all")
            countries = response.json()
            
            # Select interesting countries with unique facts
            interesting_facts = []
            
            for country in random.sample(countries, 15):  # Get 15 random countries
                fact_data = {
                    'name': country.get('name', {}).get('common', 'Unknown'),
                    'capital': country.get('capital', ['Unknown'])[0] if country.get('capital') else 'Unknown',
                    'population': country.get('population', 0),
                    'area': country.get('area', 0),
                    'region': country.get('region', 'Unknown'),
                    'languages': list(country.get('languages', {}).values()) if country.get('languages') else [],
                    'currencies': list(country.get('currencies', {}).keys()) if country.get('currencies') else [],
                    'flag': country.get('flags', {}).get('png', ''),
                    'interesting_fact': self.get_country_interesting_fact(country.get('name', {}).get('common', ''))
                }
                interesting_facts.append(fact_data)
            
            return {
                'category': 'geography',
                'data': interesting_facts[:10],  # Top 10 for the list
                'metadata': {
                    'total_countries': len(countries),
                    'data_source': 'REST Countries API'
                }
            }
            
        except Exception as e:
            logging.error(f"Error collecting geography data: {str(e)}")
            return self.get_fallback_geography_data()
    
    def get_country_interesting_fact(self, country_name: str) -> str:
        """Get an interesting fact about a country using Wikipedia"""
        try:
            page = wikipedia.page(country_name, auto_suggest=False)
            summary = page.summary
            
            # Extract interesting sentences (simple approach)
            sentences = summary.split('.')
            interesting_sentences = [s.strip() for s in sentences if len(s.strip()) > 50 and len(s.strip()) < 200]
            
            return random.choice(interesting_sentences) if interesting_sentences else "This country has a rich history and culture."
            
        except:
            return f"{country_name} has unique geographical and cultural features."
    
    def get_history_data(self) -> Dict[str, Any]:
        """Collect historical facts and events"""
        historical_topics = [
            "Ancient Egypt", "Roman Empire", "World War II", "Renaissance", 
            "Industrial Revolution", "Cold War", "Ancient Greece", "Viking Age",
            "Mongol Empire", "American Revolution"
        ]
        
        historical_facts = []
        
        for topic in random.sample(historical_topics, 10):
            try:
                page = wikipedia.page(topic)
                summary = page.summary
                
                fact_data = {
                    'topic': topic,
                    'summary': summary[:300] + "..." if len(summary) > 300 else summary,
                    'interesting_fact': self.extract_interesting_fact(summary),
                    'url': page.url
                }
                historical_facts.append(fact_data)
                
            except Exception as e:
                logging.warning(f"Could not fetch data for {topic}: {str(e)}")
        
        return {
            'category': 'history',
            'data': historical_facts,
            'metadata': {
                'topics_covered': len(historical_facts),
                'data_source': 'Wikipedia API'
            }
        }
    
    def get_science_data(self) -> Dict[str, Any]:
        """Collect science facts and discoveries"""
        science_topics = [
            "Quantum physics", "DNA", "Theory of relativity", "Evolution",
            "Photosynthesis", "Black holes", "Antibiotics", "Periodic table",
            "Genetics", "Climate change"
        ]
        
        science_facts = []
        
        for topic in random.sample(science_topics, 10):
            try:
                page = wikipedia.page(topic)
                summary = page.summary
                
                fact_data = {
                    'topic': topic,
                    'summary': summary[:250] + "..." if len(summary) > 250 else summary,
                    'discovery_year': self.extract_year_from_text(summary),
                    'importance': self.generate_importance_statement(topic)
                }
                science_facts.append(fact_data)
                
            except Exception as e:
                logging.warning(f"Could not fetch data for {topic}: {str(e)}")
        
        return {
            'category': 'science',
            'data': science_facts,
            'metadata': {
                'topics_covered': len(science_facts),
                'data_source': 'Wikipedia API'
            }
        }
    
    def extract_interesting_fact(self, text: str) -> str:
        """Extract an interesting fact from a larger text"""
        sentences = text.split('.')
        # Look for sentences with numbers, superlatives, or surprising facts
        interesting_keywords = ['first', 'largest', 'smallest', 'only', 'never', 'most', 'least', 'discovered', 'invented']
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in interesting_keywords):
                if 20 < len(sentence.strip()) < 150:
                    return sentence.strip()
        
        # Fallback to first meaningful sentence
        for sentence in sentences:
            if 20 < len(sentence.strip()) < 150:
                return sentence.strip()
        
        return text[:150] + "..." if len(text) > 150 else text

    def extract_year_from_text(self, text: str) -> str:
        """Extract year from text using simple regex"""
        import re
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        return years[0] if years else "Unknown"
    
    def generate_importance_statement(self, topic: str) -> str:
        """Generate importance statement for scientific topics"""
        importance_templates = [
            f"{topic} revolutionized our understanding of the natural world.",
            f"The discovery of {topic} changed the course of scientific history.",
            f"{topic} remains one of the most important concepts in modern science.",
            f"Understanding {topic} is crucial for advancing human knowledge."
        ]
        return random.choice(importance_templates)

    def get_space_data(self) -> Dict[str, Any]:
        """Collect space and astronomy facts using NASA API and Wikipedia"""
        try:
            space_topics = [
                "Black hole", "Solar System", "Mars exploration", "International Space Station",
                "Hubble Space Telescope", "Space exploration", "Milky Way", "Supernova",
                "Exoplanet", "Dark matter"
            ]
            
            space_facts = []
            
            # Get NASA APOD (Astronomy Picture of the Day)
            nasa_response = requests.get(
                f"https://api.nasa.gov/planetary/apod?api_key={self.nasa_api_key}"
            )
            if nasa_response.status_code == 200:
                apod_data = nasa_response.json()
                space_facts.append({
                    'topic': 'NASA Picture of the Day',
                    'title': apod_data.get('title', ''),
                    'explanation': apod_data.get('explanation', ''),
                    'image_url': apod_data.get('url', ''),
                    'date': apod_data.get('date', '')
                })
            
            # Get Wikipedia space facts
            for topic in random.sample(space_topics, 5):
                try:
                    page = wikipedia.page(topic)
                    fact_data = {
                        'topic': topic,
                        'summary': page.summary[:300] + "..." if len(page.summary) > 300 else page.summary,
                        'interesting_fact': self.extract_interesting_fact(page.summary),
                        'url': page.url
                    }
                    space_facts.append(fact_data)
                except Exception as e:
                    continue
            
            return {
                'category': 'space',
                'data': space_facts,
                'metadata': {
                    'topics_covered': len(space_facts),
                    'data_source': ['NASA API', 'Wikipedia']
                }
            }
            
        except Exception as e:
            logging.error(f"Error collecting space data: {str(e)}")
            return self.get_fallback_space_data()

    def get_technology_data(self) -> Dict[str, Any]:
        """Collect technology facts and innovations"""
        try:
            tech_topics = [
                "Artificial Intelligence", "Quantum Computing", "Blockchain",
                "Internet of Things", "5G technology", "Cloud computing",
                "Machine Learning", "Virtual Reality", "Robotics", "Cybersecurity"
            ]
            
            tech_facts = []
            
            for topic in random.sample(tech_topics, 10):
                try:
                    page = wikipedia.page(topic)
                    fact_data = {
                        'topic': topic,
                        'summary': page.summary[:250] + "..." if len(page.summary) > 250 else page.summary,
                        'latest_developments': self.extract_interesting_fact(page.content),
                        'impact': self.generate_tech_impact_statement(topic)
                    }
                    tech_facts.append(fact_data)
                except Exception as e:
                    continue
            
            return {
                'category': 'technology',
                'data': tech_facts,
                'metadata': {
                    'topics_covered': len(tech_facts),
                    'data_source': 'Wikipedia'
                }
            }
            
        except Exception as e:
            logging.error(f"Error collecting technology data: {str(e)}")
            return self.get_fallback_technology_data()

    def get_psychology_data(self) -> Dict[str, Any]:
        """Collect psychology facts and theories"""
        try:
            psych_topics = [
                "Cognitive psychology", "Behavioral psychology", "Social psychology",
                "Developmental psychology", "Personality theory", "Mental health",
                "Psychological theories", "Human behavior", "Memory", "Emotions"
            ]
            
            psych_facts = []
            
            for topic in random.sample(psych_topics, 10):
                try:
                    page = wikipedia.page(topic)
                    fact_data = {
                        'topic': topic,
                        'summary': page.summary[:300] + "..." if len(page.summary) > 300 else page.summary,
                        'key_concepts': self.extract_interesting_fact(page.content),
                        'significance': self.generate_psychology_impact(topic)
                    }
                    psych_facts.append(fact_data)
                except Exception as e:
                    continue
            
            return {
                'category': 'psychology',
                'data': psych_facts,
                'metadata': {
                    'topics_covered': len(psych_facts),
                    'data_source': 'Wikipedia'
                }
            }
            
        except Exception as e:
            logging.error(f"Error collecting psychology data: {str(e)}")
            return self.get_fallback_psychology_data()

    def get_trending_data(self) -> Dict[str, Any]:
        """Collect trending topics and current events"""
        try:
            # Combine facts from different categories
            categories = ['science', 'history', 'geography', 'space', 'technology']
            trending_facts = []
            
            for category in random.sample(categories, 3):
                if category == 'science':
                    data = self.get_science_data()
                elif category == 'history':
                    data = self.get_history_data()
                elif category == 'geography':
                    data = self.get_geography_data()
                elif category == 'space':
                    data = self.get_space_data()
                else:
                    data = self.get_technology_data()
                
                if data and 'data' in data:
                    trending_facts.extend(data['data'][:3])
            
            # Shuffle and limit to 10 facts
            random.shuffle(trending_facts)
            trending_facts = trending_facts[:10]
            
            return {
                'category': 'trending',
                'data': trending_facts,
                'metadata': {
                    'topics_covered': len(trending_facts),
                    'data_source': 'Mixed Sources'
                }
            }
            
        except Exception as e:
            logging.error(f"Error collecting trending data: {str(e)}")
            return self.get_fallback_trending_data()

    def get_fallback_geography_data(self) -> Dict[str, Any]:
        """Fallback data when geography API fails"""
        fallback_facts = [
            {
                'name': 'United States',
                'capital': 'Washington, D.C.',
                'population': 331002651,
                'area': 9833517,
                'interesting_fact': 'The United States is home to all of Earth\'s five climate types.'
            },
            {
                'name': 'China',
                'capital': 'Beijing',
                'population': 1439323776,
                'area': 9596961,
                'interesting_fact': 'The Great Wall of China is not visible from space with the naked eye.'
            },
            {
                'name': 'Brazil',
                'capital': 'Brasília',
                'population': 212559417,
                'area': 8515770,
                'interesting_fact': 'Brazil contains about 60% of the Amazon Rainforest.'
            }
        ]
        
        return {
            'category': 'geography',
            'data': fallback_facts,
            'metadata': {
                'total_countries': 3,
                'data_source': 'Fallback Data'
            }
        }

    def get_fallback_space_data(self) -> Dict[str, Any]:
        """Fallback data when space APIs fail"""
        fallback_facts = [
            {
                'topic': 'Solar System',
                'summary': 'Our Solar System consists of eight planets orbiting around the Sun.',
                'interesting_fact': 'If the Sun were as tall as a typical front door, Earth would be the size of a nickel.'
            },
            {
                'topic': 'Mars',
                'summary': 'Mars is often called the Red Planet due to its reddish appearance.',
                'interesting_fact': 'Mars has the largest dust storms in our solar system.'
            }
        ]
        
        return {
            'category': 'space',
            'data': fallback_facts,
            'metadata': {
                'topics_covered': 2,
                'data_source': 'Fallback Data'
            }
        }

    def get_fallback_technology_data(self) -> Dict[str, Any]:
        """Fallback data when technology data collection fails"""
        fallback_facts = [
            {
                'topic': 'Artificial Intelligence',
                'summary': 'AI is the simulation of human intelligence by machines.',
                'latest_developments': 'AI systems can now generate human-like text and images.',
                'impact': 'AI is transforming industries from healthcare to transportation.'
            },
            {
                'topic': 'Quantum Computing',
                'summary': 'Quantum computers use quantum mechanics to process information.',
                'latest_developments': 'Companies are developing quantum computers with increasing numbers of qubits.',
                'impact': 'Quantum computing could revolutionize cryptography and drug discovery.'
            }
        ]
        
        return {
            'category': 'technology',
            'data': fallback_facts,
            'metadata': {
                'topics_covered': 2,
                'data_source': 'Fallback Data'
            }
        }

    def get_fallback_psychology_data(self) -> Dict[str, Any]:
        """Fallback data when psychology data collection fails"""
        fallback_facts = [
            {
                'topic': 'Cognitive Psychology',
                'summary': 'Cognitive psychology studies mental processes including thinking, learning, and memory.',
                'key_concepts': 'Memory formation and retrieval are complex processes involving multiple brain regions.',
                'significance': 'Understanding cognitive processes helps improve learning and decision-making.'
            },
            {
                'topic': 'Social Psychology',
                'summary': 'Social psychology examines how people\'s thoughts and behaviors are influenced by others.',
                'key_concepts': 'Group dynamics and social influence play crucial roles in human behavior.',
                'significance': 'Social psychology insights help improve communication and relationships.'
            }
        ]
        
        return {
            'category': 'psychology',
            'data': fallback_facts,
            'metadata': {
                'topics_covered': 2,
                'data_source': 'Fallback Data'
            }
        }

    def get_fallback_trending_data(self) -> Dict[str, Any]:
        """Fallback data when trending data collection fails"""
        fallback_facts = [
            {
                'topic': 'Climate Change',
                'summary': 'Global temperatures continue to rise due to human activities.',
                'interesting_fact': 'The last decade was the warmest on record.'
            },
            {
                'topic': 'Space Exploration',
                'summary': 'Private companies are making space travel more accessible.',
                'interesting_fact': 'Reusable rockets have significantly reduced the cost of space launches.'
            }
        ]
        
        return {
            'category': 'trending',
            'data': fallback_facts,
            'metadata': {
                'topics_covered': 2,
                'data_source': 'Fallback Data'
            }
        }

    def generate_tech_impact_statement(self, topic: str) -> str:
        """Generate impact statement for technology topics"""
        impact_templates = [
            f"{topic} is revolutionizing how we live and work.",
            f"The impact of {topic} on society is profound and far-reaching.",
            f"{topic} represents a major breakthrough in technological advancement.",
            f"The development of {topic} marks a new era in human innovation."
        ]
        return random.choice(impact_templates)

    def generate_psychology_impact(self, topic: str) -> str:
        """Generate impact statement for psychology topics"""
        impact_templates = [
            f"Understanding {topic} helps us improve mental health and well-being.",
            f"Research in {topic} has transformed our understanding of human behavior.",
            f"{topic} provides crucial insights into human development and behavior.",
            f"The study of {topic} continues to enhance our understanding of the mind."
        ]
        return random.choice(impact_templates)

