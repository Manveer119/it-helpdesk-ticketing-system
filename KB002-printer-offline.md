# KB002 — Troubleshooting a Printer Showing "Offline"

**Category:** Printer
**Priority:** Medium
**Last updated:** July 2026

## Symptom
A shared network printer shows an "Offline" status in Windows on some
or all workstations, and print jobs will not go through.

## Likely Causes
- Printer lost its DHCP-assigned IP address (most common cause for
  printers not using a static/reserved IP)
- Printer is powered off, in sleep mode, or has a paper jam/error
  state halting the print spooler
- Print spooler service on the print server has stalled

## Resolution Steps
1. Physically check the printer: confirm it's powered on, has no
   error lights, and is connected to the network (check for a link
   light on the network port).
2. On the printer's control panel, check the network settings menu
   for its current IP address.
3. Compare that IP to the IP configured on the print server /
   workstation printer port. If they don't match, the printer's lease
   likely renewed with a new address.
4. **Preferred fix:** assign the printer a DHCP reservation or static
   IP in the network configuration so this doesn't recur, then update
   the printer port on the print server to match.
5. If the IP matches but it's still offline, restart the **Print
   Spooler** service on the print server:
   - `services.msc` → Print Spooler → Restart
6. Send a test print from the print server to confirm it clears.
7. If only one workstation shows offline (others are fine), the issue
   is local — remove and re-add the printer on that machine.

## Prevention
- Maintain a list of all network printers with reserved/static IPs to
  avoid this being a recurring ticket category (this was one of the
  top 3 most common ticket types in the sample data for this project
  — see reports/volume_by_category.png).
