# KB003 — VPN Client Fails to Connect (Remote User)

**Category:** VPN / Remote Access
**Priority:** Critical (remote user is fully blocked from working)
**Last updated:** July 2026

## Symptom
A remote user's VPN client fails to connect, times out, or
authenticates but immediately disconnects.

## Likely Causes
- Stored/cached credentials in the VPN client are stale after a
  password change
- Local network issue on the user's end (their home router/ISP)
- VPN client software is outdated or corrupted
- MFA push notification not being received (see KB004)

## Resolution Steps
1. Ask the user to confirm they have working internet access outside
   the VPN (can they browse normal websites?). This isolates whether
   it's a VPN-specific issue or a broader connectivity problem.
2. Have the user fully close the VPN client (check Task Manager, not
   just the window) and relaunch it.
3. Re-enter credentials manually rather than relying on a saved/cached
   login — this resolves the majority of cases where the user changed
   their password recently.
4. If it still fails, uninstall and reinstall the VPN client software,
   as a corrupted install is a common secondary cause.
5. Confirm the user is using the correct VPN gateway/profile if the
   organization has more than one (e.g., a specific gateway for a
   particular department or system).
6. If MFA is involved and the client authenticates but then fails,
   see **KB004 — MFA Push Notifications Not Arriving**.
7. Escalate to network team if the issue persists after the above and
   affects multiple users simultaneously (may indicate a gateway-side
   issue rather than a client-side one).

## Prevention
- Remind users to update their VPN client credentials immediately
  after any required password change, before their next remote
  session.
