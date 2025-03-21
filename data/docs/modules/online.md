# Online Module Documentation

## Overview

The Online module manages user presence tracking and activity monitoring in Discord servers.

## Features

### Presence Tracking
- Online status monitoring
- Activity status tracking
- Game presence detection
- Custom status tracking

### Activity Analytics
- User activity patterns
- Peak activity times
- Game popularity stats
- Voice channel usage

### Notifications
- Status change alerts
- Game session notifications
- Voice channel updates
- Custom status alerts

## Commands

### Status Commands

```
/online status <user>
Description: Check user's current online status
Options:
- user: User to check
Permissions: None
```

```
/online activity <user>
Description: View user's current activity
Options:
- user: User to check
Permissions: None
```

### Analytics Commands

```
/online stats [user]
Description: View activity statistics
Options:
- user: User to check (optional)
Permissions: None
```

```
/online peak [timeframe]
Description: View peak activity times
Options:
- timeframe: Time period (day/week/month)
Permissions: None
```

### Notification Commands

```
/online notify add <user> <status>
Description: Add status notification
Options:
- user: User to monitor
- status: Status to track
Permissions: None
```

```
/online notify list
Description: List active notifications
Options: None
Permissions: None
```

## Configuration

### Environment Variables

```env
# Online Module Settings
ONLINE_ENABLED=True
ONLINE_TRACK_GAMES=True
ONLINE_TRACK_VOICE=True
ONLINE_TRACK_STATUS=True
ONLINE_NOTIFICATION_CHANNEL=channel_id
ONLINE_UPDATE_INTERVAL=60
ONLINE_STORE_DAYS=30
```

### Module Settings

```python
ONLINE_SETTINGS = {
    'track_games': True,     # Track game activity
    'track_voice': True,     # Track voice activity
    'track_status': True,    # Track custom status
    'update_interval': 60,   # Update interval (seconds)
    'store_days': 30,       # Data retention period
    'notify_enabled': True,  # Enable notifications
}
```

## Events

### Monitored Events
- `on_presence_update`: Status changes
- `on_voice_state_update`: Voice activity
- `on_member_update`: Member updates
- `on_activity_update`: Activity changes

### Event Handlers

```python
async def on_presence_update(before, after):
    """Handle presence updates."""
    if has_status_changed(before, after):
        await process_status_change(before, after)

async def on_voice_state_update(member, before, after):
    """Handle voice state updates."""
    await track_voice_activity(member, before, after)
```

## Utilities

### Status Checking

```python
def get_user_status(member):
    """Get user's current status."""
    return {
        'status': member.status,
        'activity': member.activity,
        'voice': member.voice
    }

def is_playing_game(member):
    """Check if user is playing a game."""
    return member.activity and member.activity.type == ActivityType.playing
```

### Analytics Processing

```python
async def calculate_peak_times(timeframe):
    """Calculate peak activity times."""
    data = await fetch_activity_data(timeframe)
    return analyze_peak_times(data)
```

## Database Schema

### Activity Table
```sql
CREATE TABLE activity_log (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    status TEXT,
    activity_type TEXT,
    activity_name TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### Notifications Table
```sql
CREATE TABLE notifications (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    target_id TEXT NOT NULL,
    status TEXT,
    active BOOLEAN DEFAULT TRUE
);
```

## API Reference

### OnlineModule Class

```python
class OnlineModule:
    """Main online module class."""
    
    def __init__(self, bot):
        self.bot = bot
        self.settings = OnlineSettings()
        self.db = OnlineDatabase()
    
    async def track_presence(self, member):
        """Track member presence."""
        pass
    
    async def get_activity_stats(self, user, timeframe):
        """Get activity statistics."""
        pass
    
    async def add_notification(self, user, target, status):
        """Add status notification."""
        pass
```

### OnlineSettings Class

```python
class OnlineSettings:
    """Online module settings."""
    
    def __init__(self):
        self.load_settings()
    
    def get_update_interval(self):
        """Get status update interval."""
        pass
    
    def get_notification_channel(self):
        """Get notification channel ID."""
        pass
```

## Error Handling

### Custom Exceptions

```python
class OnlineError(Exception):
    """Base online module error."""
    pass

class TrackingError(OnlineError):
    """Tracking-related errors."""
    pass

class NotificationError(OnlineError):
    """Notification-related errors."""
    pass
```

### Error Processing

```python
try:
    await online.track_presence(member)
except TrackingError:
    await handle_tracking_error()
except OnlineError as e:
    await handle_online_error(e)
```

## Best Practices

1. **Data Collection**
   - Respect privacy
   - Minimize storage
   - Regular cleanup
   - Data anonymization

2. **Performance**
   - Optimize updates
   - Cache results
   - Batch processing
   - Rate limiting

3. **Notifications**
   - Avoid spam
   - User preferences
   - Clear messaging
   - Easy management

4. **Analytics**
   - Accurate tracking
   - Useful metrics
   - Clear reporting
   - Data validation

## Notes

- Regular maintenance
- Privacy compliance
- Performance monitoring
- Data backup
- User feedback
- Documentation updates 