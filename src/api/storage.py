import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import logging

from ..models.tags import (
    TagSet, TagSearchRequest,
    ContentType, Domain, Priority, Stakeholder
)


logger = logging.getLogger(__name__)


class TagStorage:
    """Storage system for tags using SQLite"""
    
    def __init__(self, db_path: str = "tags.db"):
        self.db_path = db_path
        self.conn = None
    
    def initialize(self):
        """Initialize the database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()
        logger.info(f"Database initialized at {self.db_path}")
    
    def _create_tables(self):
        """Create necessary tables"""
        cursor = self.conn.cursor()
        
        # Main tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                content_id TEXT PRIMARY KEY,
                content_type TEXT,
                priority TEXT,
                created_at TEXT,
                updated_at TEXT,
                tag_data TEXT
            )
        """)
        
        # Domains junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_domains (
                content_id TEXT,
                domain TEXT,
                FOREIGN KEY (content_id) REFERENCES tags(content_id)
            )
        """)
        
        # Stakeholders junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tag_stakeholders (
                content_id TEXT,
                stakeholder TEXT,
                FOREIGN KEY (content_id) REFERENCES tags(content_id)
            )
        """)
        
        # Custom tags table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_tags (
                content_id TEXT,
                category TEXT,
                value TEXT,
                confidence REAL,
                source TEXT,
                FOREIGN KEY (content_id) REFERENCES tags(content_id)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_content_type ON tags(content_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_priority ON tags(priority)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON tags(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_domains ON tag_domains(domain)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stakeholders ON tag_stakeholders(stakeholder)")
        
        self.conn.commit()
    
    def store_tags(self, content_id: str, tag_set: TagSet):
        """Store tags in the database"""
        cursor = self.conn.cursor()
        
        try:
            # Store main tag data
            cursor.execute("""
                INSERT OR REPLACE INTO tags 
                (content_id, content_type, priority, created_at, updated_at, tag_data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                content_id,
                tag_set.content_type.value if tag_set.content_type else None,
                tag_set.priority.value if tag_set.priority else None,
                tag_set.created_at.isoformat(),
                tag_set.updated_at.isoformat() if tag_set.updated_at else None,
                tag_set.json()
            ))
            
            # Clear existing domain and stakeholder associations
            cursor.execute("DELETE FROM tag_domains WHERE content_id = ?", (content_id,))
            cursor.execute("DELETE FROM tag_stakeholders WHERE content_id = ?", (content_id,))
            cursor.execute("DELETE FROM custom_tags WHERE content_id = ?", (content_id,))
            
            # Store domains
            for domain in tag_set.domains:
                cursor.execute(
                    "INSERT INTO tag_domains (content_id, domain) VALUES (?, ?)",
                    (content_id, domain.value)
                )
            
            # Store stakeholders
            for stakeholder in tag_set.stakeholders:
                cursor.execute(
                    "INSERT INTO tag_stakeholders (content_id, stakeholder) VALUES (?, ?)",
                    (content_id, stakeholder.value)
                )
            
            # Store custom tags
            for tag in tag_set.custom_tags:
                cursor.execute("""
                    INSERT INTO custom_tags 
                    (content_id, category, value, confidence, source)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    content_id, tag.category, tag.value, tag.confidence, tag.source
                ))
            
            self.conn.commit()
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to store tags: {e}")
            raise
    
    def get_tags(self, content_id: str) -> Optional[TagSet]:
        """Retrieve tags for a content ID"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT tag_data FROM tags WHERE content_id = ?", (content_id,))
        row = cursor.fetchone()
        
        if row:
            return TagSet.parse_raw(row["tag_data"])
        return None
    
    def search_by_tags(self, search_request: TagSearchRequest) -> List[Dict[str, Any]]:
        """Search for content by tags"""
        cursor = self.conn.cursor()
        
        # Build query
        query = "SELECT DISTINCT t.content_id, t.tag_data FROM tags t"
        conditions = []
        params = []
        joins = []
        
        # Content type filter
        if search_request.content_types:
            type_conditions = " OR ".join(["t.content_type = ?" for _ in search_request.content_types])
            conditions.append(f"({type_conditions})")
            params.extend([ct.value for ct in search_request.content_types])
        
        # Priority filter
        if search_request.priorities:
            priority_conditions = " OR ".join(["t.priority = ?" for _ in search_request.priorities])
            conditions.append(f"({priority_conditions})")
            params.extend([p.value for p in search_request.priorities])
        
        # Domain filter
        if search_request.domains:
            joins.append("JOIN tag_domains td ON t.content_id = td.content_id")
            domain_conditions = " OR ".join(["td.domain = ?" for _ in search_request.domains])
            conditions.append(f"({domain_conditions})")
            params.extend([d.value for d in search_request.domains])
        
        # Stakeholder filter
        if search_request.stakeholders:
            joins.append("JOIN tag_stakeholders ts ON t.content_id = ts.content_id")
            stakeholder_conditions = " OR ".join(["ts.stakeholder = ?" for _ in search_request.stakeholders])
            conditions.append(f"({stakeholder_conditions})")
            params.extend([s.value for s in search_request.stakeholders])
        
        # Date range filter
        if search_request.start_date:
            conditions.append("t.created_at >= ?")
            params.append(search_request.start_date.isoformat())
        
        if search_request.end_date:
            conditions.append("t.created_at <= ?")
            params.append(search_request.end_date.isoformat())
        
        # Build final query
        if joins:
            query += " " + " ".join(joins)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY t.created_at DESC"
        query += f" LIMIT {search_request.limit} OFFSET {search_request.offset}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            tag_set = TagSet.parse_raw(row["tag_data"])
            results.append({
                "content_id": row["content_id"],
                "tags": tag_set.dict()
            })
        
        return results
    
    def delete_tags(self, content_id: str) -> bool:
        """Delete tags for a content ID"""
        cursor = self.conn.cursor()
        
        try:
            # Check if exists
            cursor.execute("SELECT 1 FROM tags WHERE content_id = ?", (content_id,))
            if not cursor.fetchone():
                return False
            
            # Delete from all tables
            cursor.execute("DELETE FROM custom_tags WHERE content_id = ?", (content_id,))
            cursor.execute("DELETE FROM tag_stakeholders WHERE content_id = ?", (content_id,))
            cursor.execute("DELETE FROM tag_domains WHERE content_id = ?", (content_id,))
            cursor.execute("DELETE FROM tags WHERE content_id = ?", (content_id,))
            
            self.conn.commit()
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"Failed to delete tags: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        cursor = self.conn.cursor()
        
        stats = {
            "total_tagged_contents": 0,
            "content_type_distribution": {},
            "domain_distribution": {},
            "priority_distribution": {},
            "stakeholder_distribution": {}
        }
        
        # Total count
        cursor.execute("SELECT COUNT(*) as count FROM tags")
        stats["total_tagged_contents"] = cursor.fetchone()["count"]
        
        # Content type distribution
        cursor.execute("""
            SELECT content_type, COUNT(*) as count 
            FROM tags 
            WHERE content_type IS NOT NULL 
            GROUP BY content_type
        """)
        for row in cursor.fetchall():
            stats["content_type_distribution"][row["content_type"]] = row["count"]
        
        # Domain distribution
        cursor.execute("""
            SELECT domain, COUNT(*) as count 
            FROM tag_domains 
            GROUP BY domain
        """)
        for row in cursor.fetchall():
            stats["domain_distribution"][row["domain"]] = row["count"]
        
        # Priority distribution
        cursor.execute("""
            SELECT priority, COUNT(*) as count 
            FROM tags 
            WHERE priority IS NOT NULL 
            GROUP BY priority
        """)
        for row in cursor.fetchall():
            stats["priority_distribution"][row["priority"]] = row["count"]
        
        # Stakeholder distribution
        cursor.execute("""
            SELECT stakeholder, COUNT(*) as count 
            FROM tag_stakeholders 
            GROUP BY stakeholder
        """)
        for row in cursor.fetchall():
            stats["stakeholder_distribution"][row["stakeholder"]] = row["count"]
        
        return stats
    
    def export_tags(
        self, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json"
    ) -> Any:
        """Export tags in specified format"""
        cursor = self.conn.cursor()
        
        query = "SELECT content_id, tag_data FROM tags"
        conditions = []
        params = []
        
        if start_date:
            conditions.append("created_at >= ?")
            params.append(start_date.isoformat())
        
        if end_date:
            conditions.append("created_at <= ?")
            params.append(end_date.isoformat())
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if format == "json":
            results = []
            for row in rows:
                tag_set = TagSet.parse_raw(row["tag_data"])
                results.append({
                    "content_id": row["content_id"],
                    "tags": tag_set.dict()
                })
            return results
        
        elif format == "csv":
            # Simple CSV export
            csv_lines = ["content_id,content_type,domains,priority,stakeholders,created_at"]
            
            for row in rows:
                tag_set = TagSet.parse_raw(row["tag_data"])
                csv_lines.append(",".join([
                    row["content_id"],
                    tag_set.content_type.value if tag_set.content_type else "",
                    ";".join([d.value for d in tag_set.domains]),
                    tag_set.priority.value if tag_set.priority else "",
                    ";".join([s.value for s in tag_set.stakeholders]),
                    tag_set.created_at.isoformat()
                ]))
            
            return "\n".join(csv_lines)
        
        else:
            raise ValueError(f"Unsupported format: {format}")