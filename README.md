# Discord Bot Project
Version: 2.0.0
Last Updated: 2024-03-20

## Overview
A modular Discord bot built with discord.py, featuring a robust command system, comprehensive error handling, and advanced logging capabilities.

## Features

### Core Systems
- **Command System**: Unified command registration and routing
- **Error Handling**: Centralized error management with custom exceptions
- **Logging**: Structured logging with rotation and module-specific loggers

### Modules
- **Mod**: Moderation tools and utilities
- **Online**: Online status tracking
- **Instore**: Store management features
- **Redeye**: Profile and task management

## Setup

### Prerequisites
- Python 3.8 or higher
- Discord Developer Account
- Bot Token and Application ID

### Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/discord-bot.git
cd discord-bot
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```env
# Required Configuration
DISCORD_TOKEN=your_bot_token
APPLICATION_ID=your_application_id

# Optional Configuration
GUILD_IDS=guild_id1,guild_id2
ENABLED_MODULES=mod,online,instore,redeye

# Logging Configuration
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE=logs/discord_bot.log
LOG_MAX_SIZE=5242880  # 5MB
LOG_BACKUP_COUNT=5
```

4. Run the bot:
```bash
python discord_bot.py
```

## Project Structure
```
discord_bot/
├── core/               # Core framework
│   ├── commands/      # Command system
│   ├── error_handler/ # Error handling
│   └── logging/       # Logging system
├── modules/           # Feature modules
├── data/             # Data storage
│   └── docs/         # Documentation
├── logs/             # Log files
├── tests/            # Test files
├── .env              # Configuration
└── README.md         # This file
```

## Documentation
- [Phase 2 Completion](data/docs/phase2_completion.md): Details about completed code quality improvements
- [Command System](data/docs/command_system.md): Guide to using the command system
- [Error Handling](data/docs/error_handling.md): Error handling documentation
- [Logging System](data/docs/logging.md): Logging system guide

## Development Status
- ✅ Phase 2: Code Quality Improvements
- 🔄 Phase 3: Testing Infrastructure (In Progress)
- 📅 Phase 4: Documentation (Planned)
- 📅 Phase 5: Security & Performance (Planned)
- 📅 Phase 6: Maintenance & Monitoring (Planned)

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Best Practices
- Follow the standardized command structure
- Use appropriate error handling
- Implement proper logging
- Write tests for new features

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments
- discord.py team for the excellent library
- Contributors and testers

## Contact
- GitHub Issues for bug reports and feature requests
- Project maintainers for other inquiries