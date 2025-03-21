"""
Unit tests for database operations.
"""
import pytest
import asyncio
from unittest.mock import Mock, patch
from core.database import Database, DatabaseError, ConnectionPool

@pytest.mark.unit
class TestDatabase:
    """Test suite for database operations."""
    
    @pytest.fixture
    async def db(self):
        """Fixture to provide a database instance with mock connection."""
        with patch('core.database.asyncpg.create_pool') as mock_create_pool:
            # Mock the connection pool
            mock_pool = Mock()
            mock_pool.acquire = Mock()
            mock_pool.release = Mock()
            mock_pool.close = Mock()
            
            # Mock successful connection
            mock_create_pool.return_value = mock_pool
            
            db = Database()
            await db.initialize()
            yield db
            
            # Cleanup
            await db.close()
    
    async def test_database_initialization(self):
        """Test database initialization and connection pool creation."""
        with patch('core.database.asyncpg.create_pool') as mock_create_pool:
            # Setup mock
            mock_pool = Mock()
            mock_create_pool.return_value = mock_pool
            
            # Test
            db = Database()
            await db.initialize()
            
            # Verify
            mock_create_pool.assert_called_once()
            assert db.pool == mock_pool
            
            # Cleanup
            await db.close()
            
    async def test_database_connection_error(self):
        """Test handling of database connection errors."""
        with patch('core.database.asyncpg.create_pool') as mock_create_pool:
            # Setup mock to raise an error
            mock_create_pool.side_effect = Exception("Connection failed")
            
            # Test
            db = Database()
            with pytest.raises(DatabaseError, match="Failed to initialize database"):
                await db.initialize()
                
    async def test_connection_pool_management(self, db):
        """Test connection pool acquisition and release."""
        # Setup mock connection
        mock_conn = Mock()
        db.pool.acquire.return_value = mock_conn
        
        # Test
        async with db.get_connection() as conn:
            assert conn == mock_conn
            
        # Verify
        db.pool.acquire.assert_called_once()
        db.pool.release.assert_called_once_with(mock_conn)
        
    async def test_query_execution(self, db):
        """Test query execution with parameters."""
        # Setup mock connection and result
        mock_conn = Mock()
        mock_result = [{"id": 1, "name": "test"}]
        mock_conn.fetch = Mock(return_value=mock_result)
        db.pool.acquire.return_value = mock_conn
        
        # Test
        query = "SELECT * FROM test WHERE id = $1"
        params = [1]
        async with db.get_connection() as conn:
            result = await db.execute_query(conn, query, params)
            
        # Verify
        assert result == mock_result
        mock_conn.fetch.assert_called_once_with(query, *params)
        
    async def test_transaction_management(self, db):
        """Test transaction management with commit and rollback."""
        # Setup mock connection
        mock_conn = Mock()
        mock_conn.transaction = Mock()
        db.pool.acquire.return_value = mock_conn
        
        # Test successful transaction
        async with db.transaction() as conn:
            await db.execute_query(conn, "INSERT INTO test VALUES ($1)", [1])
            
        # Verify transaction was committed
        mock_conn.transaction.assert_called_once()
        
        # Test failed transaction
        with pytest.raises(DatabaseError):
            async with db.transaction() as conn:
                await db.execute_query(conn, "BAD QUERY")
                
        # Verify transaction was rolled back
        assert mock_conn.transaction.call_count == 2
        
    async def test_connection_pool_limits(self, db):
        """Test connection pool respects size limits."""
        # Setup
        max_connections = 5
        db.pool.get_size = Mock(return_value=max_connections)
        db.pool.get_max_size = Mock(return_value=max_connections)
        
        # Create tasks to simulate concurrent connections
        async def get_connection():
            async with db.get_connection() as conn:
                await asyncio.sleep(0.1)  # Simulate work
                
        # Test
        tasks = [get_connection() for _ in range(max_connections + 1)]
        
        # Verify that attempting to exceed pool size raises error
        with pytest.raises(DatabaseError, match="Connection pool exhausted"):
            await asyncio.gather(*tasks)
            
    async def test_query_timeout(self, db):
        """Test query timeout handling."""
        # Setup mock connection with delayed response
        mock_conn = Mock()
        async def slow_query(*args):
            await asyncio.sleep(2)  # Simulate slow query
            return []
            
        mock_conn.fetch.side_effect = slow_query
        db.pool.acquire.return_value = mock_conn
        
        # Test
        with pytest.raises(asyncio.TimeoutError):
            async with db.get_connection() as conn:
                await asyncio.wait_for(
                    db.execute_query(conn, "SELECT * FROM test"),
                    timeout=1
                )
                
    @pytest.mark.parametrize("error_query,expected_error", [
        ("SELECT * FROM nonexistent", "Relation 'nonexistent' does not exist"),
        ("INSERT INTO test VALUES (NULL)", "NULL value not allowed"),
        ("INVALID SQL", "Syntax error"),
    ])
    async def test_query_error_handling(self, db, error_query, expected_error):
        """Test handling of various database errors."""
        # Setup mock connection
        mock_conn = Mock()
        mock_conn.fetch.side_effect = Exception(expected_error)
        db.pool.acquire.return_value = mock_conn
        
        # Test
        with pytest.raises(DatabaseError, match=expected_error):
            async with db.get_connection() as conn:
                await db.execute_query(conn, error_query) 