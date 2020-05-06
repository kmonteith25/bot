# Senior Design and Development - Discord Bot
Manual Testing for Final Project

## Issue: Unit Tests for Pagination #616
#### Features
- This function allows pagination of lengthy text outputs in Discord
#### Fields
- Test case id: #616
- Unit to test: Paginator buttons
- Assumptions: Discord Bot is up and running
- Test data: None
- Steps to be executed:
  - Use !help command in discord
  - Use all 4 pagination buttons
- Expected Result: Paginator buttons work
- Actual result: Paginator buttons work
- Pass/Fail: Pass
- Comments: None

## Issue: Unit Tests for Antimalware Cog #889
#### Features
- This feature prevents text files and possible malware being uploaded by unprivileged users
#### Fields
- Test case id: #889
- Unit to test: Antimalware Cog
- Assumptions: Discord Bot is up and running
- Test data: Multiple different text file types
- Steps to be executed:
  - Upload one text file without permissions.
  - Verify antimalware cog is working and repeat
- Expected Result: Discord Bot will prevent user from uploading files
- Actual result: Discord Bot prevented user from uploading files
- Pass/Fail: Pass
- Comments: Possible file types could be put through, but implementation of a whitelist for file types can prevent this.
