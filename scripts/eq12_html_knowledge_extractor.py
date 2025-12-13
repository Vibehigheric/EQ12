#!/usr/bin/env python3
"""
EQ12 HTML.com Knowledge Extractor - Specialized Learning System
Professional Engineering Grade HTML Tutorial Analysis

Author: EQ12 Engineering Team
Version: 2.1.0
Date: 2025-11-22
Python: 3.12+

This script provides specialized analysis of HTML.com content for learning acceleration:
- Extracts HTML tutorials and code examples
- Analyzes learning progression and dependencies
- Creates structured knowledge maps for curriculum building
- Generates practice exercises and validation tests
- Integrates with EQ12 learning management system

Usage Examples:
  python eq12_html_knowledge_extractor.py --analyze-tutorials
  python eq12_html_knowledge_extractor.py --extract-code-examples
  python eq12_html_knowledge_extractor.py --build-curriculum

Teaching Notes (30-Day Python Curriculum Integration):
- Web content analysis (Day 24): Advanced content extraction and processing
- Knowledge management (Day 28): Structured learning data organization
- Pattern recognition (Day 26): Identifying learning patterns and dependencies
- Data visualization (Day 29): Creating learning progression visualizations
"""

import os
import re
import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Set, Tuple, Optional, Union
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict

import requests
from bs4 import BeautifulSoup, NavigableString

# Import our base crawler
try:
    from eq12_html_crawler import EQ12HTMLCrawler
except ImportError:
    print("Error: eq12_html_crawler.py must be in the same directory")
    sys.exit(1)

@dataclass
class HTMLTutorial:
    """Data class for HTML tutorial information"""
    title: str
    url: str
    difficulty: str
    topics: List[str]
    code_examples: List[Dict]
    prerequisites: List[str]
    learning_objectives: List[str]
    estimated_time: int  # minutes

@dataclass
class CodeExample:
    """Data class for code examples"""
    language: str
    code: str
    explanation: str
    output: str
    difficulty: str
    tags: List[str]

class EQ12HTMLKnowledgeExtractor:
    """
    Professional HTML.com content analyzer and knowledge extractor

    Teaching note (Day 20 - Classes): Specialized content analysis class
    that builds on the base crawler for domain-specific extraction.
    """

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the HTML knowledge extractor"""
        self.data_dir = data_dir or Path('C:/EQ12/data/html_knowledge')
        self.setup_directories()

        # Initialize base crawler
        crawler_config = {
            'data_dir': self.data_dir / 'raw_crawl',
            'max_pages': 500,  # HTML.com is well-structured
            'max_depth': 8,
            'request_delay': 1.0,  # Be respectful
            'extract_knowledge': True,
            'create_index': True
        }

        self.crawler = EQ12HTMLCrawler('https://html.com', crawler_config)

        # Knowledge structures
        self.tutorials: List[HTMLTutorial] = []
        self.code_examples: List[CodeExample] = []
        self.topic_hierarchy: Dict[str, List[str]] = {}
        self.learning_progression: List[str] = []

        # HTML learning patterns
        self.html_patterns = {
            'basic_tags': ['html', 'head', 'body', 'title', 'h1', 'h2', 'h3', 'p', 'div', 'span'],
            'text_formatting': ['strong', 'em', 'b', 'i', 'u', 'small', 'mark', 'sub', 'sup'],
            'links_media': ['a', 'img', 'video', 'audio', 'iframe', 'object', 'embed'],
            'lists_tables': ['ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'thead', 'tbody'],
            'forms_inputs': ['form', 'input', 'textarea', 'select', 'option', 'button', 'label'],
            'semantic_html': ['header', 'nav', 'main', 'article', 'section', 'aside', 'footer'],
            'advanced': ['canvas', 'svg', 'details', 'summary', 'progress', 'meter']
        }

        # Learning progression map
        self.progression_map = {
            'beginner': ['basic_tags', 'text_formatting'],
            'intermediate': ['links_media', 'lists_tables', 'forms_inputs'],
            'advanced': ['semantic_html', 'advanced']
        }

        print(f"EQ12 HTML Knowledge Extractor initialized")
        print(f"Data directory: {self.data_dir}")

    def setup_directories(self):
        """Create necessary directories"""
        dirs = [
            self.data_dir,
            self.data_dir / 'tutorials',
            self.data_dir / 'code_examples',
            self.data_dir / 'curriculum',
            self.data_dir / 'analysis',
            self.data_dir / 'raw_crawl'
        ]

        for directory in dirs:
            directory.mkdir(parents=True, exist_ok=True)

    def crawl_html_com(self) -> Dict:
        """Crawl HTML.com and extract content"""
        print("🕷️ Crawling HTML.com for learning content...")

        crawl_results = self.crawler.crawl_parallel()

        print(f"✅ Crawled {crawl_results['stats']['pages_crawled']} pages")
        print(f"📚 Knowledge index created with {len(self.crawler.knowledge_index)} entries")

        return crawl_results

    def extract_tutorials(self) -> List[HTMLTutorial]:
        """
        Extract and analyze tutorial content from crawled data

        Teaching note (Day 23 - Data processing): Advanced content analysis
        to identify structured learning materials and extract metadata.
        """
        print("📚 Extracting HTML tutorials and learning content...")

        tutorials = []

        # Load crawled content
        html_dir = self.data_dir / 'raw_crawl' / 'html'
        text_dir = self.data_dir / 'raw_crawl' / 'text'

        if not html_dir.exists():
            print("❌ No crawled HTML content found. Run crawl_html_com() first.")
            return tutorials

        # Process each crawled page
        for html_file in html_dir.glob('*.html'):
            try:
                # Read HTML content
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html_content, 'html.parser')

                # Extract tutorial information
                tutorial = self.analyze_tutorial_page(soup, html_file.stem)
                if tutorial:
                    tutorials.append(tutorial)

            except Exception as e:
                print(f"⚠️ Error processing {html_file}: {str(e)}")
                continue

        self.tutorials = tutorials
        print(f"📖 Extracted {len(tutorials)} tutorials")

        return tutorials

    def analyze_tutorial_page(self, soup: BeautifulSoup, file_id: str) -> Optional[HTMLTutorial]:
        """
        Analyze a single tutorial page and extract structured information

        Teaching note (Day 24 - Web scraping): Specialized HTML analysis
        for educational content extraction and structuring.
        """
        # Extract title
        title_elem = soup.find('title')
        if not title_elem:
            return None

        title = title_elem.get_text().strip()

        # Skip non-tutorial pages
        tutorial_indicators = ['tutorial', 'guide', 'how to', 'learn', 'introduction', 'reference']
        if not any(indicator in title.lower() for indicator in tutorial_indicators):
            return None

        # Extract main content
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if not main_content:
            main_content = soup.find('body')

        # Determine difficulty level
        difficulty = self.determine_difficulty(title, main_content)

        # Extract topics covered
        topics = self.extract_topics(main_content)

        # Extract code examples
        code_examples = self.extract_code_examples(main_content)

        # Extract prerequisites
        prerequisites = self.extract_prerequisites(main_content, title)

        # Extract learning objectives
        learning_objectives = self.extract_learning_objectives(main_content, title)

        # Estimate reading time
        text_content = main_content.get_text() if main_content else ""
        word_count = len(text_content.split())
        estimated_time = max(5, word_count // 200)  # ~200 words per minute

        # Find URL from knowledge index
        url = "unknown"
        for indexed_url, data in self.crawler.knowledge_index.items():
            if file_id in indexed_url or title in data.get('title', ''):
                url = indexed_url
                break

        return HTMLTutorial(
            title=title,
            url=url,
            difficulty=difficulty,
            topics=topics,
            code_examples=code_examples,
            prerequisites=prerequisites,
            learning_objectives=learning_objectives,
            estimated_time=estimated_time
        )

    def determine_difficulty(self, title: str, content: BeautifulSoup) -> str:
        """Determine tutorial difficulty level"""
        title_lower = title.lower()
        content_text = content.get_text().lower() if content else ""

        # Beginner indicators
        beginner_terms = ['introduction', 'basic', 'beginner', 'getting started', 'first', 'simple']
        if any(term in title_lower for term in beginner_terms):
            return 'beginner'

        # Advanced indicators
        advanced_terms = ['advanced', 'complex', 'professional', 'optimization', 'performance']
        if any(term in title_lower for term in advanced_terms):
            return 'advanced'

        # Check content complexity
        advanced_html_tags = ['canvas', 'svg', 'webgl', 'service worker', 'web components']
        if any(tag in content_text for tag in advanced_html_tags):
            return 'advanced'

        basic_html_tags = ['html', 'body', 'head', 'title', 'h1', 'p']
        basic_tag_count = sum(1 for tag in basic_html_tags if tag in content_text)

        if basic_tag_count >= 3:
            return 'beginner'

        return 'intermediate'

    def extract_topics(self, content: BeautifulSoup) -> List[str]:
        """Extract HTML topics covered in the tutorial"""
        if not content:
            return []

        topics = set()
        content_text = content.get_text().lower()

        # Check for HTML tag patterns
        for category, tags in self.html_patterns.items():
            for tag in tags:
                # Look for tag mentions in various forms
                patterns = [
                    f'<{tag}',
                    f'{tag} tag',
                    f'{tag} element',
                    f'&lt;{tag}',
                ]

                if any(pattern in content_text for pattern in patterns):
                    topics.add(category)
                    topics.add(tag)

        # Check for CSS and JavaScript integration
        if any(term in content_text for term in ['css', 'style', 'stylesheet']):
            topics.add('css_integration')

        if any(term in content_text for term in ['javascript', 'script', 'js']):
            topics.add('javascript_integration')

        # Check for accessibility topics
        if any(term in content_text for term in ['accessibility', 'aria', 'alt text', 'screen reader']):
            topics.add('accessibility')

        # Check for responsive design
        if any(term in content_text for term in ['responsive', 'mobile', 'viewport', 'media query']):
            topics.add('responsive_design')

        return list(topics)

    def extract_code_examples(self, content: BeautifulSoup) -> List[Dict]:
        """Extract and analyze code examples from tutorial content"""
        if not content:
            return []

        examples = []

        # Find code blocks
        code_elements = content.find_all(['code', 'pre', 'script']) + \
                       content.find_all('div', class_=re.compile(r'(code|highlight|example)'))

        for elem in code_elements:
            code_text = elem.get_text().strip()

            # Skip very short or empty code blocks
            if len(code_text) < 10:
                continue

            # Determine language
            language = 'html'  # Default for HTML.com

            # Check for CSS
            if any(indicator in code_text for indicator in ['color:', 'font-size:', 'margin:', 'padding:']):
                language = 'css'

            # Check for JavaScript
            if any(indicator in code_text for indicator in ['function', 'var ', 'let ', 'const ', 'document.']):
                language = 'javascript'

            # Extract explanation (look for nearby text)
            explanation = ""
            next_sibling = elem.find_next_sibling(['p', 'div', 'span'])
            if next_sibling:
                explanation = next_sibling.get_text().strip()[:200]

            # Determine tags used
            html_tags = re.findall(r'<(\w+)', code_text)
            tags = list(set(html_tags))

            examples.append({
                'language': language,
                'code': code_text,
                'explanation': explanation,
                'output': '',  # Could be extracted if present
                'difficulty': self.determine_code_difficulty(code_text, tags),
                'tags': tags
            })

        return examples[:10]  # Limit to prevent overflow

    def determine_code_difficulty(self, code: str, tags: List[str]) -> str:
        """Determine difficulty of a code example"""
        basic_tags = set(['html', 'head', 'body', 'title', 'h1', 'h2', 'h3', 'p', 'div'])
        advanced_tags = set(['canvas', 'svg', 'video', 'audio', 'form', 'table'])

        used_tags = set(tags)

        if used_tags.intersection(advanced_tags):
            return 'advanced'
        elif used_tags.intersection(basic_tags) and len(used_tags) <= 3:
            return 'beginner'
        else:
            return 'intermediate'

    def extract_prerequisites(self, content: BeautifulSoup, title: str) -> List[str]:
        """Extract tutorial prerequisites"""
        prerequisites = []

        if not content:
            return prerequisites

        content_text = content.get_text().lower()
        title_lower = title.lower()

        # Look for explicit prerequisites
        prereq_patterns = [
            r'prerequisite[s]?:?\s*([^.]+)',
            r'before you start[^.]+',
            r'you should know[^.]+',
            r'assumes?[^.]+knowledge of[^.]+'
        ]

        for pattern in prereq_patterns:
            matches = re.findall(pattern, content_text)
            prerequisites.extend(matches)

        # Infer prerequisites based on difficulty and topics
        if 'advanced' in title_lower:
            prerequisites.append('Basic HTML knowledge')
            prerequisites.append('Understanding of HTML structure')

        if any(term in content_text for term in ['css', 'styling']):
            prerequisites.append('Basic CSS knowledge')

        if any(term in content_text for term in ['javascript', 'interactive']):
            prerequisites.append('Basic JavaScript knowledge')

        return list(set(prerequisites))[:5]  # Limit and deduplicate

    def extract_learning_objectives(self, content: BeautifulSoup, title: str) -> List[str]:
        """Extract learning objectives from tutorial content"""
        objectives = []

        if not content:
            return objectives

        content_text = content.get_text()

        # Look for explicit objectives
        objective_patterns = [
            r'you will learn[^.]+',
            r'this tutorial covers[^.]+',
            r'by the end[^.]+you will[^.]+',
            r'objectives?:?\s*([^.]+)'
        ]

        for pattern in objective_patterns:
            matches = re.findall(pattern, content_text, re.IGNORECASE)
            objectives.extend(matches)

        # Extract from headings
        headings = content.find_all(['h1', 'h2', 'h3', 'h4'])
        for heading in headings:
            heading_text = heading.get_text().strip()
            if any(indicator in heading_text.lower() for indicator in ['how to', 'creating', 'building', 'using']):
                objectives.append(heading_text)

        return list(set(objectives))[:8]  # Limit and deduplicate

    def build_learning_curriculum(self) -> Dict:
        """
        Build structured learning curriculum from extracted tutorials

        Teaching note (Day 28 - Data organization): Creating structured
        learning progressions from unstructured content analysis.
        """
        print("📚 Building structured learning curriculum...")

        if not self.tutorials:
            print("⚠️ No tutorials found. Run extract_tutorials() first.")
            return {}

        # Group by difficulty
        curriculum = {
            'beginner': [],
            'intermediate': [],
            'advanced': []
        }

        for tutorial in self.tutorials:
            curriculum[tutorial.difficulty].append({
                'title': tutorial.title,
                'url': tutorial.url,
                'topics': tutorial.topics,
                'estimated_time': tutorial.estimated_time,
                'prerequisites': tutorial.prerequisites,
                'objectives': tutorial.learning_objectives,
                'code_examples': len(tutorial.code_examples)
            })

        # Sort by estimated time and complexity
        for level in curriculum:
            curriculum[level].sort(key=lambda x: (len(x['prerequisites']), x['estimated_time']))

        # Create topic progression
        topic_progression = self.create_topic_progression()

        # Calculate total curriculum stats
        stats = {
            'total_tutorials': len(self.tutorials),
            'beginner_count': len(curriculum['beginner']),
            'intermediate_count': len(curriculum['intermediate']),
            'advanced_count': len(curriculum['advanced']),
            'total_time_hours': sum(t.estimated_time for t in self.tutorials) / 60,
            'unique_topics': len(set(topic for t in self.tutorials for topic in t.topics)),
            'total_code_examples': sum(len(t.code_examples) for t in self.tutorials)
        }

        full_curriculum = {
            'metadata': {
                'created_at': datetime.now().isoformat(),
                'source': 'HTML.com',
                'extractor_version': '2.1.0'
            },
            'statistics': stats,
            'curriculum': curriculum,
            'topic_progression': topic_progression,
            'learning_path': self.create_learning_path()
        }

        # Save curriculum
        curriculum_file = self.data_dir / 'curriculum' / f"html_curriculum_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(curriculum_file, 'w', encoding='utf-8') as f:
            json.dump(full_curriculum, f, indent=2, ensure_ascii=False)

        print(f"✅ Curriculum saved: {curriculum_file}")
        print(f"📊 {stats['total_tutorials']} tutorials, {stats['total_time_hours']:.1f} hours total")

        return full_curriculum

    def create_topic_progression(self) -> Dict[str, List[str]]:
        """Create logical topic progression map"""
        progression = {}

        # Analyze topic dependencies
        topic_counts = defaultdict(int)
        topic_cooccurrences = defaultdict(lambda: defaultdict(int))

        for tutorial in self.tutorials:
            for topic in tutorial.topics:
                topic_counts[topic] += 1

                for other_topic in tutorial.topics:
                    if topic != other_topic:
                        topic_cooccurrences[topic][other_topic] += 1

        # Build progression based on our HTML learning patterns
        for level, categories in self.progression_map.items():
            progression[level] = []
            for category in categories:
                if category in self.html_patterns:
                    progression[level].extend(self.html_patterns[category])

        return progression

    def create_learning_path(self) -> List[Dict]:
        """Create recommended learning path through tutorials"""
        path = []

        # Sort tutorials by difficulty and prerequisites
        sorted_tutorials = sorted(self.tutorials, key=lambda t: (
            ['beginner', 'intermediate', 'advanced'].index(t.difficulty),
            len(t.prerequisites),
            t.estimated_time
        ))

        for i, tutorial in enumerate(sorted_tutorials):
            path.append({
                'step': i + 1,
                'title': tutorial.title,
                'difficulty': tutorial.difficulty,
                'estimated_time': tutorial.estimated_time,
                'topics': tutorial.topics[:5],  # Top 5 topics
                'url': tutorial.url
            })

        return path

    def generate_practice_exercises(self) -> List[Dict]:
        """
        Generate practice exercises based on extracted content

        Teaching note (Day 26 - Problem solving): Automatic generation
        of practice exercises from analyzed tutorial content.
        """
        print("🎯 Generating practice exercises...")

        exercises = []

        for tutorial in self.tutorials:
            for example in tutorial.code_examples:
                if example['language'] == 'html' and len(example['tags']) > 0:
                    # Create fill-in-the-blank exercise
                    exercise = self.create_fill_in_blank(example)
                    if exercise:
                        exercises.append(exercise)

                    # Create tag identification exercise
                    exercise = self.create_tag_identification(example)
                    if exercise:
                        exercises.append(exercise)

        # Save exercises
        exercises_file = self.data_dir / 'curriculum' / f"practice_exercises_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(exercises_file, 'w', encoding='utf-8') as f:
            json.dump(exercises, f, indent=2, ensure_ascii=False)

        print(f"🎯 Generated {len(exercises)} practice exercises: {exercises_file}")
        return exercises

    def create_fill_in_blank(self, code_example: Dict) -> Optional[Dict]:
        """Create fill-in-the-blank exercise from code example"""
        code = code_example['code']
        tags = code_example['tags']

        if len(tags) == 0:
            return None

        # Select a tag to blank out
        target_tag = tags[0]

        # Create blanked version
        blanked_code = re.sub(f'<{target_tag}\\b[^>]*>', f'<___>', code)
        blanked_code = re.sub(f'</{target_tag}>', f'</___>', blanked_code)

        return {
            'type': 'fill_in_blank',
            'question': f"Fill in the blank to complete this HTML code:",
            'code': blanked_code,
            'answer': target_tag,
            'difficulty': code_example['difficulty'],
            'explanation': f"The {target_tag} tag is used in this context."
        }

    def create_tag_identification(self, code_example: Dict) -> Optional[Dict]:
        """Create tag identification exercise"""
        tags = code_example['tags']

        if len(tags) < 2:
            return None

        return {
            'type': 'tag_identification',
            'question': f"Which HTML tags are used in this code example?",
            'code': code_example['code'],
            'correct_answers': tags,
            'difficulty': code_example['difficulty'],
            'explanation': f"This example uses the following tags: {', '.join(tags)}"
        }

    def run_complete_analysis(self) -> Dict:
        """
        Run complete HTML.com knowledge extraction and analysis

        Teaching note (Day 11 - Functions): Master function that orchestrates
        the entire knowledge extraction workflow.
        """
        print("🚀 Starting complete HTML.com knowledge extraction...")

        results = {
            'start_time': datetime.now().isoformat(),
            'steps_completed': [],
            'errors': []
        }

        try:
            # Step 1: Crawl HTML.com
            print("\n📥 Step 1: Crawling HTML.com...")
            crawl_results = self.crawl_html_com()
            results['steps_completed'].append('crawl')
            results['crawl_stats'] = crawl_results['stats']

            # Step 2: Extract tutorials
            print("\n📚 Step 2: Extracting tutorials...")
            tutorials = self.extract_tutorials()
            results['steps_completed'].append('extract_tutorials')
            results['tutorial_count'] = len(tutorials)

            # Step 3: Build curriculum
            print("\n🎓 Step 3: Building curriculum...")
            curriculum = self.build_learning_curriculum()
            results['steps_completed'].append('build_curriculum')
            results['curriculum_stats'] = curriculum['statistics']

            # Step 4: Generate exercises
            print("\n🎯 Step 4: Generating practice exercises...")
            exercises = self.generate_practice_exercises()
            results['steps_completed'].append('generate_exercises')
            results['exercise_count'] = len(exercises)

            results['end_time'] = datetime.now().isoformat()
            results['status'] = 'success'

            # Save results summary
            summary_file = self.data_dir / 'analysis' / f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='ascii', errors='replace') as f:
                json.dump(results, f, indent=2, ensure_ascii=True, default=str)

            print(f"\n✅ Complete analysis finished successfully!")
            print(f"📊 Results saved: {summary_file}")

            return results

        except Exception as e:
            results['errors'].append(str(e))
            results['status'] = 'failed'
            results['end_time'] = datetime.now().isoformat()

            print(f"\n❌ Analysis failed: {str(e)}")
            return results

def main():
    """Main entry point for HTML knowledge extractor"""
    import argparse

    parser = argparse.ArgumentParser(description='EQ12 HTML.com Knowledge Extractor')
    parser.add_argument('--analyze-tutorials', action='store_true', help='Extract and analyze tutorials')
    parser.add_argument('--extract-code', action='store_true', help='Extract code examples')
    parser.add_argument('--build-curriculum', action='store_true', help='Build learning curriculum')
    parser.add_argument('--generate-exercises', action='store_true', help='Generate practice exercises')
    parser.add_argument('--complete-analysis', action='store_true', help='Run complete analysis')
    parser.add_argument('--data-dir', help='Data directory path')

    args = parser.parse_args()

    try:
        # Initialize extractor
        data_dir = Path(args.data_dir) if args.data_dir else None
        extractor = EQ12HTMLKnowledgeExtractor(data_dir)

        print("🎓 EQ12 HTML.com Knowledge Extractor")
        print("Professional Learning Content Analysis")
        print("=" * 60)

        if args.complete_analysis:
            extractor.run_complete_analysis()
        else:
            if args.analyze_tutorials:
                extractor.crawl_html_com()
                extractor.extract_tutorials()

            if args.build_curriculum:
                extractor.build_learning_curriculum()

            if args.generate_exercises:
                extractor.generate_practice_exercises()

        print("\n🎉 Analysis completed successfully!")
        return 0

    except KeyboardInterrupt:
        print("\n🛑 Analysis cancelled by user")
        return 130

    except Exception as e:
        print(f"\n💥 Error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
