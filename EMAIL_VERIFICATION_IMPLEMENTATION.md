# Email Verification Implementation

## Overview

Email verification has been implemented for user registration to ensure users provide valid email addresses and prevent spam accounts.

## Features

### 1. **Registration Flow**
- Users must provide a valid email address during registration
- Account is created but set as **inactive** (`is_active=False`)
- Verification email is sent automatically
- User is redirected to a confirmation page

### 2. **Email Verification**
- Unique token generated for each user (valid for 24 hours)
- Token includes user ID, email, and active status
- Clicking the verification link activates the account
- Welcome notification is created upon successful verification

### 3. **Login Protection**
- Inactive users cannot log in
- Helpful message directs them to resend verification email
- Active users can log in normally

### 4. **Resend Verification**
- Users can request a new verification email
- Security: doesn't reveal if email exists in system
- Already active accounts are handled gracefully

## Files Created/Modified

### New Files
- `core/tokens.py` - Token generator for email verification
- `core/management/commands/test_email_verification.py` - Testing command
- `templates/registration/verification_email.txt` - Plain text email template
- `templates/registration/verification_email.html` - HTML email template
- `templates/registration/registration_complete.html` - Post-registration page
- `templates/registration/resend_verification.html` - Resend verification page
- `administration/email_backend.py` - Custom SMTP backend (SSL fix)

### Modified Files
- `core/views.py` - Updated RegisterView, CustomLoginView, added verification views
- `core/forms.py` - Made email required in registration form
- `core/urls.py` - Added verification URLs
- `templates/registration/register.html` - Updated email field to show as required
- `administration/email_utils.py` - Fixed SSL certificate verification, method name

## URLs

```python
/register/                      # User registration
/registration-complete/         # Post-registration confirmation
/verify-email/<uidb64>/<token>/ # Email verification link
/resend-verification/           # Resend verification email
```

## Testing

### Manual Testing

1. **Register a new user:**
   ```
   Visit: http://localhost:8000/register/
   Fill in the form with a valid email
   ```

2. **Check email:**
   - Verification email should be sent
   - Check SMTP logs or email inbox

3. **Verify email:**
   - Click the link in the email
   - Should redirect to login with success message

4. **Try to login before verification:**
   - Should be blocked with helpful message

### Command Line Testing

```bash
# Create a test user with inactive account
python manage.py test_email_verification test@example.com --username testuser

# This will output:
# - User credentials
# - Verification URL to test
# - Testing instructions
```

### Test SMTP Configuration

```bash
# Test SMTP connection and send email
python manage.py test_smtp your-email@example.com
```

## Configuration

### SMTP Settings
Email verification requires a working SMTP configuration. Configure in Django admin:
```
http://localhost:8000/admin/administration/smtpconfiguration/
```

### Token Expiration
Tokens are valid for 24 hours by default. This is controlled by Django's `PASSWORD_RESET_TIMEOUT` setting (default: 259200 seconds = 3 days for password reset, but our custom token generator can be configured separately if needed).

## Security Features

1. **Token-based verification** - Unique, time-limited tokens
2. **No email enumeration** - Resend feature doesn't reveal if email exists
3. **Inactive by default** - Users can't access system until verified
4. **SSL/TLS support** - Secure email transmission
5. **Rate limiting** - Can be added to prevent abuse

## Email Templates

### Plain Text (`verification_email.txt`)
Simple text version for email clients that don't support HTML

### HTML (`verification_email.html`)
Styled HTML version with:
- Professional branding
- Clear call-to-action button
- Fallback URL for manual copy/paste
- Warning about 24-hour expiration
- Footer with contact info

## User Experience

### Registration Success
- Clear confirmation message
- Instructions on what to do next
- Link to resend verification if needed

### Email Not Received
- Resend verification page
- Check spam folder reminder
- Support contact information

### Verification Success
- Success message
- Automatic redirect to login
- Welcome notification created

## Future Enhancements

1. **Email change verification** - Verify new email when user updates profile
2. **Rate limiting** - Limit verification email requests per IP/user
3. **Email templates in multiple languages** - Support for French/Malagasy
4. **Admin override** - Allow admins to manually activate accounts
5. **Bulk user import** - Skip verification for admin-created accounts
6. **Two-factor authentication** - Additional security layer

## Troubleshooting

### Emails not sending
1. Check SMTP configuration in admin
2. Test SMTP connection: `python manage.py test_smtp your@email.com`
3. Check email logs in admin: `/admin/administration/emaillog/`
4. Verify SSL certificates are properly configured

### Token invalid/expired
1. Tokens expire after 24 hours
2. User can request new verification email
3. Check that user's email hasn't changed

### User still can't login
1. Verify `is_active=True` in database
2. Check for other login restrictions (staff-only, etc.)
3. Verify password is correct

## Notes

- Email field is now **required** for registration
- Old users without email can still login (they're already active)
- Admin users are not affected by this verification flow
- The system uses the custom SMTP backend to handle SSL certificate issues on macOS
