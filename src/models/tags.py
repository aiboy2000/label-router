from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ContentType(str, Enum):
    """Content type enumeration"""
    DECISION = "決定事項"  # Decision items
    ISSUE = "課題"  # Issues
    ACTION_ITEM = "行動項目"  # Action items
    INFORMATION = "情報共有"  # Information sharing
    DISCUSSION = "議論"  # Discussion
    OTHER = "その他"  # Other


class Domain(str, Enum):
    """Professional domain enumeration"""
    STRUCTURE = "構造"  # Structure
    EQUIPMENT = "設備"  # Equipment
    CONSTRUCTION_MANAGEMENT = "施工管理"  # Construction management
    DESIGN = "設計"  # Design
    SAFETY = "安全"  # Safety
    QUALITY = "品質"  # Quality
    COST = "コスト"  # Cost
    SCHEDULE = "工程"  # Schedule
    OTHER = "その他"  # Other


class Priority(str, Enum):
    """Priority levels"""
    HIGH = "高"  # High
    MEDIUM = "中"  # Medium
    LOW = "低"  # Low


class Stakeholder(str, Enum):
    """Stakeholder types"""
    CLIENT = "発注者"  # Client
    DESIGNER = "設計者"  # Designer
    CONTRACTOR = "施工者"  # Contractor
    SUPERVISOR = "監理者"  # Supervisor
    SUBCONTRACTOR = "協力業者"  # Subcontractor
    OTHER = "その他"  # Other


class Tag(BaseModel):
    """Individual tag model"""
    category: str = Field(..., description="Tag category (e.g., content_type, domain, priority)")
    value: str = Field(..., description="Tag value")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="Confidence score for ML-generated tags")
    source: str = Field("manual", description="Tag source: manual, rule, ml")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class TagSet(BaseModel):
    """Complete tag set for a piece of content"""
    content_id: str = Field(..., description="Unique identifier for the content")
    content_type: Optional[ContentType] = Field(None, description="Type of content")
    domains: List[Domain] = Field(default_factory=list, description="Related professional domains")
    priority: Optional[Priority] = Field(None, description="Priority level")
    stakeholders: List[Stakeholder] = Field(default_factory=list, description="Related stakeholders")
    custom_tags: List[Tag] = Field(default_factory=list, description="Custom tags")
    created_at: datetime = Field(default_factory=datetime.now, description="Timestamp of tag creation")
    updated_at: Optional[datetime] = Field(None, description="Timestamp of last update")


class TagRequest(BaseModel):
    """Request model for tagging content"""
    content: str = Field(..., description="Text content to be tagged")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context for tagging")
    enable_ml: bool = Field(True, description="Enable ML-based tagging")
    enable_rules: bool = Field(True, description="Enable rule-based tagging")


class TagResponse(BaseModel):
    """Response model for tagging results"""
    content_id: str = Field(..., description="Generated content ID")
    tags: TagSet = Field(..., description="Generated tags")
    processing_time: float = Field(..., description="Processing time in seconds")
    
    
class TagSearchRequest(BaseModel):
    """Request model for searching by tags"""
    content_types: Optional[List[ContentType]] = None
    domains: Optional[List[Domain]] = None
    priorities: Optional[List[Priority]] = None
    stakeholders: Optional[List[Stakeholder]] = None
    custom_tags: Optional[List[str]] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)