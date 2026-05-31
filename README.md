# grasp_bunny

## Database settings

Python scripts read MySQL connection settings from environment variables.

PowerShell example:

```powershell
$env:GRASP_BUNNY_DB_HOST = "localhost"
$env:GRASP_BUNNY_DB_USER = "root"
$env:GRASP_BUNNY_DB_PASSWORD = "your_password"
$env:GRASP_BUNNY_DB_NAME = "grasp_bunny"
```

Unset values default to `localhost`, `root`, an empty password, and `grasp_bunny`.
