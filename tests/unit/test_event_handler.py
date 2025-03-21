"""
Unit tests for event handling system.
"""
import pytest
from unittest.mock import Mock, patch
from core.event_handler import EventHandler, EventError, Event

@pytest.mark.unit
class TestEventHandler:
    """Test suite for event handling functionality."""
    
    @pytest.fixture
    def event_handler(self):
        """Fixture to provide an event handler instance."""
        return EventHandler()
        
    def test_event_registration(self, event_handler):
        """Test event listener registration."""
        # Setup
        async def test_listener(event):
            pass
            
        event_type = "test_event"
        
        # Test
        event_handler.register(event_type, test_listener)
        
        # Verify
        assert test_listener in event_handler.listeners[event_type]
        
    def test_duplicate_listener_registration(self, event_handler):
        """Test handling of duplicate listener registration."""
        # Setup
        async def test_listener(event):
            pass
            
        event_type = "test_event"
        
        # Register listener twice
        event_handler.register(event_type, test_listener)
        event_handler.register(event_type, test_listener)
        
        # Verify listener is only registered once
        assert len(event_handler.listeners[event_type]) == 1
        assert event_handler.listeners[event_type].count(test_listener) == 1
        
    def test_event_unregistration(self, event_handler):
        """Test event listener unregistration."""
        # Setup
        async def test_listener(event):
            pass
            
        event_type = "test_event"
        event_handler.register(event_type, test_listener)
        
        # Test
        event_handler.unregister(event_type, test_listener)
        
        # Verify
        assert test_listener not in event_handler.listeners[event_type]
        
    async def test_event_dispatch(self, event_handler):
        """Test event dispatching to listeners."""
        # Setup
        received_events = []
        
        async def test_listener(event):
            received_events.append(event)
            
        event_type = "test_event"
        event_data = {"key": "value"}
        event_handler.register(event_type, test_listener)
        
        # Test
        await event_handler.dispatch(Event(event_type, event_data))
        
        # Verify
        assert len(received_events) == 1
        assert received_events[0].type == event_type
        assert received_events[0].data == event_data
        
    async def test_multiple_listeners(self, event_handler):
        """Test event dispatching to multiple listeners."""
        # Setup
        listener_calls = []
        
        async def listener1(event):
            listener_calls.append("listener1")
            
        async def listener2(event):
            listener_calls.append("listener2")
            
        event_type = "test_event"
        event_handler.register(event_type, listener1)
        event_handler.register(event_type, listener2)
        
        # Test
        await event_handler.dispatch(Event(event_type, {}))
        
        # Verify all listeners were called
        assert len(listener_calls) == 2
        assert "listener1" in listener_calls
        assert "listener2" in listener_calls
        
    async def test_listener_error_handling(self, event_handler):
        """Test handling of listener errors."""
        # Setup
        async def error_listener(event):
            raise Exception("Listener error")
            
        event_type = "test_event"
        event_handler.register(event_type, error_listener)
        
        # Test
        with pytest.raises(EventError, match="Error in event listener"):
            await event_handler.dispatch(Event(event_type, {}))
            
    async def test_event_filtering(self, event_handler):
        """Test event filtering functionality."""
        # Setup
        received_events = []
        
        async def filtered_listener(event):
            if event.data.get("important"):
                received_events.append(event)
                
        event_type = "test_event"
        event_handler.register(event_type, filtered_listener)
        
        # Test with different events
        await event_handler.dispatch(Event(event_type, {"important": True}))
        await event_handler.dispatch(Event(event_type, {"important": False}))
        
        # Verify only important events were processed
        assert len(received_events) == 1
        assert received_events[0].data["important"] is True
        
    def test_listener_priority(self, event_handler):
        """Test listener priority ordering."""
        # Setup
        execution_order = []
        
        async def high_priority(event):
            execution_order.append("high")
            
        async def medium_priority(event):
            execution_order.append("medium")
            
        async def low_priority(event):
            execution_order.append("low")
            
        event_type = "test_event"
        
        # Register listeners with priorities
        event_handler.register(event_type, low_priority, priority=1)
        event_handler.register(event_type, high_priority, priority=3)
        event_handler.register(event_type, medium_priority, priority=2)
        
        # Test
        await event_handler.dispatch(Event(event_type, {}))
        
        # Verify execution order
        assert execution_order == ["high", "medium", "low"]
        
    async def test_async_event_processing(self, event_handler):
        """Test asynchronous event processing."""
        import asyncio
        
        # Setup
        processed = []
        
        async def slow_listener(event):
            await asyncio.sleep(0.1)
            processed.append("slow")
            
        async def fast_listener(event):
            processed.append("fast")
            
        event_type = "test_event"
        event_handler.register(event_type, slow_listener)
        event_handler.register(event_type, fast_listener)
        
        # Test
        await event_handler.dispatch(Event(event_type, {}))
        
        # Verify both listeners completed
        assert len(processed) == 2
        assert "slow" in processed
        assert "fast" in processed
        
    def test_event_validation(self, event_handler):
        """Test event validation."""
        # Test with invalid event type
        with pytest.raises(EventError, match="Invalid event type"):
            Event(None, {})
            
        # Test with invalid event data
        with pytest.raises(EventError, match="Event data must be a dictionary"):
            Event("test_event", "invalid_data") 