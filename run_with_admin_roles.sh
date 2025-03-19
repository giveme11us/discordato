#!/bin/bash

# Make sure settings directory exists
mkdir -p data/settings

# Create empty admin roles config file if it doesn't exist
if [ ! -f data/settings/admin_roles.json ]; then
    echo '{
        "ADMIN_ROLE_IDS": [],
        "ALLOW_SERVER_ADMINS": true
    }' > data/settings/admin_roles.json
    echo "Created initial admin roles config"
fi

# Run the bot
python discord_bot.py

# Print a message when the bot stops
echo "Bot stopped. Admin roles system is now in place."
echo "Use /admin-roles to configure which roles can use configuration commands." 