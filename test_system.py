#!/usr/bin/env python3
"""
Simple test script to verify the Label Router system is working correctly
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.core.smart_tagger import SmartTagger
from src.models.tags import TagRequest


def test_tagging_system():
    """Test the tagging system with various examples"""
    
    print("=== Label Router System Test ===\n")
    
    # Initialize tagger
    print("Initializing Smart Tagger...")
    tagger = SmartTagger(enable_ml=True)
    print("✓ Tagger initialized\n")
    
    # Test cases
    test_cases = [
        {
            "name": "Decision Item",
            "text": "本日の会議で基礎工事の工程について決定しました。施工者は来週月曜日までに詳細な工程表を提出してください。",
            "expected": {
                "content_type": "決定事項",
                "has_domains": True,
                "has_stakeholders": True
            }
        },
        {
            "name": "Safety Issue",
            "text": "安全パトロールの結果、3階の作業エリアで危険箇所が確認されました。至急、協力業者は是正措置を実施してください。",
            "expected": {
                "content_type": "課題",
                "priority": "高",
                "has_domains": True
            }
        },
        {
            "name": "Cost Information",
            "text": "設備工事の追加費用について報告します。見積金額は約500万円となります。発注者の承認をお願いします。",
            "expected": {
                "has_amount": True,
                "has_stakeholders": True
            }
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases):
        print(f"Test {i+1}: {test_case['name']}")
        print(f"Text: {test_case['text'][:50]}...")
        
        # Create request
        request = TagRequest(
            content=test_case["text"],
            enable_ml=True,
            enable_rules=True
        )
        
        # Tag content
        response = tagger.tag(request)
        tags = response.tags
        
        print(f"Results:")
        print(f"  - Content Type: {tags.content_type.value if tags.content_type else 'None'}")
        print(f"  - Domains: {[d.value for d in tags.domains]}")
        print(f"  - Priority: {tags.priority.value if tags.priority else 'None'}")
        print(f"  - Stakeholders: {[s.value for s in tags.stakeholders]}")
        print(f"  - Custom Tags: {len(tags.custom_tags)}")
        print(f"  - Processing Time: {response.processing_time:.3f}s")
        
        # Basic validation
        passed = True
        expected = test_case.get("expected", {})
        
        if "content_type" in expected:
            if tags.content_type and tags.content_type.value == expected["content_type"]:
                print(f"  ✓ Content type matches expected: {expected['content_type']}")
            else:
                print(f"  ✗ Content type mismatch. Expected: {expected['content_type']}, Got: {tags.content_type.value if tags.content_type else 'None'}")
                passed = False
        
        if "priority" in expected:
            if tags.priority and tags.priority.value == expected["priority"]:
                print(f"  ✓ Priority matches expected: {expected['priority']}")
            else:
                print(f"  ✗ Priority mismatch")
                passed = False
        
        if expected.get("has_domains") and tags.domains:
            print(f"  ✓ Domains detected")
        elif expected.get("has_domains"):
            print(f"  ✗ No domains detected")
            passed = False
        
        if expected.get("has_stakeholders") and tags.stakeholders:
            print(f"  ✓ Stakeholders detected")
        elif expected.get("has_stakeholders"):
            print(f"  ✗ No stakeholders detected")
            passed = False
        
        if expected.get("has_amount"):
            amount_tags = [t for t in tags.custom_tags if t.category == "amount"]
            if amount_tags:
                print(f"  ✓ Amount detected: {amount_tags[0].value}")
            else:
                print(f"  ✗ No amount detected")
                passed = False
        
        print(f"Overall: {'PASSED' if passed else 'FAILED'}\n")
    
    print("=== Test Complete ===")


if __name__ == "__main__":
    test_tagging_system()