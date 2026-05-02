<claude-mem-context>
# Memory Context

# [recording_playback_platform] recent context, 2026-04-30 2:55pm GMT+8

Legend: 🎯session 🔴bugfix 🟣feature 🔄refactor ✅change 🔵discovery ⚖️decision
Format: ID TIME TYPE TITLE
Fetch details: get_observations([IDs]) | Search: mem-search skill

Stats: 50 obs (21,222t read) | 239,145t work | 91% savings

### Apr 22, 2026
396 7:58p 🔵 MySQL Connector Artifact Inconsistency Across Loan, Didi, and Waimai Systems
398 8:00p 🔴 loan-common pom.xml - MySQL Connector Migrated to com.mysql:mysql-connector-j
399 8:54p 🔵 Loan System - All Three Services Started Successfully
401 8:55p 🔵 Loan System Port Check - Only loan-mock (28083) Actively Listening
402 " 🔵 loan-old (28081) Not Accepting Connections - curl Returns HTTP 000
405 " 🔵 loan-old Startup Failure - MySQL Connector Rejects utf8mb4 Charset
406 8:56p 🔵 loan-new Has Identical utf8mb4 Startup Failure as loan-old
408 8:58p 🔵 loan-old and loan-new JVM Processes Confirmed Dead - Only loan-mock Running
410 " 🔴 loan-old and loan-new JDBC URL Fixed - utf8mb4 Changed to utf8
413 8:59p 🔴 Loan System Maven Rebuild Succeeded After utf8mb4 Fix
415 9:01p 🔴 loan-old and loan-new Restarted After utf8mb4 Fix
416 9:28p ⚖️ Platform Sub-Call vs Database Call Comparison - Capability Question Raised
417 9:29p 🔵 Platform Sub-Call Comparison Architecture - Full Capability Confirmed for Both HTTP and MySQL
### Apr 25, 2026
451 5:13p 🔵 Frontend Project Structure - Vue Router SPA with Multi-View Architecture
453 5:15p 🔵 Router Structure vs Navigation Calls - Full Navigation Graph Mapped
### Apr 27, 2026
463 3:24p 🔵 loan-jar Integration Path Exists in Platform Repository
465 " 🔵 AREX Platform Service Registration Architecture - Full Onboarding Requirements Revealed
467 3:32p 🔵 Recording/Replay Platform - Session Lifecycle and Sub-Call Architecture Revealed
468 3:34p 🔵 ArexClient Integration - Per-App arex_storage_url and Recording Sync Architecture
470 " 🔵 Repository State - loan.jar Already Present Under systems-under-test/
472 3:35p 🔵 Recording Visibility Filter - Internal Servlet Records Excluded from Count
474 " 🔵 ArexClient Full API Surface - REST Endpoints and Replay Mock Cache Protocol
477 " 🔵 Recording Session Creation Form - application_id, name, and recording_filter_prefixes Fields
479 3:38p 🔵 Session Backend API - arex_app_id Fallback, Session States, and Deletion Guards
480 3:40p 🔵 Recording Governance Workflow - raw → candidate → approved States and Group View
482 " 🔵 Frontend Auto-Polls Session List Every 10s During Active or Collecting Sessions
485 3:41p 🔵 Recording Frontend API - Complete REST Endpoint Map for Sessions and Recordings
486 3:43p 🔵 Session Audit Log Event Types and Sync Flow Confirmed via Tests
488 3:44p 🔵 Sync Pagination Confirmed and Active Session Preview Sync Feature Detected
491 " 🔵 Batch Test Case Generation from Recordings - batchFromRecordings API with Prefix
493 3:46p 🔵 Session Detail Page - Audit Log Tab, Error Message Display, and Recording Filters
494 3:48p 🔵 Application Detail Page - testConnection and mountAgent Functions Detected
497 3:49p 🔵 Deep-Link Support on Recording Index and Single-Recording Convert Flow
498 3:51p 🔵 Session Detail Polls Every 5s During active/collecting - Including Audit Logs
500 5:27p 🔵 Platform Replay - Date Field Serialization Mismatch: Timestamp Suffix Appended
503 5:29p 🔵 Date Serialization Mismatch Root Cause - AREX Agent Captures Java Object vs HTTP Wire Format
504 5:31p 🔵 sessions.py _decode_body - Platform Does NOT Modify Date Values, Stores Raw HTTP Response
507 6:59p 🔵 Platform-Wide Normalization Architecture - Date, Mapping, and Sub-Call Patterns
508 " 🔵 transaction_mapping.py - Full Rule Engine Architecture Revealed
510 7:00p 🔵 交易码映射模板.md - User-Facing Transaction Mapping Documentation
513 7:04p 🔵 replay_job Table Missing 'error' Column
514 7:05p 🔵 replay_job Schema Uses 'errored' Not 'error' Column
516 " 🔵 Replay Job 17 - loan-jar AREX Recording Shows DateTime Format Issue in Birth Field
519 7:06p 🔵 Exact Schema Confirmed for replay_job, replay_result, replay_audit_log Tables
521 7:07p 🔵 Root Cause Confirmed: birth Field DateTime Format Mismatch Between SAT and UAT Responses
523 7:08p 🔵 Replay Executor Code Path - Where Response Mapping and Diff Are Applied
527 7:09p 🔵 Sub-Call Fetch Logic: Why loan-jar Replay Captured 0 Sub-Calls
528 7:10p 🔴 Backend Restart to Deploy Sub-Call Capture Fix and Job Name Default Fix
530 7:11p 🔴 replay_executor.py Modified and Syntax-Verified for Sub-Call Capture Fix
531 7:13p 🔴 Fixed Sub-Call Capture: Added db.commit() Before Mocker Queries in _fetch_replay_sub_calls

Access 239k tokens of past work via get_observations([IDs]) or mem-search skill.
</claude-mem-context>
