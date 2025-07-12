import time
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from .rule_tagger import RuleTagger
from .ml_tagger import MLTagger
from ..models.tags import (
    TagSet, TagRequest, TagResponse, Tag,
    ContentType, Domain, Priority, Stakeholder
)


logger = logging.getLogger(__name__)


class SmartTagger:
    """Smart tagger that combines rule-based and ML-based tagging approaches"""
    
    def __init__(self, enable_ml: bool = True):
        """Initialize smart tagger
        
        Args:
            enable_ml: Whether to enable ML-based tagging (requires model download)
        """
        self.rule_tagger = RuleTagger()
        self.ml_tagger = None
        
        if enable_ml:
            try:
                self.ml_tagger = MLTagger()
                logger.info("ML tagger initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize ML tagger: {e}")
                logger.warning("Continuing with rule-based tagging only")
    
    def tag(self, request: TagRequest) -> TagResponse:
        """Tag content using both rule-based and ML-based approaches"""
        start_time = time.time()
        
        # Generate content ID
        content_id = str(uuid.uuid4())
        
        # Initialize tag results
        combined_tags = {
            "content_type": None,
            "domains": [],
            "priority": None,
            "stakeholders": [],
            "custom_tags": []
        }
        
        # Apply rule-based tagging if enabled
        if request.enable_rules:
            rule_tags = self.rule_tagger.tag_content(
                request.content, 
                request.context
            )
            combined_tags = self._merge_tags(combined_tags, rule_tags, "rule")
        
        # Apply ML-based tagging if enabled and available
        if request.enable_ml and self.ml_tagger:
            try:
                ml_tags = self.ml_tagger.tag_content(
                    request.content,
                    request.context
                )
                combined_tags = self._merge_tags(combined_tags, ml_tags, "ml")
            except Exception as e:
                logger.error(f"ML tagging failed: {e}")
                # Add error tag
                combined_tags["custom_tags"].append(Tag(
                    category="error",
                    value="ml_tagging_failed",
                    confidence=0.0,
                    source="system"
                ))
        
        # Create TagSet
        tag_set = TagSet(
            content_id=content_id,
            content_type=combined_tags["content_type"],
            domains=combined_tags["domains"],
            priority=combined_tags["priority"],
            stakeholders=combined_tags["stakeholders"],
            custom_tags=combined_tags["custom_tags"],
            created_at=datetime.now()
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create and return response
        return TagResponse(
            content_id=content_id,
            tags=tag_set,
            processing_time=processing_time
        )
    
    def _merge_tags(
        self, 
        current_tags: Dict[str, Any], 
        new_tags: Dict[str, Any], 
        source: str
    ) -> Dict[str, Any]:
        """Merge tags from different sources with conflict resolution"""
        
        # Merge content type (prefer ML if confidence is high)
        if new_tags.get("content_type"):
            if not current_tags["content_type"]:
                current_tags["content_type"] = new_tags["content_type"]
            elif source == "ml":
                # Check ML confidence
                ml_confidence = self._get_ml_confidence(new_tags, "content_type")
                if ml_confidence > 0.7:  # High confidence threshold
                    current_tags["content_type"] = new_tags["content_type"]
        
        # Merge domains (union of all detected domains)
        for domain in new_tags.get("domains", []):
            if domain not in current_tags["domains"]:
                current_tags["domains"].append(domain)
        
        # Merge priority (prefer higher priority)
        if new_tags.get("priority"):
            if not current_tags["priority"]:
                current_tags["priority"] = new_tags["priority"]
            else:
                # Compare priorities
                priority_order = [Priority.LOW, Priority.MEDIUM, Priority.HIGH]
                current_idx = priority_order.index(current_tags["priority"])
                new_idx = priority_order.index(new_tags["priority"])
                if new_idx > current_idx:
                    current_tags["priority"] = new_tags["priority"]
        
        # Merge stakeholders (union)
        for stakeholder in new_tags.get("stakeholders", []):
            if stakeholder not in current_tags["stakeholders"]:
                current_tags["stakeholders"].append(stakeholder)
        
        # Merge custom tags
        current_tags["custom_tags"].extend(new_tags.get("custom_tags", []))
        
        return current_tags
    
    def _get_ml_confidence(self, tags: Dict[str, Any], category: str) -> float:
        """Extract ML confidence for a specific category from tags"""
        for tag in tags.get("custom_tags", []):
            if (tag.category == "ml_confidence" and 
                tag.value.startswith(f"{category}:")):
                try:
                    return float(tag.value.split(":")[1])
                except:
                    pass
        return 0.0
    
    def batch_tag(self, contents: List[str], **kwargs) -> List[TagResponse]:
        """Tag multiple contents in batch"""
        responses = []
        
        for content in contents:
            request = TagRequest(content=content, **kwargs)
            response = self.tag(request)
            responses.append(response)
        
        return responses