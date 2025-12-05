# Cash Payment System - Management Commands Guide

This document provides a comprehensive guide to the management commands available for the cash payment system.

## Overview

Four management commands have been implemented to automate key operational tasks:

1. **close_expired_sessions** - Auto-close sessions after timeout
2. **generate_commission_report** - Generate monthly commission reports
3. **verify_audit_trail** - Verify hash chain integrity
4. **reconciliation_reminder** - Send daily reconciliation reminders

---

## 1. Close Expired Sessions

**Command:** `python manage.py close_expired_sessions`

**Purpose:** Automatically close cash sessions that have exceeded the configured timeout period.

### Usage

```bash
# Dry run - see what would be closed without actually closing
python manage.py close_expired_sessions --dry-run

# Close expired sessions
python manage.py close_expired_sessions

# Force close even if there are transactions
python manage.py close_expired_sessions --force
```

### Options

- `--dry-run` - Show which sessions would be closed without actually closing them
- `--force` - Force close sessions even if they have transactions

### What it does

1. Queries for open sessions older than the configured timeout (default: 12 hours)
2. Calculates expected balance for each session
3. Closes the session with auto-generated notes
4. Sends notification to the agent partenaire
5. Logs all actions in the audit trail

### Recommended Schedule

Run this command every hour via cron:

```bash
0 * * * * cd /path/to/project && python manage.py close_expired_sessions
```

---

## 2. Generate Commission Report

**Command:** `python manage.py generate_commission_report`

**Purpose:** Generate monthly commission reports for agent partenaires and email them to administrators.

### Usage

```bash
# Generate report for previous month (default)
python manage.py generate_commission_report

# Generate report for specific month
python manage.py generate_commission_report --month 10 --year 2024

# Send to specific email address
python manage.py generate_commission_report --email admin@example.com

# Dry run - generate report without sending emails
python manage.py generate_commission_report --dry-run
```

### Options

- `--month MONTH` - Month (1-12). Defaults to previous month
- `--year YEAR` - Year (e.g., 2024). Defaults to current year
- `--email EMAIL` - Email address to send report to. If not provided, sends to all admin users
- `--dry-run` - Generate report without sending emails

### Report Contents

The report includes:

- **Overall Statistics**
  - Total transactions
  - Total tax collected
  - Total commissions

- **By Payment Status**
  - Pending commissions
  - Paid commissions
  - Cancelled commissions

- **By Agent Partenaire**
  - Transaction count
  - Tax collected
  - Commission earned
  - Pending vs. paid breakdown

### Recommended Schedule

Run this command on the 1st of each month via cron:

```bash
0 9 1 * * cd /path/to/project && python manage.py generate_commission_report
```

---

## 3. Verify Audit Trail

**Command:** `python manage.py verify_audit_trail`

**Purpose:** Verify the integrity of the cash audit trail hash chain and alert if tampering is detected.

### Usage

```bash
# Verify last 30 days (default)
python manage.py verify_audit_trail

# Verify specific date range
python manage.py verify_audit_trail --start-date 2024-10-01 --end-date 2024-10-31

# Verify entire audit trail
python manage.py verify_audit_trail --full

# Send alert email if tampering detected
python manage.py verify_audit_trail --alert-on-tampering

# Send alert to specific email
python manage.py verify_audit_trail --email security@example.com --alert-on-tampering
```

### Options

- `--start-date YYYY-MM-DD` - Start date for verification. Defaults to 30 days ago
- `--end-date YYYY-MM-DD` - End date for verification. Defaults to now
- `--full` - Verify entire audit trail (may take time for large datasets)
- `--email EMAIL` - Email address to send alert to if tampering detected
- `--alert-on-tampering` - Send email alert to all admins if tampering is detected

### What it verifies

1. **Hash Chain Integrity** - Verifies that each log entry's previous_hash matches the actual previous entry's current_hash
2. **Entry Integrity** - Recalculates each entry's hash and compares with stored hash

### Alert Content

If tampering is detected, the alert includes:

- Number of issues found
- Log entry IDs affected
- Timestamps of affected entries
- Type of integrity violation
- Hash mismatches

### Recommended Schedule

Run this command daily via cron:

```bash
0 2 * * * cd /path/to/project && python manage.py verify_audit_trail --alert-on-tampering
```

---

## 4. Reconciliation Reminder

**Command:** `python manage.py reconciliation_reminder`

**Purpose:** Send daily reminders for unreconciled cash sessions to agent partenaires and administrators.

### Usage

```bash
# Check last 1 day (default)
python manage.py reconciliation_reminder

# Check last 3 days
python manage.py reconciliation_reminder --days 3

# Dry run - see what would be sent without sending
python manage.py reconciliation_reminder --dry-run

# Also send summary to admins
python manage.py reconciliation_reminder --email-admins
```

### Options

- `--days DAYS` - Number of days to look back for unreconciled sessions (default: 1)
- `--dry-run` - Show what would be sent without actually sending notifications
- `--email-admins` - Also send summary email to admin staff

### What it does

1. Finds closed sessions that haven't been reconciled
2. Groups sessions by agent partenaire
3. Sends individual reminders to each agent
4. Optionally sends summary report to administrators

### Reminder Content

**To Agent Partenaires:**
- List of unreconciled sessions
- Session numbers and closing times
- Total expected balance
- Total discrepancies

**To Administrators:**
- Overall statistics
- Sessions grouped by agent
- Total unreconciled amount
- Action required

### Recommended Schedule

Run this command daily in the morning via cron:

```bash
0 8 * * * cd /path/to/project && python manage.py reconciliation_reminder --email-admins
```

---

## Cron Configuration Example

Add these lines to your crontab (`crontab -e`):

```bash
# Close expired sessions every hour
0 * * * * cd /path/to/project && /path/to/venv/bin/python manage.py close_expired_sessions >> /var/log/cash_sessions.log 2>&1

# Verify audit trail daily at 2 AM
0 2 * * * cd /path/to/project && /path/to/venv/bin/python manage.py verify_audit_trail --alert-on-tampering >> /var/log/audit_verification.log 2>&1

# Send reconciliation reminders daily at 8 AM
0 8 * * * cd /path/to/project && /path/to/venv/bin/python manage.py reconciliation_reminder --email-admins >> /var/log/reconciliation_reminders.log 2>&1

# Generate commission report on 1st of each month at 9 AM
0 9 1 * * cd /path/to/project && /path/to/venv/bin/python manage.py generate_commission_report >> /var/log/commission_reports.log 2>&1
```

---

## Logging

All commands log their activities to:

1. **Django logging system** - Check your configured log files
2. **Standard output** - Captured if running via cron with output redirection
3. **Audit trail** - For commands that modify data (close_expired_sessions)

---

## Troubleshooting

### Command not found

Make sure you're in the project directory and using the correct Python environment:

```bash
cd /path/to/project
source venv/bin/activate  # or your virtualenv path
python manage.py <command>
```

### Email not sending

1. Check SMTP configuration in the admin panel
2. Verify email addresses are configured for admin users
3. Check email logs in the database
4. Review Django logs for email errors

### No sessions/records found

This is normal if:
- No sessions have exceeded timeout (close_expired_sessions)
- No commissions in the specified period (generate_commission_report)
- No unreconciled sessions (reconciliation_reminder)
- Audit trail is intact (verify_audit_trail)

---

## Requirements Mapping

These commands fulfill the following requirements from the specification:

- **Requirement 7** - Session management and timeout
- **Requirement 6** - Commission tracking and reporting
- **Requirement 9** - Real-time transaction logging
- **Requirement 10** - Daily cash reconciliation
- **Requirement 11** - Cash collection reports
- **Requirement 12** - Tamper-proof transaction records

---

## Security Considerations

1. **Audit Trail Verification** - Run regularly to detect tampering
2. **Email Alerts** - Configure for critical security events
3. **Access Control** - Ensure cron jobs run with appropriate permissions
4. **Log Monitoring** - Review command logs regularly
5. **Backup** - Ensure audit logs are backed up before verification

---

## Support

For issues or questions about these commands:

1. Check the Django logs
2. Run commands with `--dry-run` first
3. Review the command help: `python manage.py <command> --help`
4. Contact the development team
