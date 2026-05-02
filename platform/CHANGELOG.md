# Changelog

This file records notable platform changes.

## Unreleased

- Documented additional runtime environment variables in `.env.example`.
- Clarified root startup script scope and updated README testing metadata.
- Normalized `CiTriggerRequest` validator declaration order without changing validation behavior.
- Added migration failure logging to make startup diagnostics easier to inspect.
- Optimized frontend Docker build layering for better cache reuse.
