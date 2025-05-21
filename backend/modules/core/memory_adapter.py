#!/usr/bin/env python3
# SecureScout - Memory Adapter for Claude Taskmaster Integration

import os
import json
import logging
import sqlite3
import datetime
from typing import Dict, Any, Optional, List, Union

# Configure logging
logger = logging.getLogger("securescout.memory")

class MemoryAdapter:
    """
    Memory adapter for storing and retrieving Claude Taskmaster compatible memory entries.
    This provides a persistence layer for AI memory that can be used by both the backend
    and the frontend taskmaster integration.
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the memory adapter.
        
        Args:
            db_path: Path to SQLite database file. If None, uses in-memory database.
        """
        self.db_path = db_path or ':memory:'
        self.conn = None
        self._init_db()
    
    def _init_db(self):
        """Initialize the database connection and create tables if needed."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            cursor = self.conn.cursor()
            
            # Create memory table
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            ''')
            
            # Create memory_lock table for concurrency control
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory_lock (
                key TEXT PRIMARY KEY,
                locked_at TEXT NOT NULL,
                lock_expiry TEXT NOT NULL
            )
            ''')
            
            self.conn.commit()
            logger.info(f"Memory adapter initialized with database at {self.db_path}")
        except Exception as e:
            logger.error(f"Error initializing memory database: {e}")
            raise
    
    def _ensure_connection(self):
        """Ensure database connection is active."""
        if not self.conn:
            self._init_db()
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a memory value.
        
        Args:
            key: Memory key
            value: Memory value (will be serialized to JSON)
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connection()
        
        try:
            # Serialize value to JSON
            json_value = json.dumps(value)
            
            now = datetime.datetime.utcnow().isoformat()
            
            cursor = self.conn.cursor()
            cursor.execute(
                '''
                INSERT OR REPLACE INTO memory (key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                ''',
                (key, json_value, now, now)
            )
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error setting memory key '{key}': {e}")
            return False
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a memory value.
        
        Args:
            key: Memory key
            
        Returns:
            The deserialized value, or None if not found
        """
        self._ensure_connection()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT value FROM memory WHERE key = ?', (key,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Deserialize JSON
            value = json.loads(row[0])
            return value
        except Exception as e:
            logger.error(f"Error getting memory key '{key}': {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """
        Delete a memory value.
        
        Args:
            key: Memory key
            
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connection()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM memory WHERE key = ?', (key,))
            
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error deleting memory key '{key}': {e}")
            return False
    
    def list_keys(self, prefix: Optional[str] = None) -> List[str]:
        """
        List all memory keys, optionally filtered by prefix.
        
        Args:
            prefix: Optional key prefix to filter by
            
        Returns:
            List of matching keys
        """
        self._ensure_connection()
        
        try:
            cursor = self.conn.cursor()
            
            if prefix:
                cursor.execute('SELECT key FROM memory WHERE key LIKE ?', (f"{prefix}%",))
            else:
                cursor.execute('SELECT key FROM memory')
            
            return [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error listing memory keys: {e}")
            return []
    
    def clear(self) -> bool:
        """
        Clear all memory values.
        
        Returns:
            True if successful, False otherwise
        """
        self._ensure_connection()
        
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM memory')
            
            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"Error clearing memory: {e}")
            return False
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __del__(self):
        """Clean up on garbage collection."""
        self.close()


class TaskMasterMemoryManager:
    """
    Manager class for integrating with Claude Taskmaster memory.
    This class provides methods that match the Taskmaster memory API.
    """
    
    def __init__(self, adapter: Optional[MemoryAdapter] = None, db_path: Optional[str] = None):
        """
        Initialize the memory manager.
        
        Args:
            adapter: Optional memory adapter instance
            db_path: Path to SQLite database file (used if adapter not provided)
        """
        self.adapter = adapter or MemoryAdapter(db_path)
    
    async def get(self, key: str) -> Any:
        """
        Get a memory value (async API compatible with Taskmaster).
        
        Args:
            key: Memory key
            
        Returns:
            The value, or None if not found
        """
        return self.adapter.get(key)
    
    async def set(self, key: str, value: Any) -> bool:
        """
        Set a memory value (async API compatible with Taskmaster).
        
        Args:
            key: Memory key
            value: Memory value
            
        Returns:
            True if successful
        """
        return self.adapter.set(key, value)
    
    async def delete(self, key: str) -> bool:
        """
        Delete a memory value (async API compatible with Taskmaster).
        
        Args:
            key: Memory key
            
        Returns:
            True if successful
        """
        return self.adapter.delete(key)
    
    async def list(self, prefix: Optional[str] = None) -> List[str]:
        """
        List memory keys (async API compatible with Taskmaster).
        
        Args:
            prefix: Optional key prefix filter
            
        Returns:
            List of matching keys
        """
        return self.adapter.list_keys(prefix)
    
    async def clear(self) -> bool:
        """
        Clear all memory (async API compatible with Taskmaster).
        
        Returns:
            True if successful
        """
        return self.adapter.clear()


# Singleton memory manager instance
memory_manager = None

def get_memory_manager(db_path: Optional[str] = None) -> TaskMasterMemoryManager:
    """
    Get or create the singleton memory manager instance.
    
    Args:
        db_path: Optional database path
        
    Returns:
        TaskMasterMemoryManager instance
    """
    global memory_manager
    if not memory_manager:
        # Default DB path in the data directory
        if not db_path:
            from config import Config
            db_path = os.path.join(Config.DATA_DIR, 'memory.db')
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        memory_manager = TaskMasterMemoryManager(db_path=db_path)
    
    return memory_manager


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create in-memory adapter for testing
    adapter = MemoryAdapter()
    
    # Example operations
    print("Setting value...")
    adapter.set("test_key", {"message": "Hello from memory adapter!", "timestamp": datetime.datetime.utcnow().isoformat()})
    
    print("Getting value...")
    value = adapter.get("test_key")
    print(f"Retrieved value: {value}")
    
    print("Listing keys...")
    keys = adapter.list_keys()
    print(f"Keys: {keys}")
    
    print("Deleting key...")
    deleted = adapter.delete("test_key")
    print(f"Deleted: {deleted}")
    
    print("Memory test complete.")