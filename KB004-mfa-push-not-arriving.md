# KB004 — MFA Push Notifications Not Arriving

**Category:** VPN / Remote Access, Account / Active Directory
**Priority:** High
**Last updated:** July 2026

## Symptom
User enters their password successfully but never receives the
multi-factor authentication (MFA) push notification on their phone,
blocking login to VPN, email, or other MFA-protected systems.

## Likely Causes
- Phone lost signal/data connectivity at the moment of the push
- MFA app needs an update or was reinstalled, breaking device
  registration
- User got a new phone and didn't re-register the authenticator app
- Notifications are being silenced/blocked at the OS level on the
  user's device

## Resolution Steps
1. Confirm the user's phone has an active internet connection
   (WiFi or cellular data) and notifications are not in Do Not
   Disturb mode.
2. Have the user check the MFA app directly (open it manually) rather
   than waiting for the push — sometimes the request is visible in-app
   even if the push notification itself didn't display.
3. If nothing appears in-app either, the device registration is
   likely broken. Re-register the user's MFA device in the
   authentication portal (verify identity first).
4. If the user recently got a new phone, this re-registration step is
   almost always the fix — walk them through scanning the new QR code
   during setup.
5. As a temporary fallback if the user is mid-shift and blocked, use a
   backup authentication method (SMS or backup codes) if your
   organization's MFA policy supports one, while the app-based method
   is being fixed.
6. Confirm successful login before closing the ticket.

## Prevention
- Add a step to the offboarding/device-replacement checklist reminding
  users to re-register MFA when they get a new phone, before their old
  device is wiped.
