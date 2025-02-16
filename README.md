# Database User Management Automation

This repository provides an example of how to automate the creation and deletion of database users in AWS-hosted databases using GitHub Actions. The workflow connects to multiple databases, executes SQL commands, and manages users efficiently.

# Features

 - Automates the creation and deletion of users in AWS databases.

 - Supports MySQL and PostgreSQL.

 - Uses GitHub Actions to execute scripts on demand.

 - Secure authentication via GitHub Secrets. (Can be changed with OIDC)

 - YAML-based user configuration.

# How It Works

 - Define users in a users.yaml file.

 - Run the GitHub Actions workflow to apply changes.

 - The workflow connects to multiple databases and executes SQL commands.

 - Users are created or deleted automatically based on the configuration.