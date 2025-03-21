# Redeeye Module Documentation

## Overview

The Redeeye module manages late-night activity monitoring and coordination for Discord communities.

## Features

### Activity Monitoring
- Late-night presence
- Activity patterns
- Voice channel usage
- Gaming sessions

### Time Management
- Timezone tracking
- Sleep schedules
- Activity limits
- Break reminders

### Notifications
- Activity alerts
- Health reminders
- Schedule updates
- Group coordination

## Commands

### Status Commands

```
/redeeye status
Description: Check current late-night status
Options: None
Permissions: None
```

```
/redeeye active
Description: List active late-night users
Options: None
Permissions: None
```

### Time Commands

```
/redeeye timezone [timezone]
Description: Set or view timezone
Options:
- timezone: Your timezone (optional)
Permissions: None
```

```
/redeeye schedule [schedule]
Description: Set or view sleep schedule
Options:
- schedule: Sleep schedule (optional)
Permissions: None
```

### Group Commands

```
/redeeye group create <name>
Description: Create late-night group
Options:
- name: Group name
Permissions: None
```

```
/redeeye group join <name>
Description: Join late-night group
Options:
- name: Group name
Permissions: None
```

## Configuration

### Environment Variables

```env
# Redeeye Module Settings
REDEEYE_ENABLED=True
REDEEYE_START_HOUR=22
REDEEYE_END_HOUR=6
REDEEYE_NOTIFICATION_CHANNEL=channel_id
REDEEYE_REMINDER_INTERVAL=3600
REDEEYE_DEFAULT_TIMEZONE=UTC
```

### Module Settings

```python
REDEEYE_SETTINGS = {
    'start_hour': 22,       # Night start (24h)
    'end_hour': 6,         # Night end (24h)
    'reminder_interval': 60, # Minutes between reminders
    'health_checks': True,  # Enable health reminders
    'group_enabled': True,  # Enable group features
    'track_activity': True, # Track activity patterns
}
```

## Events

### Monitored Events
- `on_presence_update`: Activity changes
- `on_voice_state_update`: Voice activity
- `on_message`: Chat activity
- `on_member_update`: Status changes

### Event Handlers

```python
async def on_presence_update(before, after):
    """Handle presence updates."""
    if is_late_night():
        await track_night_activity(before, after)

async def on_voice_state_update(member, before, after):
    """Handle voice activity."""
    await process_voice_activity(member, before, after)
```

## Utilities

### Time Management

```python
def is_late_night(timezone=None):
    """Check if current time is late night."""
    current_time = get_current_time(timezone)
    return is_night_hours(current_time)

def get_user_timezone(member):
    """Get user's timezone."""
    return get_member_settings(member).get('timezone', 'UTC')
```

### Activity Tracking

```python
async def track_activity(member, activity_type):
    """Track member activity."""
    await log_activity(member, activity_type)
    await check_health_alerts(member)
```

## Database Schema

### Activity Table
```sql
CREATE TABLE night_activity (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    activity_type TEXT,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    end_time DATETIME,
    duration INTEGER
);
```

### Schedule Table
```sql
CREATE TABLE sleep_schedule (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    timezone TEXT DEFAULT 'UTC',
    sleep_start TIME,
    sleep_end TIME,
    active BOOLEAN DEFAULT TRUE
);
```

## API Reference

### RedeyeModule Class

```python
class RedeyeModule:
    """Main redeeye module class."""
    
    def __init__(self, bot):
        self.bot = bot
        self.settings = RedeyeSettings()
        self.db = RedeyeDatabase()
    
    async def track_night_activity(self, member):
        """Track late-night activity."""
        pass
    
    async def get_active_users(self):
        """Get currently active users."""
        pass
    
    async def process_health_check(self, member):
        """Process health check for member."""
        pass
```

### RedeyeSettings Class

```python
class RedeyeSettings:
    """Redeeye module settings."""
    
    def __init__(self):
        self.load_settings()
    
    def get_night_hours(self):
        """Get night hour range."""
        pass
    
    def get_reminder_interval(self):
        """Get reminder interval."""
        pass
```

## Error Handling

### Custom Exceptions

```python
class RedeyeError(Exception):
    """Base redeeye module error."""
    pass

class TimezoneError(RedeyeError):
    """Timezone-related errors."""
    pass

class ScheduleError(RedeyeError):
    """Schedule-related errors."""
    pass
```

### Error Processing

```python
try:
    await redeeye.track_night_activity(member)
except TimezoneError:
    await handle_timezone_error()
except RedeyeError as e:
    await handle_redeeye_error(e)
```

## Best Practices

1. **Health Focus**
   - Regular breaks
   - Sleep reminders
   - Activity limits
   - Wellness tips

2. **Time Management**
   - Timezone respect
   - Schedule flexibility
   - Break tracking
   - Pattern analysis

3. **Group Coordination**
   - Activity syncing
   - Group formation
   - Communication
   - Shared goals

4. **Privacy**
   - Data protection
   - User consent
   - Limited tracking
   - Clear policies

## Notes

- Health priority
- User wellbeing
- Regular updates
- Pattern monitoring
- Group support
- Documentation maintenance 