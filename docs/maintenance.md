# Music Mix Analyzer Maintenance

This document provides information about maintenance tasks and how to automate them.

## File Retention Policy

The application has a file retention policy that automatically deletes uploaded files after 30 days. This helps:

1. Conserve disk space
2. Improve application performance
3. Protect user privacy by not keeping data longer than necessary
4. Comply with data retention policies

## Manual Cleanup

To manually clean up files older than 30 days, use:

```bash
# From the project root directory
./manage.py maintenance --cleanup-uploads

# To specify a different retention period (e.g., 15 days)
./manage.py maintenance --cleanup-uploads --days=15

# To perform a dry run without actually deleting files
./manage.py maintenance --cleanup-uploads --dry-run
```

## Automated Cleanup with Cron

To set up automated cleanup, you can use a cron job:

### For Linux/Unix/macOS

1. Open the crontab editor:

```bash
crontab -e
```

2. Add the following line to run the cleanup task daily at midnight:

```
0 0 * * * cd /path/to/music/project && ./manage.py maintenance --cleanup-uploads >> logs/cleanup_cron.log 2>&1
```

Replace `/path/to/music/project` with the absolute path to your project directory.

### Using Docker

If you're using Docker, you can either:

1. Mount the host's cron to the container, or
2. Use the host's cron to execute the command inside the container:

```
0 0 * * * docker exec music-analyzer /app/manage.py maintenance --cleanup-uploads >> /path/to/logs/cleanup_cron.log 2>&1
```

## Environment-Specific Configuration

You may want different retention policies for different environments:

- Development: Short retention (7 days)
- Staging: Medium retention (14 days)
- Production: Standard retention (30 days)

To implement this, use different `--days` values in your cron jobs based on the environment.

## Monitoring

The cleanup process logs its activity to:

1. Standard output
2. `logs/uploads_cleanup_YYYYMMDD.log`

Review these logs periodically to ensure the cleanup process is working correctly.

## Troubleshooting

If the cleanup process fails:

1. Check log files for error messages
2. Verify that the user running the cron job has permission to delete files
3. Ensure there's enough disk space for the log files
4. Check if the script can access the application's configuration

For persistent issues, run the script manually with the `--dry-run` flag to diagnose problems. 