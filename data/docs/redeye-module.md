# Redeye Module Documentation

This documentation covers the Redeye module functionality for viewing and managing profiles.

## Overview

The Redeye module provides functionality for interacting with the following CSV files:
- `profiles.csv` - Contains profile information for various configurations
- `tasks.csv` - Contains task information associated with profiles

These file paths are hardcoded in the environment configuration for security purposes.

## Commands

### `/redeye-profiles`

The `/redeye-profiles` command allows you to view the contents of the profiles.csv file in a formatted display.

**Usage:**
- `/redeye-profiles` - Lists all profiles with basic information
- `/redeye-profiles profile_name:NAME` - Shows detailed information for a specific profile

**Example Output:**

When viewing all profiles:
```
Redeye Profiles
Found X profiles in total.

1. ProfileName
Webhook: https://discordapp.com/api/webhooks/...
```

When viewing a specific profile:
```
Profile: ProfileName
Detailed profile information

Webhook
`https://discordapp.com/api/webhooks/...`

Personal Information
Name: John Doe
Phone: 1234567890
Address: 123 Main St
City: Anytown
Zip: 12345
State: CA
Country: US
Fiscal Code: 
```

### `/redeye-config`

The `/redeye-config` command allows you to view and update the file path configurations for the Redeye module.

**Usage:**
- `/redeye-config` - Shows current file path configuration
- `/redeye-config profiles_path:PATH` - Updates the path to the profiles CSV file
- `/redeye-config tasks_path:PATH` - Updates the path to the tasks CSV file
- `/redeye-config profiles_path:PATH tasks_path:PATH` - Updates both file paths

## Configuration

The Redeye module uses the following configuration settings:

### Environment Variables

```
# Redeye Module Settings
REDEYE_WHITELIST_ROLE_IDS=811975979492704337,969204849101119528

# Redeye Module File Paths (Hardcoded)
REDEYE_PROFILES_PATH=/Users/ivansposato/Documents/projects/easycopeu/discord/data/redeye/profiles.csv
REDEYE_TASKS_PATH=/Users/ivansposato/Documents/projects/easycopeu/discord/data/redeye/tasks.csv
```

### CSV File Format

#### profiles.csv

The profiles.csv file contains the following columns:
- `Name` - Profile name
- `Webhook` - Discord webhook URL
- `FirstName` - First name for shipping
- `LastName` - Last name for shipping
- `Phone` - Phone number
- `CountryId` - Country ID
- `Address` - Street address
- `ZipCode` - Postal code
- `City` - City
- `StateId` - State/Province ID
- `CodFisc` - Fiscal code

#### tasks.csv

The tasks.csv file contains the following columns:
- `ProfileName` - Name of the profile to use
- `Pid` - Product ID
- `Email` - Email address
- `Password` - Password

## Permissions

The Redeye module uses role-based permissions:
- Only users with roles specified in the `REDEYE_WHITELIST_ROLE_IDS` environment variable can use Redeye commands
- All command responses are ephemeral (only visible to the user who triggered the command)

## Error Handling

When a user without the required roles attempts to use Redeye module commands, they will receive a permission denied message listing all the roles required to use these commands. 