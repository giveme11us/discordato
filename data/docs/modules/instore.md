# Instore Module Documentation

## Overview

The Instore module manages in-store presence tracking and coordination for retail locations.

## Features

### Store Management
- Location tracking
- Store hours
- Staff scheduling
- Capacity monitoring

### Presence Tracking
- Check-in system
- Duration tracking
- Staff presence
- Customer counts

### Notifications
- Store updates
- Capacity alerts
- Schedule reminders
- Emergency broadcasts

## Commands

### Store Commands

```
/instore status
Description: Check store status
Options: None
Permissions: None
```

```
/instore hours
Description: View store hours
Options: None
Permissions: None
```

### Check-in Commands

```
/instore checkin
Description: Check in at store
Options: None
Permissions: None
```

```
/instore checkout
Description: Check out from store
Options: None
Permissions: None
```

### Staff Commands

```
/instore staff list
Description: List staff presence
Options: None
Permissions: MANAGE_ROLES
```

```
/instore schedule [date]
Description: View staff schedule
Options:
- date: Date to check (optional)
Permissions: None
```

## Configuration

### Environment Variables

```env
# Instore Module Settings
INSTORE_ENABLED=True
INSTORE_LOCATION=store_id
INSTORE_CAPACITY=50
INSTORE_STAFF_ROLE=role_id
INSTORE_NOTIFICATION_CHANNEL=channel_id
INSTORE_UPDATE_INTERVAL=300
INSTORE_TIMEZONE=UTC
```

### Module Settings

```python
INSTORE_SETTINGS = {
    'store_capacity': 50,    # Maximum store capacity
    'staff_minimum': 2,      # Minimum staff required
    'hours_format': '24h',   # Time format
    'checkin_timeout': 480,  # Auto-checkout (minutes)
    'notify_enabled': True,  # Enable notifications
    'track_customers': True, # Track customer count
}
```

## Events

### Monitored Events
- `on_member_join`: New arrivals
- `on_member_remove`: Departures
- `on_role_update`: Staff changes
- `on_presence_update`: Status changes

### Event Handlers

```python
async def on_member_join(member):
    """Handle new arrivals."""
    if is_customer(member):
        await process_arrival(member)

async def on_role_update(before, after):
    """Handle staff role changes."""
    await update_staff_status(before, after)
```

## Utilities

### Store Management

```python
def check_store_capacity():
    """Check current store capacity."""
    return {
        'current': get_current_count(),
        'maximum': get_max_capacity(),
        'available': get_available_space()
    }

def is_store_open():
    """Check if store is open."""
    return check_hours() and has_minimum_staff()
```

### Presence Tracking

```python
async def track_presence(member):
    """Track member presence."""
    await update_presence_log(member)
    await check_capacity_alerts()
```

## Database Schema

### Presence Table
```sql
CREATE TABLE presence_log (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    checkin_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    checkout_time DATETIME,
    duration INTEGER,
    is_staff BOOLEAN DEFAULT FALSE
);
```

### Schedule Table
```sql
CREATE TABLE schedule (
    id INTEGER PRIMARY KEY,
    user_id TEXT NOT NULL,
    role_id TEXT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status TEXT DEFAULT 'scheduled'
);
```

## API Reference

### InstoreModule Class

```python
class InstoreModule:
    """Main instore module class."""
    
    def __init__(self, bot):
        self.bot = bot
        self.settings = InstoreSettings()
        self.db = InstoreDatabase()
    
    async def process_checkin(self, member):
        """Process member check-in."""
        pass
    
    async def process_checkout(self, member):
        """Process member check-out."""
        pass
    
    async def get_store_status(self):
        """Get current store status."""
        pass
```

### InstoreSettings Class

```python
class InstoreSettings:
    """Instore module settings."""
    
    def __init__(self):
        self.load_settings()
    
    def get_store_capacity(self):
        """Get store capacity."""
        pass
    
    def get_staff_roles(self):
        """Get staff role IDs."""
        pass
```

## Error Handling

### Custom Exceptions

```python
class InstoreError(Exception):
    """Base instore module error."""
    pass

class CapacityError(InstoreError):
    """Capacity-related errors."""
    pass

class ScheduleError(InstoreError):
    """Schedule-related errors."""
    pass
```

### Error Processing

```python
try:
    await instore.process_checkin(member)
except CapacityError:
    await handle_capacity_error()
except InstoreError as e:
    await handle_instore_error(e)
```

## Best Practices

1. **Capacity Management**
   - Regular monitoring
   - Automatic alerts
   - Staff notifications
   - Emergency procedures

2. **Staff Scheduling**
   - Coverage checks
   - Role verification
   - Schedule conflicts
   - Break management

3. **Data Accuracy**
   - Regular audits
   - Auto-checkout
   - Data validation
   - Error correction

4. **Communication**
   - Clear updates
   - Status visibility
   - Emergency alerts
   - Staff coordination

## Notes

- Regular audits
- System maintenance
- Staff training
- Emergency plans
- Data backup
- Documentation updates 