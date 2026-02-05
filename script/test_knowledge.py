#!/usr/bin/env python3
"""
Test script to verify Skolverket knowledge base without ChromaDB dependency
"""

import sys
from pathlib import Path

# Add the script directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_knowledge_base():
    """Test the knowledge base creation without ChromaDB"""
    
    # Import only the function we need
    from script.load_skolverket_knowledge import create_skolverket_knowledge_base
    
    # Create knowledge items
    items = create_skolverket_knowledge_base()
    
    print(f"✅ Created {len(items)} knowledge items")
    print()
    
    # Show first few items
    print("📚 First 3 items:")
    for i, item in enumerate(items[:3], 1):
        print(f"{i}. Type: {item['type']}")
        print(f"   Subject: {item['subject']}, Level: {item['level']}")
        print(f"   Content: {item['content'][:100]}...")
        print()
    
    # Show all types
    types = set(item['type'] for item in items)
    print(f"🎯 Knowledge types: {sorted(types)}")
    print()
    
    # Count by type
    type_counts = {}
    for item in items:
        type_counts[item['type']] = type_counts.get(item['type'], 0) + 1
    
    print("📊 Items per type:")
    for type_name, count in sorted(type_counts.items()):
        print(f"   {type_name}: {count} items")
    
    print()
    print("🎉 Knowledge base test completed successfully!")
    print("Ready to load into ChromaDB when dependencies are installed.")

if __name__ == "__main__":
    test_knowledge_base()

