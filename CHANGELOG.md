# Change Log
All notable changes to this project will be documented in this file.

## 0.2.0 - 2015-02-07
### Changed
- Started keeping a changelog!
- Added a separate 'authenticate' flow to provide explicit support for
  calling out to indieauth without requesting any sort of access
  token.
- Redirect_url is now determined automatically based on the
  authenticated_handler or authorized_handler annotations
