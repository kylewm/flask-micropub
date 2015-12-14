# Change Log
All notable changes to this project will be documented in this file.

## 0.2.4 - 2015-12-13
### Changed
- Replace `next_url` parameter with more general `state`
  (though we're keeping `next_url` for backward compatibility for now)

## 0.2.3
### Changed
- Fix; fall back to indieauth.com when no authorization_endpoint is
  specified (previous fix broke this).

## 0.2.2
### Changed
- Fix vulnerability; re-discover the authorization_endpoint and
  token_endpoint at each stage in the flow. Prevents a buggy or
  malicious authorization_endpoint from giving you credentials for
  another user's domain name.

## 0.2.1 - 2015-02-07
### Changed
- Updated setup.py, no functional changes

## 0.2.0 - 2015-02-07
### Changed
- Started keeping a changelog!
- Added a separate 'authenticate' flow to provide explicit support for
  calling out to indieauth without requesting any sort of access
  token.
- Redirect_url is now determined automatically based on the
  authenticated_handler or authorized_handler annotations
