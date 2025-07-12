from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import logging
from datetime import datetime

from ..core.smart_tagger import SmartTagger
from ..models.tags import (
    TagRequest, TagResponse, TagSearchRequest,
    ContentType, Domain, Priority, Stakeholder
)
from .storage import TagStorage


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Label Router - Intelligent Tagging System",
    description="API for intelligent tagging of construction meeting content",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
smart_tagger = SmartTagger(enable_ml=True)
tag_storage = TagStorage()


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    logger.info("Label Router API starting up...")
    tag_storage.initialize()
    logger.info("Label Router API ready")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Label Router - Intelligent Tagging System",
        "version": "0.1.0",
        "status": "running"
    }


@app.post("/api/v1/tag", response_model=TagResponse)
async def tag_content(request: TagRequest):
    """
    Tag a single piece of content
    
    This endpoint analyzes the provided text content and generates appropriate tags
    using both rule-based and ML-based approaches.
    """
    try:
        response = smart_tagger.tag(request)
        
        # Store tags
        tag_storage.store_tags(response.content_id, response.tags)
        
        return response
    except Exception as e:
        logger.error(f"Tagging failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/tag/batch", response_model=List[TagResponse])
async def tag_contents_batch(contents: List[str], enable_ml: bool = True, enable_rules: bool = True):
    """
    Tag multiple contents in batch
    
    This endpoint processes multiple text contents and returns tags for each.
    """
    try:
        responses = []
        for content in contents:
            request = TagRequest(
                content=content,
                enable_ml=enable_ml,
                enable_rules=enable_rules
            )
            response = smart_tagger.tag(request)
            
            # Store tags
            tag_storage.store_tags(response.content_id, response.tags)
            
            responses.append(response)
        
        return responses
    except Exception as e:
        logger.error(f"Batch tagging failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/tags/{content_id}", response_model=TagResponse)
async def get_tags(content_id: str):
    """
    Retrieve tags for a specific content ID
    """
    tags = tag_storage.get_tags(content_id)
    if not tags:
        raise HTTPException(status_code=404, detail="Content ID not found")
    
    return TagResponse(
        content_id=content_id,
        tags=tags,
        processing_time=0.0  # Not available for retrieved tags
    )


@app.post("/api/v1/search/tags")
async def search_by_tags(search_request: TagSearchRequest):
    """
    Search for content by tags
    
    This endpoint allows searching for previously tagged content based on
    various tag criteria.
    """
    try:
        results = tag_storage.search_by_tags(search_request)
        return {
            "total": len(results),
            "results": results
        }
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/stats")
async def get_statistics():
    """
    Get tagging system statistics
    """
    stats = tag_storage.get_statistics()
    return stats


@app.get("/api/v1/enums/content-types")
async def get_content_types():
    """Get all available content types"""
    return [{"value": ct.value, "name": ct.name} for ct in ContentType]


@app.get("/api/v1/enums/domains")
async def get_domains():
    """Get all available domains"""
    return [{"value": d.value, "name": d.name} for d in Domain]


@app.get("/api/v1/enums/priorities")
async def get_priorities():
    """Get all available priorities"""
    return [{"value": p.value, "name": p.name} for p in Priority]


@app.get("/api/v1/enums/stakeholders")
async def get_stakeholders():
    """Get all available stakeholders"""
    return [{"value": s.value, "name": s.name} for s in Stakeholder]


@app.delete("/api/v1/tags/{content_id}")
async def delete_tags(content_id: str):
    """
    Delete tags for a specific content ID
    """
    success = tag_storage.delete_tags(content_id)
    if not success:
        raise HTTPException(status_code=404, detail="Content ID not found")
    
    return {"message": "Tags deleted successfully", "content_id": content_id}


@app.get("/api/v1/export")
async def export_tags(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    format: str = Query("json", regex="^(json|csv)$")
):
    """
    Export tags in various formats
    
    This endpoint allows exporting tag data for integration with other systems.
    """
    try:
        data = tag_storage.export_tags(start_date, end_date, format)
        return data
    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)