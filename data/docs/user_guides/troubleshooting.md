# Troubleshooting Guide

This guide helps you diagnose and resolve common issues with the Discord bot framework.

## Quick Diagnosis

### Bot Not Responding

1. **Check Bot Status**
   ```bash
   # View bot process
   ps aux | grep discord_bot.py
   
   # Check logs
   tail -f discord_bot.log
   ```

2. **Verify Token**
   - Check `.env` file for valid token
   - Ensure token has required permissions
   - Try regenerating token in Discord Developer Portal

3. **Check Connectivity**
   - Verify internet connection
   - Check Discord API status
   - Confirm firewall settings

### Command Issues

1. **Slash Commands Not Working**
   ```
   Common causes:
   - Commands not synced
   - Bot lacks permissions
   - Rate limits exceeded
   ```

2. **Permission Errors**
   - Verify bot role hierarchy
   - Check command permissions
   - Review role configurations

3. **Command Not Found**
   - Ensure command is registered
   - Check module is enabled
   - Verify command syntax

## Module-Specific Issues

### Mod Module

1. **Mute Command Fails**
   - Check role hierarchy
   - Verify mute role exists
   - Confirm bot permissions

2. **Kick/Ban Not Working**
   - Verify bot permissions
   - Check target user's role
   - Review server audit log

3. **Message Clear Issues**
   - Check message age
   - Verify channel permissions
   - Review rate limits

### Online Module

1. **Status Not Updating**
   - Check update interval
   - Verify user presence intent
   - Review rate limits

2. **Notifications Not Sending**
   - Check channel permissions
   - Verify role mentions
   - Review webhook status

3. **Tracking Issues**
   - Verify user visibility
   - Check privacy settings
   - Review tracking limits

### Instore Module

1. **Link Detection Issues**
   - Check regex patterns
   - Verify link format
   - Review channel settings

2. **Forward System Problems**
   - Check reaction permissions
   - Verify channel access
   - Review message content

3. **Product ID Extraction**
   - Verify URL format
   - Check regex patterns
   - Review store compatibility

## Common Error Messages

### Discord API Errors

1. **Rate Limit Exceeded**
   ```
   Error: 429 Too Many Requests
   Solution:
   - Implement request throttling
   - Add cooldown periods
   - Review API usage
   ```

2. **Invalid Token**
   ```
   Error: Improper token provided
   Solution:
   - Check token format
   - Regenerate token
   - Update .env file
   ```

3. **Missing Permissions**
   ```
   Error: Missing Permissions
   Solution:
   - Review required permissions
   - Check role hierarchy
   - Update bot invite link
   ```

### Bot Framework Errors

1. **Module Load Failure**
   ```
   Error: Failed to load module
   Solution:
   - Check module dependencies
   - Verify configuration
   - Review module code
   ```

2. **Configuration Error**
   ```
   Error: Invalid configuration
   Solution:
   - Check .env format
   - Verify required values
   - Review settings
   ```

3. **Database Connection**
   ```
   Error: Database connection failed
   Solution:
   - Check credentials
   - Verify database status
   - Review connection string
   ```

## Performance Issues

### High Resource Usage

1. **CPU Usage**
   - Monitor process stats
   - Check background tasks
   - Review event handlers

2. **Memory Leaks**
   - Monitor memory usage
   - Check resource cleanup
   - Review long-running tasks

3. **Network Issues**
   - Monitor connection status
   - Check API call frequency
   - Review websocket status

## Debugging Tools

### Log Analysis

1. **View Logs**
   ```bash
   # View recent logs
   tail -f discord_bot.log
   
   # Search for errors
   grep ERROR discord_bot.log
   
   # Check specific module
   grep "module_name" discord_bot.log
   ```

2. **Debug Mode**
   ```env
   # Enable debug logging
   DEBUG_LOGGING=True
   LOG_LEVEL=DEBUG
   ```

3. **Performance Monitoring**
   ```bash
   # Monitor resource usage
   top -p $(pgrep -f discord_bot.py)
   ```

## Recovery Procedures

### Bot Recovery

1. **Safe Restart**
   ```bash
   # Stop bot gracefully
   kill -SIGTERM $(pgrep -f discord_bot.py)
   
   # Start bot
   python discord_bot.py
   ```

2. **Configuration Reset**
   - Backup current config
   - Reset to defaults
   - Gradually restore settings

3. **Module Recovery**
   - Disable problematic module
   - Clear module cache
   - Reload module

### Data Recovery

1. **Configuration Backup**
   - Keep .env backups
   - Version control settings
   - Document changes

2. **Database Backup**
   - Regular backups
   - Point-in-time recovery
   - Data validation

3. **Log Recovery**
   - Archive old logs
   - Compress logs
   - Maintain audit trail

## Prevention

### Best Practices

1. **Regular Maintenance**
   - Update dependencies
   - Clean old data
   - Monitor performance

2. **Configuration Management**
   - Version control
   - Change documentation
   - Regular backups

3. **Monitoring**
   - Set up alerts
   - Monitor metrics
   - Review logs

## Getting Help

### Support Resources

1. **Documentation**
   - Review guides
   - Check examples
   - Search issues

2. **Community Support**
   - Join Discord server
   - Check forums
   - Search discussions

3. **Professional Support**
   - Open GitHub issue
   - Contact maintainers
   - Consider consulting

## Next Steps

1. Implement monitoring
2. Set up automated backups
3. Review security practices
4. Join support community
