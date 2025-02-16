# Database User Management Automation

This repository provides an example of how to automate the creation and deletion of database users in AWS-hosted databases using GitHub Actions. The workflow connects to multiple databases, executes SQL commands, and manages users efficiently.

# Features

 - Automates the creation and deletion of users in AWS databases.

 - Supports PostgreSQL.

 - Uses GitHub Actions to execute scripts on demand.

 - Secure authentication via GitHub Secrets. (Can be changed with OIDC)

 - YAML-based user configuration.

# How It Works

 - Define users in a users.yaml file.

 - Run the GitHub Actions workflow to apply changes.

 - The workflow connects to multiple databases and executes SQL commands.

 - Users are created or deleted automatically based on the configuration.

 # This is how aws secrets should be:
 
**name of the secret: db-secrets-${enviroment} MEANS db-secrets-development, db-secrets-staging, db-secrets-production**

 ```json
  {
    "databases": [
    {
        "host": "example.host.aws.com",
        "username": "admin",
        "password": "secure_password_1"
    },
    {
        "host": "example-1.host.aws.com",
        "username": "admin-1",
        "password": "password-secure-2"
    }
    ]
  }
```

# This is how users.yaml should be:

**name if the secret: db-users-development, db-users-staging, db-users-production**

```json
{
    "user1": "password1",
    "user2": "password2",
    "user3": "password3"
}
```