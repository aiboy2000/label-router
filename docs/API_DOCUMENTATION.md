# Label Router API Documentation

## Overview

The Label Router API provides intelligent tagging capabilities for construction meeting content. It combines rule-based and machine learning approaches to automatically categorize and tag text content across multiple dimensions.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication. For production use, implement appropriate authentication mechanisms.

## API Endpoints

### 1. Tag Single Content

**POST** `/api/v1/tag`

Tag a single piece of text content.

#### Request Body

```json
{
  "content": "本日の会議で基礎工事の工程について決定しました。",
  "context": {},
  "enable_ml": true,
  "enable_rules": true
}
```

#### Response

```json
{
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "tags": {
    "content_id": "123e4567-e89b-12d3-a456-426614174000",
    "content_type": "決定事項",
    "domains": ["構造", "工程"],
    "priority": "中",
    "stakeholders": ["施工者"],
    "custom_tags": [
      {
        "category": "ml_confidence",
        "value": "content_type:0.85",
        "confidence": 0.85,
        "source": "ml"
      }
    ],
    "created_at": "2024-01-15T10:30:00",
    "updated_at": null
  },
  "processing_time": 0.234
}
```

### 2. Batch Tag Contents

**POST** `/api/v1/tag/batch`

Tag multiple contents in a single request.

#### Request Body

```json
[
  "第一段のテキスト内容",
  "第二段のテキスト内容"
]
```

#### Query Parameters

- `enable_ml` (boolean): Enable ML-based tagging (default: true)
- `enable_rules` (boolean): Enable rule-based tagging (default: true)

#### Response

```json
[
  {
    "content_id": "...",
    "tags": {...},
    "processing_time": 0.234
  },
  {
    "content_id": "...",
    "tags": {...},
    "processing_time": 0.189
  }
]
```

### 3. Get Tags by Content ID

**GET** `/api/v1/tags/{content_id}`

Retrieve previously generated tags for a specific content ID.

#### Response

```json
{
  "content_id": "123e4567-e89b-12d3-a456-426614174000",
  "tags": {...},
  "processing_time": 0.0
}
```

### 4. Search by Tags

**POST** `/api/v1/search/tags`

Search for content based on tag criteria.

#### Request Body

```json
{
  "content_types": ["決定事項", "課題"],
  "domains": ["構造"],
  "priorities": ["高"],
  "stakeholders": ["施工者"],
  "start_date": "2024-01-01T00:00:00",
  "end_date": "2024-12-31T23:59:59",
  "limit": 100,
  "offset": 0
}
```

#### Response

```json
{
  "total": 25,
  "results": [
    {
      "content_id": "...",
      "tags": {...}
    }
  ]
}
```

### 5. Get Statistics

**GET** `/api/v1/stats`

Get system-wide tagging statistics.

#### Response

```json
{
  "total_tagged_contents": 1000,
  "content_type_distribution": {
    "決定事項": 350,
    "課題": 200,
    "行動項目": 300,
    "情報共有": 100,
    "議論": 50
  },
  "domain_distribution": {
    "構造": 400,
    "設備": 300,
    "施工管理": 500
  },
  "priority_distribution": {
    "高": 150,
    "中": 600,
    "低": 250
  },
  "stakeholder_distribution": {
    "施工者": 700,
    "設計者": 400,
    "発注者": 300
  }
}
```

### 6. Get Enumerations

Get available values for tag categories:

- **GET** `/api/v1/enums/content-types`
- **GET** `/api/v1/enums/domains`
- **GET** `/api/v1/enums/priorities`
- **GET** `/api/v1/enums/stakeholders`

#### Response Example

```json
[
  {"value": "決定事項", "name": "DECISION"},
  {"value": "課題", "name": "ISSUE"},
  {"value": "行動項目", "name": "ACTION_ITEM"}
]
```

### 7. Delete Tags

**DELETE** `/api/v1/tags/{content_id}`

Delete tags for a specific content ID.

#### Response

```json
{
  "message": "Tags deleted successfully",
  "content_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

### 8. Export Tags

**GET** `/api/v1/export`

Export tag data in various formats.

#### Query Parameters

- `start_date` (datetime): Filter by start date
- `end_date` (datetime): Filter by end date
- `format` (string): Export format - "json" or "csv" (default: "json")

#### Response

Returns data in the requested format.

## Tag Categories

### Content Types (内容タイプ)
- `決定事項` (DECISION) - Decision items
- `課題` (ISSUE) - Issues requiring attention
- `行動項目` (ACTION_ITEM) - Action items with assignees
- `情報共有` (INFORMATION) - Information sharing
- `議論` (DISCUSSION) - Discussion topics
- `その他` (OTHER) - Other content

### Domains (専門領域)
- `構造` (STRUCTURE) - Structural engineering
- `設備` (EQUIPMENT) - Equipment and facilities
- `施工管理` (CONSTRUCTION_MANAGEMENT) - Construction management
- `設計` (DESIGN) - Design related
- `安全` (SAFETY) - Safety matters
- `品質` (QUALITY) - Quality control
- `コスト` (COST) - Cost and budget
- `工程` (SCHEDULE) - Schedule and timeline
- `その他` (OTHER) - Other domains

### Priority Levels (優先度)
- `高` (HIGH) - High priority, urgent
- `中` (MEDIUM) - Medium priority, normal
- `低` (LOW) - Low priority, non-urgent

### Stakeholders (関係者)
- `発注者` (CLIENT) - Client/Owner
- `設計者` (DESIGNER) - Designer/Architect
- `施工者` (CONTRACTOR) - Main contractor
- `監理者` (SUPERVISOR) - Construction supervisor
- `協力業者` (SUBCONTRACTOR) - Subcontractors
- `その他` (OTHER) - Other stakeholders

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request format"
}
```

### 404 Not Found

```json
{
  "detail": "Content ID not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error message"
}
```

## Rate Limiting

Currently no rate limiting is implemented. For production use, implement appropriate rate limiting.

## CORS

CORS is enabled for all origins in development. Configure appropriately for production use.