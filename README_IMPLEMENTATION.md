# Label Router - Intelligent Tagging System

This implementation provides the intelligent tagging system component from the original Label Router project specification. It offers both rule-based and ML-based tagging for construction meeting content.

## Features

- **Multi-dimensional Tagging**: Categorizes content by type, domain, priority, and stakeholders
- **Dual Approach**: Combines rule-based patterns with ML-based semantic understanding
- **REST API**: Full-featured API for integration with external systems
- **Japanese Language Support**: Optimized for Japanese construction terminology
- **Real-time Processing**: Fast tagging with sub-second response times
- **Persistent Storage**: SQLite-based storage for tagged content
- **Web UI Demo**: Gradio-based interface for testing

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API Server

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start the UI Demo (Optional)

```bash
python src/ui_demo.py
```

## API Usage

### Tag Content

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/tag",
    json={
        "content": "本日の会議で基礎工事の工程について決定しました。",
        "enable_ml": True,
        "enable_rules": True
    }
)

result = response.json()
print(f"Content Type: {result['tags']['content_type']}")
print(f"Domains: {result['tags']['domains']}")
print(f"Priority: {result['tags']['priority']}")
```

### Search by Tags

```python
response = requests.post(
    "http://localhost:8000/api/v1/search/tags",
    json={
        "content_types": ["決定事項"],
        "domains": ["構造"],
        "limit": 10
    }
)

results = response.json()
```

## Tag Categories

### Content Types
- `決定事項` - Decision items
- `課題` - Issues
- `行動項目` - Action items
- `情報共有` - Information sharing
- `議論` - Discussion

### Domains
- `構造` - Structure
- `設備` - Equipment
- `施工管理` - Construction management
- `設計` - Design
- `安全` - Safety
- `品質` - Quality
- `コスト` - Cost
- `工程` - Schedule

### Priority Levels
- `高` - High
- `中` - Medium
- `低` - Low

### Stakeholders
- `発注者` - Client
- `設計者` - Designer
- `施工者` - Contractor
- `監理者` - Supervisor
- `協力業者` - Subcontractor

## Project Structure

```
label-router/
├── src/
│   ├── api/
│   │   ├── main.py         # FastAPI application
│   │   └── storage.py      # Database operations
│   ├── core/
│   │   ├── rule_tagger.py  # Rule-based tagging
│   │   ├── ml_tagger.py    # ML-based tagging
│   │   └── smart_tagger.py # Combined tagger
│   ├── models/
│   │   └── tags.py         # Data models
│   └── ui_demo.py          # Gradio demo
├── docs/
│   ├── API_DOCUMENTATION.md
│   └── USAGE_EXAMPLES.md
├── requirements.txt
└── setup.py
```

## Integration

The system provides REST API endpoints for easy integration:

- **POST /api/v1/tag** - Tag single content
- **POST /api/v1/tag/batch** - Batch tag multiple contents
- **GET /api/v1/tags/{id}** - Retrieve tags
- **POST /api/v1/search/tags** - Search by tags
- **GET /api/v1/stats** - Get statistics
- **GET /api/v1/export** - Export data

See [API Documentation](docs/API_DOCUMENTATION.md) for complete details.

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black src/
flake8 src/
```

## License

This is a verification project for demonstration purposes.