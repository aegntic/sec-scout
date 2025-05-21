"""
Tests for the memory adapter module.
"""

import os
import pytest
import tempfile
from datetime import datetime

from backend.modules.core.memory_adapter import MemoryAdapter, TaskMasterMemoryManager

class TestMemoryAdapter:
    """Tests for the MemoryAdapter class."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create a temporary database file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def memory_adapter(self, temp_db_path):
        """Create a memory adapter instance with a temporary database."""
        adapter = MemoryAdapter(db_path=temp_db_path)
        yield adapter
        adapter.close()
    
    @pytest.fixture
    def in_memory_adapter(self):
        """Create an in-memory adapter instance."""
        adapter = MemoryAdapter(db_path=':memory:')
        yield adapter
        adapter.close()
    
    def test_set_and_get(self, memory_adapter):
        """Test setting and getting values."""
        # Set a string value
        assert memory_adapter.set('test_key', 'test_value') is True
        assert memory_adapter.get('test_key') == 'test_value'
        
        # Set a more complex value
        complex_value = {
            'name': 'Test Object',
            'created_at': datetime.utcnow().isoformat(),
            'values': [1, 2, 3],
            'nested': {
                'key': 'value'
            }
        }
        
        assert memory_adapter.set('complex_key', complex_value) is True
        retrieved = memory_adapter.get('complex_key')
        
        assert retrieved is not None
        assert retrieved['name'] == 'Test Object'
        assert 'created_at' in retrieved
        assert retrieved['values'] == [1, 2, 3]
        assert retrieved['nested']['key'] == 'value'
        
        # Get non-existent key
        assert memory_adapter.get('non_existent') is None
    
    def test_delete(self, memory_adapter):
        """Test deleting values."""
        # Set a value
        memory_adapter.set('to_delete', 'delete_me')
        assert memory_adapter.get('to_delete') == 'delete_me'
        
        # Delete it
        assert memory_adapter.delete('to_delete') is True
        assert memory_adapter.get('to_delete') is None
        
        # Delete non-existent key
        assert memory_adapter.delete('non_existent') is False
    
    def test_list_keys(self, memory_adapter):
        """Test listing keys."""
        # Set multiple values with different prefixes
        memory_adapter.set('test_1', 'value_1')
        memory_adapter.set('test_2', 'value_2')
        memory_adapter.set('other_1', 'other_value_1')
        
        # List all keys
        all_keys = memory_adapter.list_keys()
        assert len(all_keys) == 3
        assert 'test_1' in all_keys
        assert 'test_2' in all_keys
        assert 'other_1' in all_keys
        
        # List keys with prefix
        test_keys = memory_adapter.list_keys(prefix='test_')
        assert len(test_keys) == 2
        assert 'test_1' in test_keys
        assert 'test_2' in test_keys
        assert 'other_1' not in test_keys
        
        # List keys with non-matching prefix
        non_matching = memory_adapter.list_keys(prefix='nonexistent_')
        assert len(non_matching) == 0
    
    def test_clear(self, memory_adapter):
        """Test clearing all values."""
        # Set multiple values
        memory_adapter.set('key1', 'value1')
        memory_adapter.set('key2', 'value2')
        
        # Verify they were set
        assert memory_adapter.get('key1') == 'value1'
        assert memory_adapter.get('key2') == 'value2'
        
        # Clear all values
        assert memory_adapter.clear() is True
        
        # Verify they were cleared
        assert memory_adapter.get('key1') is None
        assert memory_adapter.get('key2') is None
        
        # List keys should be empty
        assert len(memory_adapter.list_keys()) == 0
    
    def test_persistence(self, temp_db_path):
        """Test that values persist after closing and reopening the adapter."""
        # Create adapter and set values
        adapter1 = MemoryAdapter(db_path=temp_db_path)
        adapter1.set('persistent', 'value')
        adapter1.close()
        
        # Create new adapter with same db path
        adapter2 = MemoryAdapter(db_path=temp_db_path)
        
        # Verify value persisted
        assert adapter2.get('persistent') == 'value'
        adapter2.close()
    
    def test_in_memory_isolation(self, in_memory_adapter):
        """Test that in-memory adapter is isolated."""
        # Set value in first adapter
        in_memory_adapter.set('temp', 'value')
        
        # Create second in-memory adapter
        adapter2 = MemoryAdapter(db_path=':memory:')
        
        # Verify value doesn't exist in second adapter
        assert adapter2.get('temp') is None
        adapter2.close()
    
    def test_concurrency(self, memory_adapter):
        """Test concurrency with multiple operations."""
        # Set multiple values in quick succession
        for i in range(100):
            memory_adapter.set(f'concurrent_{i}', f'value_{i}')
        
        # Verify all values were set correctly
        for i in range(100):
            assert memory_adapter.get(f'concurrent_{i}') == f'value_{i}'
        
        # Update values in quick succession
        for i in range(100):
            memory_adapter.set(f'concurrent_{i}', f'updated_{i}')
        
        # Verify all values were updated correctly
        for i in range(100):
            assert memory_adapter.get(f'concurrent_{i}') == f'updated_{i}'
        
        # Delete values in quick succession
        for i in range(100):
            memory_adapter.delete(f'concurrent_{i}')
        
        # Verify all values were deleted
        for i in range(100):
            assert memory_adapter.get(f'concurrent_{i}') is None


class TestTaskMasterMemoryManager:
    """Tests for the TaskMasterMemoryManager class."""
    
    @pytest.fixture
    def memory_manager(self, memory_adapter):
        """Create a memory manager instance with a memory adapter."""
        return TaskMasterMemoryManager(adapter=memory_adapter)
    
    @pytest.mark.asyncio
    async def test_async_get_set(self, memory_manager):
        """Test the async get and set methods."""
        # Set a value
        result = await memory_manager.set('async_key', 'async_value')
        assert result is True
        
        # Get the value
        value = await memory_manager.get('async_key')
        assert value == 'async_value'
        
        # Get non-existent key
        value = await memory_manager.get('non_existent')
        assert value is None
    
    @pytest.mark.asyncio
    async def test_async_delete(self, memory_manager):
        """Test the async delete method."""
        # Set a value
        await memory_manager.set('to_delete_async', 'delete_me')
        
        # Delete it
        result = await memory_manager.delete('to_delete_async')
        assert result is True
        
        # Verify it's gone
        value = await memory_manager.get('to_delete_async')
        assert value is None
    
    @pytest.mark.asyncio
    async def test_async_list(self, memory_manager):
        """Test the async list method."""
        # Set values with different prefixes
        await memory_manager.set('prefix1_key1', 'value1')
        await memory_manager.set('prefix1_key2', 'value2')
        await memory_manager.set('prefix2_key1', 'value3')
        
        # List all keys
        keys = await memory_manager.list()
        assert len(keys) >= 3
        assert 'prefix1_key1' in keys
        assert 'prefix1_key2' in keys
        assert 'prefix2_key1' in keys
        
        # List keys with prefix
        keys = await memory_manager.list('prefix1_')
        assert len(keys) == 2
        assert 'prefix1_key1' in keys
        assert 'prefix1_key2' in keys
        assert 'prefix2_key1' not in keys
    
    @pytest.mark.asyncio
    async def test_async_clear(self, memory_manager):
        """Test the async clear method."""
        # Set multiple values
        await memory_manager.set('clear_key1', 'value1')
        await memory_manager.set('clear_key2', 'value2')
        
        # Clear all values
        result = await memory_manager.clear()
        assert result is True
        
        # Verify keys were cleared
        value1 = await memory_manager.get('clear_key1')
        value2 = await memory_manager.get('clear_key2')
        assert value1 is None
        assert value2 is None