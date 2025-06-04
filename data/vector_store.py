import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import json
import asyncio
from pathlib import Path

class VectorKnowledgeStore:
    """Vector database for semantic search of government knowledge"""
    
    def __init__(self, persist_directory: str = "data/chroma_db"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collections
        self.faq_collection = self.client.get_or_create_collection(
            name="brushy_creek_faq",
            metadata={"description": "Brushy Creek MUD FAQ and knowledge base"}
        )
        
        self.procedures_collection = self.client.get_or_create_collection(
            name="brushy_creek_procedures", 
            metadata={"description": "Service procedures and emergency protocols"}
        )
    
    async def initialize_knowledge_base(self):
        """Initialize vector store with knowledge base content"""
        from government.brushy_creek_knowledge import BrushyCreekKnowledgeBase
        
        kb = BrushyCreekKnowledgeBase()
        
        # Clear existing data
        try:
            self.faq_collection.delete(where={})
            self.procedures_collection.delete(where={})
        except:
            pass
        
        # Index FAQ content
        await self._index_faq_content(kb)
        
        # Index procedures and emergency protocols
        await self._index_procedures(kb)
        
        print("✅ Vector knowledge base initialized successfully")
    
    async def _index_faq_content(self, kb: 'BrushyCreekKnowledgeBase'):
        """Index FAQ content into vector store"""
        documents = []
        metadatas = []
        ids = []
        
        counter = 0
        
        # Index all FAQ sections
        for section_name in ["water_quality_faq", "billing_faq", "facilities_faq", "trash_recycling_faq"]:
            section_data = getattr(kb, section_name)
            
            for category, items in section_data.items():
                if isinstance(items, dict):
                    for key, value in items.items():
                        # Create searchable document
                        document = f"Question: {key.replace('_', ' ').title()}\nAnswer: {value}"
                        
                        documents.append(document)
                        metadatas.append({
                            "section": section_name.replace('_faq', ''),
                            "category": category,
                            "topic": key,
                            "type": "faq"
                        })
                        ids.append(f"faq_{counter}")
                        counter += 1
                elif isinstance(items, list):
                    # Handle list items (like recyclables)
                    document = f"Category: {category}\nItems: {', '.join(items)}"
                    documents.append(document)
                    metadatas.append({
                        "section": section_name.replace('_faq', ''),
                        "category": category,
                        "type": "list"
                    })
                    ids.append(f"faq_{counter}")
                    counter += 1
                else:
                    # Handle simple string values
                    document = f"Category: {category}\nInformation: {items}"
                    documents.append(document)
                    metadatas.append({
                        "section": section_name.replace('_faq', ''),
                        "category": category,
                        "type": "info"
                    })
                    ids.append(f"faq_{counter}")
                    counter += 1
        
        # Add to collection
        if documents:
            self.faq_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    async def _index_procedures(self, kb: 'BrushyCreekKnowledgeBase'):
        """Index emergency procedures and common scenarios"""
        documents = []
        metadatas = []
        ids = []
        
        counter = 0
        
        # Index common scenarios
        for scenario, data in kb.common_scenarios.items():
            document = f"Scenario: {scenario.replace('_', ' ').title()}\nKeywords: {', '.join(data['keywords'])}\nResponse: {data['response']}"
            
            documents.append(document)
            metadatas.append({
                "scenario": scenario,
                "priority": data["priority"],
                "type": "procedure"
            })
            ids.append(f"proc_{counter}")
            counter += 1
        
        # Add district history and context
        for key, value in kb.district_history.items():
            if isinstance(value, list):
                document = f"Topic: {key.replace('_', ' ').title()}\nInformation: {', '.join(value)}"
            else:
                document = f"Topic: {key.replace('_', ' ').title()}\nInformation: {value}"
            
            documents.append(document)
            metadatas.append({
                "topic": key,
                "type": "history"
            })
            ids.append(f"proc_{counter}")
            counter += 1
        
        # Add to collection
        if documents:
            self.procedures_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
    
    async def search_knowledge(self, query: str, max_results: int = 5) -> List[Dict]:
        """Semantic search across knowledge base"""
        results = []
        
        # Search FAQ collection
        faq_results = self.faq_collection.query(
            query_texts=[query],
            n_results=min(max_results, 10)
        )
        
        # Search procedures collection
        proc_results = self.procedures_collection.query(
            query_texts=[query],
            n_results=min(max_results, 10)
        )
        
        # Combine and format results
        for i, (doc, metadata, distance) in enumerate(zip(
            faq_results['documents'][0],
            faq_results['metadatas'][0], 
            faq_results['distances'][0]
        )):
            results.append({
                "content": doc,
                "metadata": metadata,
                "relevance_score": 1 - distance,  # Convert distance to similarity
                "source": "faq"
            })
        
        for i, (doc, metadata, distance) in enumerate(zip(
            proc_results['documents'][0],
            proc_results['metadatas'][0],
            proc_results['distances'][0]
        )):
            results.append({
                "content": doc,
                "metadata": metadata,
                "relevance_score": 1 - distance,
                "source": "procedures"
            })
        
        # Sort by relevance and return top results
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:max_results]
    
    async def get_emergency_response(self, query: str) -> Optional[Dict]:
        """Get immediate emergency response for urgent queries"""
        emergency_keywords = [
            "emergency", "urgent", "help", "leak", "flooding", 
            "no water", "burst pipe", "sewage backup"
        ]
        
        query_lower = query.lower()
        if any(keyword in query_lower for keyword in emergency_keywords):
            # Search for emergency procedures
            results = await self.search_knowledge(query, max_results=1)
            if results and results[0].get('metadata', {}).get('priority') == 'emergency':
                return results[0]
        
        return None
    
    async def update_knowledge_item(self, item_id: str, content: str, metadata: Dict):
        """Update a specific knowledge base item"""
        try:
            # Try FAQ collection first
            self.faq_collection.update(
                ids=[item_id],
                documents=[content],
                metadatas=[metadata]
            )
        except:
            try:
                # Try procedures collection
                self.procedures_collection.update(
                    ids=[item_id],
                    documents=[content],
                    metadatas=[metadata]
                )
            except Exception as e:
                print(f"Failed to update knowledge item {item_id}: {e}")
    
    async def add_new_knowledge(self, content: str, metadata: Dict, collection: str = "faq"):
        """Add new knowledge to the vector store"""
        import uuid
        
        item_id = f"{collection}_{uuid.uuid4().hex[:8]}"
        
        target_collection = self.faq_collection if collection == "faq" else self.procedures_collection
        
        target_collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[item_id]
        )
        
        return item_id
    
    def get_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        return {
            "faq_count": self.faq_collection.count(),
            "procedures_count": self.procedures_collection.count(),
            "total_items": self.faq_collection.count() + self.procedures_collection.count()
        } 