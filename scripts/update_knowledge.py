#!/usr/bin/env python3
"""
Knowledge Base Management Script

This script helps maintain and update the Brushy Creek MUD knowledge base
by crawling their website, updating FAQ content, and managing the vector store.
"""

import asyncio
import requests
from bs4 import BeautifulSoup
import sys
from pathlib import Path
import json
from typing import Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data.vector_store import VectorKnowledgeStore
from government.brushy_creek_knowledge import BrushyCreekKnowledgeBase

class KnowledgeBaseUpdater:
    """Manages updates to the Brushy Creek MUD knowledge base"""
    
    def __init__(self):
        self.base_url = "https://www.bcmud.org"
        self.vector_store = VectorKnowledgeStore()
        self.session = requests.Session()
        
        # Important pages to monitor
        self.critical_pages = [
            "/content/13128/13272/14041.aspx",  # General FAQ
            "/content/13126/13250/13453.aspx",  # Water Quality FAQ
            "/content/13130/13282/14637/14657.aspx",  # Swim Lessons FAQ
            "/content/13126/13258/21915.aspx",  # Trash & Recycling FAQ
            "/Billing",  # Billing Information
            "/content/13128/13272/14042.aspx",  # District History
        ]
    
    async def crawl_website_updates(self) -> Dict[str, str]:
        """Crawl the website for content updates"""
        print("🔍 Crawling Brushy Creek MUD website for updates...")
        
        updated_content = {}
        
        for page_path in self.critical_pages:
            try:
                url = f"{self.base_url}{page_path}"
                response = self.session.get(url, timeout=10)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract main content
                content_div = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
                if content_div:
                    # Remove navigation, headers, footers
                    for element in content_div.find_all(['nav', 'header', 'footer', 'script', 'style']):
                        element.decompose()
                    
                    text_content = content_div.get_text(strip=True)
                    updated_content[page_path] = text_content
                    print(f"✅ Crawled {page_path} ({len(text_content)} chars)")
                
            except Exception as e:
                print(f"❌ Failed to crawl {page_path}: {e}")
        
        return updated_content
    
    async def detect_content_changes(self, new_content: Dict[str, str]) -> List[str]:
        """Detect which pages have significant content changes"""
        changes_detected = []
        
        # Load previous content if exists
        cache_file = Path("data/content_cache.json")
        previous_content = {}
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                previous_content = json.load(f)
        
        for page_path, content in new_content.items():
            if page_path not in previous_content:
                changes_detected.append(page_path)
                print(f"🆕 New page detected: {page_path}")
            elif previous_content[page_path] != content:
                # Calculate change percentage
                old_len = len(previous_content[page_path])
                new_len = len(content)
                change_pct = abs(new_len - old_len) / max(old_len, 1) * 100
                
                if change_pct > 5:  # 5% change threshold
                    changes_detected.append(page_path)
                    print(f"📝 Content changed: {page_path} ({change_pct:.1f}% change)")
        
        # Save new content
        cache_file.parent.mkdir(exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump(new_content, f, indent=2)
        
        return changes_detected
    
    async def extract_new_faq_items(self, content: str) -> List[Dict]:
        """Extract FAQ items from crawled content"""
        faq_items = []
        
        # Simple FAQ extraction (can be enhanced with more sophisticated parsing)
        lines = content.split('\n')
        current_question = None
        current_answer = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Detect question patterns
            if line.endswith('?') or 'Q:' in line or line.startswith('What') or line.startswith('How') or line.startswith('Why'):
                if current_question and current_answer:
                    faq_items.append({
                        "question": current_question,
                        "answer": ' '.join(current_answer),
                        "source": "website_crawl"
                    })
                
                current_question = line
                current_answer = []
            elif current_question:
                current_answer.append(line)
        
        # Add final item
        if current_question and current_answer:
            faq_items.append({
                "question": current_question,
                "answer": ' '.join(current_answer),
                "source": "website_crawl"
            })
        
        return faq_items
    
    async def update_vector_store(self, new_faq_items: List[Dict]):
        """Update the vector store with new FAQ items"""
        if not new_faq_items:
            print("ℹ️  No new FAQ items to add")
            return
        
        print(f"📚 Adding {len(new_faq_items)} new FAQ items to vector store...")
        
        for item in new_faq_items:
            content = f"Question: {item['question']}\nAnswer: {item['answer']}"
            metadata = {
                "source": item["source"],
                "type": "faq",
                "category": "website_update",
                "updated": True
            }
            
            await self.vector_store.add_new_knowledge(content, metadata, "faq")
        
        print("✅ Vector store updated successfully")
    
    async def validate_knowledge_base(self):
        """Validate the current knowledge base"""
        print("🔍 Validating knowledge base...")
        
        # Test common queries
        test_queries = [
            "water emergency contact",
            "billing questions",
            "pool hours",
            "trash pickup schedule",
            "water quality issues",
            "swim lessons registration"
        ]
        
        for query in test_queries:
            results = await self.vector_store.search_knowledge(query, max_results=1)
            if results:
                relevance = results[0]['relevance_score']
                print(f"✅ '{query}': {relevance:.2f} relevance")
            else:
                print(f"❌ '{query}': No results found")
        
        # Get statistics
        stats = self.vector_store.get_stats()
        print(f"\n📊 Knowledge Base Stats:")
        print(f"   FAQ items: {stats['faq_count']}")
        print(f"   Procedures: {stats['procedures_count']}")
        print(f"   Total items: {stats['total_items']}")

async def main():
    """Main function to update knowledge base"""
    print("🚀 Starting Knowledge Base Update Process\n")
    
    updater = KnowledgeBaseUpdater()
    
    # Step 1: Initialize vector store if needed
    try:
        await updater.vector_store.initialize_knowledge_base()
    except Exception as e:
        print(f"⚠️  Vector store initialization: {e}")
    
    # Step 2: Crawl website for updates
    new_content = await updater.crawl_website_updates()
    
    # Step 3: Detect changes
    changes = await updater.detect_content_changes(new_content)
    
    if changes:
        print(f"\n📝 Processing {len(changes)} changed pages...")
        
        # Step 4: Extract new FAQ items
        all_new_faq = []
        for page_path in changes:
            if page_path in new_content:
                faq_items = await updater.extract_new_faq_items(new_content[page_path])
                all_new_faq.extend(faq_items)
        
        # Step 5: Update vector store
        await updater.update_vector_store(all_new_faq)
    else:
        print("✅ No content changes detected")
    
    # Step 6: Validate knowledge base
    await updater.validate_knowledge_base()
    
    print("\n🎉 Knowledge base update complete!")

if __name__ == "__main__":
    asyncio.run(main()) 