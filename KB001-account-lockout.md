# KB001 — Resolving Active Directory Account Lockouts

**Category:** Account / Active Directory
**Priority:** Critical (user cannot work until resolved)
**Last updated:** July 2026

## Symptom
User reports they cannot log into their workstation. Windows displays:
"Your account has been locked out. Please contact your administrator."

## Likely Causes
- Too many failed password attempts (mistyped password, cached old
  password on a phone/tablet still trying to authenticate)
- Password recently changed but not updated on a mobile device or
  mapped drive, causing repeated automatic failed attempts

## Resolution Steps
1. Verify the user's identity before making any account changes
   (confirm employee ID or have them verify via a known-good channel —
   never unlock or reset based on an unverified request).
2. Open **Active Directory Users and Computers** (ADUC).
3. Locate the user's account under the appropriate OU.
4. Right-click the account → **Unlock Account**.
5. If the lockout is recurring, check **Account lockout status** and
   review the security event log (Event ID 4740) on the domain
   controller to identify the source device causing repeated failures.
6. Common recurring cause: a personal phone or tablet with an old
   cached password still attempting to sync email. Have the user
   remove and re-add the account on that device with the current
   password.
7. If the user also forgot their password, reset it and set **User
   must change password at next logon**.
8. Confirm the user can log in successfully before closing the ticket.

## Prevention
- Encourage users to update saved passwords on all devices
  immediately after a password change.
- Consider enabling self-service password reset if not already in use,
  to reduce ticket volume for this issue.
