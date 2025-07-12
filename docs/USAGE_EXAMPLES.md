# Label Router Usage Examples

## Python Client Examples

### Basic Usage

```python
import requests
import json

# API base URL
BASE_URL = "http://localhost:8000"

# Example 1: Tag a single content
def tag_single_content(text):
    url = f"{BASE_URL}/api/v1/tag"
    payload = {
        "content": text,
        "enable_ml": True,
        "enable_rules": True
    }
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        print(f"Content ID: {result['content_id']}")
        print(f"Content Type: {result['tags']['content_type']}")
        print(f"Domains: {result['tags']['domains']}")
        print(f"Priority: {result['tags']['priority']}")
        print(f"Processing Time: {result['processing_time']:.3f}s")
        return result
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage
text = "本日の会議で基礎工事の工程について決定しました。施工者は来週月曜日までに詳細な工程表を提出してください。"
result = tag_single_content(text)
```

### Batch Processing

```python
# Example 2: Batch tag multiple contents
def batch_tag_contents(texts):
    url = f"{BASE_URL}/api/v1/tag/batch"
    
    response = requests.post(url, json=texts)
    if response.status_code == 200:
        results = response.json()
        for i, result in enumerate(results):
            print(f"\nContent {i+1}:")
            print(f"  ID: {result['content_id']}")
            print(f"  Type: {result['tags']['content_type']}")
            print(f"  Domains: {', '.join(result['tags']['domains'])}")
        return results
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage
texts = [
    "鉄筋コンクリート構造の品質検査で問題が発見されました。",
    "安全パトロールの結果を報告します。",
    "設備工事の追加費用について発注者の承認が必要です。"
]
results = batch_tag_contents(texts)
```

### Search by Tags

```python
# Example 3: Search content by tags
def search_by_tags(content_types=None, domains=None, priorities=None):
    url = f"{BASE_URL}/api/v1/search/tags"
    
    search_criteria = {
        "content_types": content_types or [],
        "domains": domains or [],
        "priorities": priorities or [],
        "limit": 10,
        "offset": 0
    }
    
    response = requests.post(url, json=search_criteria)
    if response.status_code == 200:
        result = response.json()
        print(f"Found {result['total']} results")
        for item in result['results']:
            print(f"\nContent ID: {item['content_id']}")
            print(f"  Type: {item['tags']['content_type']}")
            print(f"  Domains: {', '.join(item['tags']['domains'])}")
        return result
    else:
        print(f"Error: {response.status_code}")
        return None

# Example usage
results = search_by_tags(
    content_types=["決定事項", "課題"],
    domains=["構造"],
    priorities=["高"]
)
```

### Complete Client Class

```python
class LabelRouterClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def tag_content(self, text, enable_ml=True, enable_rules=True):
        """Tag a single piece of content"""
        url = f"{self.base_url}/api/v1/tag"
        payload = {
            "content": text,
            "enable_ml": enable_ml,
            "enable_rules": enable_rules
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def batch_tag(self, texts, enable_ml=True, enable_rules=True):
        """Tag multiple contents"""
        url = f"{self.base_url}/api/v1/tag/batch"
        params = {
            "enable_ml": enable_ml,
            "enable_rules": enable_rules
        }
        response = requests.post(url, json=texts, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_tags(self, content_id):
        """Retrieve tags for a content ID"""
        url = f"{self.base_url}/api/v1/tags/{content_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def search_tags(self, **criteria):
        """Search content by tags"""
        url = f"{self.base_url}/api/v1/search/tags"
        response = requests.post(url, json=criteria)
        response.raise_for_status()
        return response.json()
    
    def get_statistics(self):
        """Get system statistics"""
        url = f"{self.base_url}/api/v1/stats"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def export_tags(self, format="json", start_date=None, end_date=None):
        """Export tags in specified format"""
        url = f"{self.base_url}/api/v1/export"
        params = {"format": format}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json() if format == "json" else response.text

# Usage example
client = LabelRouterClient()

# Tag content
result = client.tag_content("緊急：基礎工事で重大な問題が発生しました。")
print(f"Priority: {result['tags']['priority']}")  # Should be "高" (HIGH)

# Get statistics
stats = client.get_statistics()
print(f"Total tagged contents: {stats['total_tagged_contents']}")
```

## cURL Examples

### Tag Content

```bash
# Tag a single content
curl -X POST "http://localhost:8000/api/v1/tag" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "本日の会議で決定した事項を報告します。",
    "enable_ml": true,
    "enable_rules": true
  }'
```

### Batch Tag

```bash
# Tag multiple contents
curl -X POST "http://localhost:8000/api/v1/tag/batch?enable_ml=true&enable_rules=true" \
  -H "Content-Type: application/json" \
  -d '["テキスト1", "テキスト2", "テキスト3"]'
```

### Search Tags

```bash
# Search by tags
curl -X POST "http://localhost:8000/api/v1/search/tags" \
  -H "Content-Type: application/json" \
  -d '{
    "content_types": ["決定事項"],
    "domains": ["構造"],
    "limit": 10
  }'
```

### Get Statistics

```bash
# Get system statistics
curl -X GET "http://localhost:8000/api/v1/stats"
```

## JavaScript/TypeScript Examples

```typescript
// TypeScript client example
interface TagRequest {
  content: string;
  context?: Record<string, any>;
  enable_ml?: boolean;
  enable_rules?: boolean;
}

interface TagResponse {
  content_id: string;
  tags: {
    content_id: string;
    content_type?: string;
    domains: string[];
    priority?: string;
    stakeholders: string[];
    custom_tags: Array<{
      category: string;
      value: string;
      confidence: number;
      source: string;
    }>;
    created_at: string;
    updated_at?: string;
  };
  processing_time: number;
}

class LabelRouterClient {
  private baseUrl: string;

  constructor(baseUrl: string = 'http://localhost:8000') {
    this.baseUrl = baseUrl;
  }

  async tagContent(request: TagRequest): Promise<TagResponse> {
    const response = await fetch(`${this.baseUrl}/api/v1/tag`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(request)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }

  async searchTags(criteria: any): Promise<any> {
    const response = await fetch(`${this.baseUrl}/api/v1/search/tags`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(criteria)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  }
}

// Usage
const client = new LabelRouterClient();

async function example() {
  try {
    // Tag content
    const result = await client.tagContent({
      content: '施工管理の観点から、工程の見直しが必要です。',
      enable_ml: true,
      enable_rules: true
    });
    
    console.log('Content Type:', result.tags.content_type);
    console.log('Domains:', result.tags.domains);
    
    // Search by tags
    const searchResults = await client.searchTags({
      domains: ['施工管理'],
      limit: 5
    });
    
    console.log('Found:', searchResults.total, 'results');
  } catch (error) {
    console.error('Error:', error);
  }
}
```

## Integration Examples

### Webhook Integration

```python
# Example: Integrate with external system via webhook
import requests
from typing import Dict, Any

class TaggingWebhookHandler:
    def __init__(self, label_router_url: str, webhook_url: str):
        self.label_router_url = label_router_url
        self.webhook_url = webhook_url
    
    def process_and_notify(self, content: str, metadata: Dict[str, Any]):
        # Tag the content
        tag_response = requests.post(
            f"{self.label_router_url}/api/v1/tag",
            json={"content": content}
        ).json()
        
        # Prepare webhook payload
        webhook_payload = {
            "content_id": tag_response["content_id"],
            "tags": tag_response["tags"],
            "metadata": metadata,
            "timestamp": tag_response["tags"]["created_at"]
        }
        
        # Send to webhook
        webhook_response = requests.post(
            self.webhook_url,
            json=webhook_payload
        )
        
        return tag_response, webhook_response.status_code

# Usage
handler = TaggingWebhookHandler(
    "http://localhost:8000",
    "https://your-system.com/webhook"
)

result, status = handler.process_and_notify(
    "重要な決定事項があります。",
    {"meeting_id": "MTG-2024-001", "participants": ["A", "B", "C"]}
)
```

### Database Integration

```python
# Example: Store tagged content in database
import sqlite3
from datetime import datetime

class TaggedContentStorage:
    def __init__(self, label_router_url: str, db_path: str):
        self.label_router_url = label_router_url
        self.conn = sqlite3.connect(db_path)
        self._create_tables()
    
    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tagged_content (
                id INTEGER PRIMARY KEY,
                content_id TEXT UNIQUE,
                original_content TEXT,
                content_type TEXT,
                priority TEXT,
                domains TEXT,
                created_at TEXT
            )
        """)
        self.conn.commit()
    
    def process_and_store(self, content: str):
        # Tag the content
        response = requests.post(
            f"{self.label_router_url}/api/v1/tag",
            json={"content": content}
        ).json()
        
        # Store in database
        tags = response["tags"]
        self.conn.execute("""
            INSERT INTO tagged_content 
            (content_id, original_content, content_type, priority, domains, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            response["content_id"],
            content,
            tags.get("content_type"),
            tags.get("priority"),
            ",".join(tags.get("domains", [])),
            tags.get("created_at")
        ))
        self.conn.commit()
        
        return response["content_id"]
    
    def get_by_priority(self, priority: str):
        cursor = self.conn.execute(
            "SELECT * FROM tagged_content WHERE priority = ?",
            (priority,)
        )
        return cursor.fetchall()
```

## Running the System

### 1. Start the API Server

```bash
cd label-router
pip install -r requirements.txt
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Gradio UI Demo

```bash
python src/ui_demo.py
```

### 3. Test the API

```bash
# Check if API is running
curl http://localhost:8000/

# Tag some content
curl -X POST http://localhost:8000/api/v1/tag \
  -H "Content-Type: application/json" \
  -d '{"content": "テスト内容です。"}'
```