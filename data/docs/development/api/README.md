# API Documentation

## Core APIs

### BaseModule
The foundation class for all feature modules.

```python
class BaseModule:
    """Base class for bot modules."""
    
    def __init__(self, bot):
        """Initialize module.
        
        Args:
            bot: The Discord bot instance
        """
        self.bot = bot
        self.enabled = False
        
    async def setup(self):
        """Set up the module."""
        pass
        
    async def cleanup(self):
        """Clean up module resources."""
        pass
```

### BaseConfig
Base configuration class with validation support.

```python
class BaseConfig:
    """Base class for configuration."""
    
    def __init__(self):
        """Initialize configuration."""
        self._config = {
            "ENABLED": False
        }
        self._version = "1.0.0"
        
    @property
    def ENABLED(self) -> bool:
        """Whether the module is enabled."""
        return self._config["ENABLED"]
        
    @ENABLED.setter
    def ENABLED(self, value: bool):
        self._config["ENABLED"] = value
        
    def validate_config(self) -> bool:
        """Validate configuration.
        
        Returns:
            bool: True if valid
        """
        return isinstance(self.ENABLED, bool)
```

## Feature APIs

### Moderation

#### FilterConfig
Configuration for keyword filtering.

```python
class FilterConfig(BaseConfig):
    """Filter configuration."""
    
    @property
    def FILTERS(self) -> dict:
        """Active filters."""
        return self._config["FILTERS"]
        
    def add_filter(self, name: str, config: dict):
        """Add a new filter.
        
        Args:
            name: Filter name
            config: Filter configuration
        """
        self._config["FILTERS"][name] = config
```

### Reactions

#### ForwardConfig
Configuration for message forwarding.

```python
class ForwardConfig(BaseConfig):
    """Forward configuration."""
    
    @property
    def DESTINATION_CHANNEL_ID(self) -> Optional[int]:
        """Channel for forwarded messages."""
        return self._config["DESTINATION_CHANNEL_ID"]
        
    @property
    def FORWARD_EMOJI(self) -> str:
        """Emoji for forwarding."""
        return self._config["FORWARD_EMOJI"]
```

## Utility APIs

### Settings Manager
Manages persistent settings storage.

```python
class SettingsManager:
    """Manages persistent settings."""
    
    def load(self) -> dict:
        """Load settings from storage."""
        pass
        
    def save(self, settings: dict):
        """Save settings to storage."""
        pass
```

### Command Registry
Handles command registration and permissions.

```python
class CommandRegistry:
    """Manages command registration."""
    
    def register(self, command: Command):
        """Register a new command."""
        pass
        
    def unregister(self, command: Command):
        """Unregister a command."""
        pass
```

## Event System

### Event Types
Standard event types used in the bot.

```python
class EventType(Enum):
    """Standard event types."""
    MESSAGE = "message"
    REACTION = "reaction"
    COMMAND = "command"
    ERROR = "error"
```

### Event Handler
Base class for event handlers.

```python
class EventHandler:
    """Base event handler."""
    
    async def handle(self, event: Event):
        """Handle an event.
        
        Args:
            event: The event to handle
        """
        pass
```

## Database APIs

### DatabaseManager
Manages database connections and operations.

```python
class DatabaseManager:
    """Manages database operations."""
    
    async def connect(self):
        """Establish database connection."""
        pass
        
    async def disconnect(self):
        """Close database connection."""
        pass
        
    async def execute(self, query: str, *args):
        """Execute a database query."""
        pass
```

## Logging System

### LogManager
Manages logging configuration and output.

```python
class LogManager:
    """Manages logging system."""
    
    def setup(self, config: dict):
        """Set up logging system.
        
        Args:
            config: Logging configuration
        """
        pass
        
    def get_logger(self, name: str) -> Logger:
        """Get a logger instance."""
        pass
```

## Error Handling

### ErrorHandler
Base class for error handlers.

```python
class ErrorHandler:
    """Base error handler."""
    
    async def handle(self, error: Exception):
        """Handle an error.
        
        Args:
            error: The error to handle
        """
        pass
```

## Utility Functions

### Permission Checks
```python
def has_permission(user: User, permission: str) -> bool:
    """Check if user has permission."""
    pass
    
def require_permission(permission: str):
    """Decorator for permission requirements."""
    pass
```

### Validation
```python
def validate_channel_id(channel_id: int) -> bool:
    """Validate a channel ID."""
    pass
    
def validate_role_id(role_id: int) -> bool:
    """Validate a role ID."""
    pass
```

## Constants

### Permission Levels
```python
PERMISSION_LEVELS = {
    "EVERYONE": 0,
    "MODERATOR": 1,
    "ADMIN": 2
}
```

### Event Names
```python
EVENT_NAMES = {
    "MESSAGE_CREATE": "on_message",
    "REACTION_ADD": "on_reaction_add",
    "COMMAND_ERROR": "on_command_error"
}
```

## Type Definitions

### Custom Types
```python
from typing import TypeVar, Union

ChannelID = NewType("ChannelID", int)
RoleID = NewType("RoleID", int)
UserID = NewType("UserID", int)

ConfigValue = Union[str, int, bool, list, dict]
``` 