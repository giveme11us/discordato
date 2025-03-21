# Core API Documentation

## Bot Manager

The Bot Manager is the central component of the Discord bot framework, responsible for managing bot instances, their lifecycle, and operational scenarios.

### Overview

The Bot Manager provides a flexible system for running one or multiple Discord bots with different configurations and module sets. It supports three operational scenarios:
- Single Bot: One bot instance running all modules
- Multi-Bot: Multiple bot instances, each running specific modules
- Partial: Similar to multi-bot but only for modules with available tokens

### Class: BotManager

#### Initialization
```python
manager = BotManager()
```

The BotManager constructor performs:
1. Core component initialization
2. Module discovery
3. Scenario determination
4. Bot instance initialization

#### Key Methods

##### start()
Start all initialized bot instances.
```python
success = manager.start()
```
- Returns: `bool` - True if all bots started successfully
- Raises:
  - `ConnectionError`: If Discord connection fails
  - `RuntimeError`: If bot startup fails

##### stop()
Stop all running bot instances and perform cleanup.
```python
success = manager.stop()
```
- Returns: `bool` - True if all bots stopped successfully

##### setup_bot(bot_name: str, token: str, modules: list)
Set up a new bot instance with specified configuration.
```python
bot = manager.setup_bot("main", "your-token", ["mod", "online"])
```
- Args:
  - `bot_name`: Unique identifier for the bot instance
  - `token`: Discord bot token for authentication
  - `modules`: List of module names to load
- Returns: `commands.Bot` - Configured bot instance
- Raises:
  - `ValueError`: If bot_name exists or token is invalid
  - `ModuleLoadError`: If module loading fails

##### start_bot(bot_name: str)
Start a specific bot instance by name.
```python
success = manager.start_bot("main")
```
- Args:
  - `bot_name`: Name of the bot instance to start
- Returns: `bool` - True if bot started successfully
- Raises:
  - `KeyError`: If bot_name doesn't exist
  - `ConnectionError`: If Discord connection fails

### Usage Example

```python
# Initialize the bot manager
manager = BotManager()

try:
    # Start all bots
    if manager.start():
        print("All bots started successfully")
    else:
        print("Some bots failed to start")
except Exception as e:
    print(f"Error starting bots: {e}")
finally:
    # Ensure proper cleanup
    manager.stop()
```

### Configuration

The Bot Manager relies on environment variables for configuration:
- `DISCORD_BOT_TOKEN`: Main bot token (required)
- `MODULE_NAME_TOKEN`: Additional tokens for multi-bot mode
- `ENABLED_MODULES`: Comma-separated list of enabled modules

### Best Practices

1. **Initialization**
   - Always initialize BotManager before any bot operations
   - Handle exceptions during initialization

2. **Resource Management**
   - Use try/finally to ensure proper cleanup
   - Call stop() before program termination

3. **Error Handling**
   - Handle connection errors gracefully
   - Implement proper logging
   - Monitor bot status

4. **Configuration**
   - Use environment variables for tokens
   - Keep tokens secure
   - Document module dependencies

### Notes

- The Bot Manager is designed to be the single point of control for all bot instances
- It handles command synchronization automatically in development mode
- Resource cleanup is automatic when stop() is called
- Module loading is dynamic based on configuration
