# Server Architecture for 20,000 Concurrent Users
## Tax Collection Platform - Infrastructure Design

**Document Version:** 1.0  
**Date:** November 7, 2025  
**Target Load:** 20,000 concurrent users

---

## Executive Summary

This document outlines the recommended server architecture to support 20,000 concurrent users on the tax collection platform. The architecture is designed for high availability, scalability, and optimal performance.

---

## Load Estimation

### Traffic Projections

**Concurrent Users:** 20,000

**Expected Load:**
- Peak requests: 2,000-4,000 requests/second
- Average user activity: 1 request every 5-10 seconds
- Database queries: 10,000-20,000 queries/second (avg 5 queries per request)
- File uploads: 100-200 uploads/minute (OCR processing)
- Email notifications: 500-1,000 emails/hour

### Data Volume Projections

**Total Vehicles:** 528,000

**Database Storage Estimate:**

```
Vehicles Table:
- 528,000 vehicles × 2 KB per record = 1.06 GB
- Indexes (30% overhead) = 0.32 GB
- Total: ~1.4 GB

Owners/Users Table:
- Estimated 300,000 unique owners × 1 KB = 300 MB
- Indexes = 90 MB
- Total: ~390 MB

Payments Table (Annual):
- 528,000 vehicles × 1 payment/year × 1.5 KB = 792 MB/year
- 5 years history = 3.96 GB
- Indexes = 1.2 GB
- Total: ~5.2 GB

Vehicle Documents (Database metadata only):
- 528,000 vehicles × 2 documents × 0.5 KB = 528 MB
- Total: ~530 MB

Audit Logs & History:
- Estimated 2 GB/year
- 3 years retention = 6 GB

Total Database Size: ~15 GB (data) + ~5 GB (indexes) = 20 GB
Growth rate: ~4 GB/year
Recommended: 100-200 GB database storage (5-10 years capacity)
```

**File Storage Estimate (S3):**

```
Vehicle Documents (Images):
- 528,000 vehicles × 2 documents (recto/verso)
- Average size: 2 MB per image (original)
- Optimized WebP: 500 KB per image
- Total original: 528,000 × 2 × 2 MB = 2.1 TB
- Total optimized: 528,000 × 2 × 0.5 MB = 528 GB
- Thumbnails (3 sizes): 528,000 × 2 × 3 × 100 KB = 317 GB

Total S3 Storage: ~3 TB (with originals + optimized + thumbnails)
Monthly cost: ~$70-90 (S3 Standard)
```

**Backup Storage:**

```
Database Backups:
- Daily snapshots: 20 GB × 30 days = 600 GB
- Monthly archives: 20 GB × 12 months = 240 GB
- Total: ~840 GB

File Backups:
- Weekly S3 versioning: ~500 GB
- Total: ~500 GB

Total Backup Storage: ~1.4 TB
Monthly cost: ~$15-20 (S3 Glacier)
```

---

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  INTERNET                                        │
│                            (20,000 Concurrent Users)                             │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            CDN / CloudFlare                                      │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  • Static Assets (CSS, JS, Images)                                       │   │
│  │  • DDoS Protection                                                        │   │
│  │  • SSL/TLS Termination                                                    │   │
│  │  • Cache TTL: 1 year                                                      │   │
│  │  • Gzip/Brotli Compression                                                │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                                     ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      LOAD BALANCER (AWS ALB / Nginx)                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  • Health Checks (every 30s)                                             │   │
│  │  • SSL Termination                                                        │   │
│  │  • Sticky Sessions (WebSocket)                                            │   │
│  │  • Request Routing                                                        │   │
│  │  • Timeout: 60 seconds                                                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
└────────────────────────────────────┬────────────────────────────────────────────┘
                                     │
                     ┌───────────────┴───────────────┐
                     │                               │
                     ↓                               ↓
┌──────────────────────────────────────┐  ┌────────────────────────────────────┐
│      APPLICATION LAYER               │  │     BACKGROUND WORKERS             │
│                                      │  │                                    │
│  ╔════════════════════════════════╗ │  │  ╔══════════════════════════════╗ │
│  ║  Django App Server 1           ║ │  │  ║  Celery Worker 1             ║ │
│  ║  • Gunicorn + gevent           ║ │  │  ║  • Email Sending             ║ │
│  ║  • 8 CPU / 16GB RAM            ║ │  │  ║  • OCR Processing            ║ │
│  ║  • 9-17 workers                ║ │  │  ║  • Image Optimization        ║ │
│  ╚════════════════════════════════╝ │  │  ║  • Report Generation         ║ │
│                                      │  │  ╚══════════════════════════════╝ │
│  ╔════════════════════════════════╗ │  │                                    │
│  ║  Django App Server 2           ║ │  │  ╔══════════════════════════════╗ │
│  ╚════════════════════════════════╝ │  │  ║  Celery Worker 2             ║ │
│                                      │  │  ╚══════════════════════════════╝ │
│  ╔════════════════════════════════╗ │  │                                    │
│  ║  Django App Server 3           ║ │  │  ╔══════════════════════════════╗ │
│  ╚════════════════════════════════╝ │  │  ║  Celery Worker 3             ║ │
│                                      │  │  ╚══════════════════════════════╝ │
│  ╔════════════════════════════════╗ │  │                                    │
│  ║  Django App Server 4           ║ │  │  ╔══════════════════════════════╗ │
│  ╚════════════════════════════════╝ │  │  ║  Celery Worker 4             ║ │
│                                      │  │  ╚══════════════════════════════╝ │
│           ... (8-12 total)           │  │                                    │
│                                      │  │  (4-6 workers total)               │
│  Auto-Scaling Group                  │  │  4 CPU / 8GB RAM each              │
│  • Min: 6 servers                    │  │  8-16 concurrent tasks             │
│  • Max: 16 servers                   │  │                                    │
│  • Scale up: CPU > 70%               │  │                                    │
│  • Scale down: CPU < 30%             │  │                                    │
└──────────┬───────────────────────────┘  └────────────┬───────────────────────┘
           │                                           │
           └─────────────┬─────────────────────────────┘
                         │
         ┌───────────────┼───────────────┬─────────────────┐
         │               │               │                 │
         ↓               ↓               ↓                 ↓
┌──────────────────┐ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐
│   POSTGRESQL     │ │   REDIS     │ │   AWS S3     │ │   MONITORING        │
│                  │ │  CLUSTER    │ │              │ │                     │
│ ╔══════════════╗ │ │             │ │ ╔══════════╗ │ │ ╔═════════════════╗ │
│ ║   PRIMARY    ║ │ │ ┌─────────┐ │ │ ║ Vehicle  ║ │ │ ║ New Relic/      ║ │
│ ║   (WRITE)    ║ │ │ │ Node 1  │ │ │ ║   Docs   ║ │ │ ║ DataDog         ║ │
│ ║              ║ │ │ │ Master  │ │ │ ╚══════════╝ │ │ ║ • APM           ║ │
│ ║ 32 CPU       ║ │ │ │ 16GB    │ │ │              │ │ ║ • Tracing       ║ │
│ ║ 128GB RAM    ║ │ │ └─────────┘ │ │ ╔══════════╗ │ │ ╚═════════════════╝ │
│ ║ 2TB SSD      ║ │ │             │ │ ║   OCR    ║ │ │                     │
│ ╚══════════════╝ │ │ ┌─────────┐ │ │ ║  Files   ║ │ │ ╔═════════════════╗ │
│        │         │ │ │ Node 2  │ │ │ ╚══════════╝ │ │ ║ ELK Stack/      ║ │
│        ↓         │ │ │ Replica │ │ │              │ │ ║ CloudWatch      ║ │
│ ╔══════════════╗ │ │ │ 16GB    │ │ │ ╔══════════╗ │ │ ║ • Logs          ║ │
│ ║  REPLICA 1   ║ │ │ └─────────┘ │ │ ║ Reports  ║ │ │ ║ • Search        ║ │
│ ║   (READ)     ║ │ │             │ │ ╚══════════╝ │ │ ╚═════════════════╝ │
│ ║              ║ │ │ ┌─────────┐ │ │              │ │                     │
│ ║ 16 CPU       ║ │ │ │ Node 3  │ │ │ ╔══════════╗ │ │ ╔═════════════════╗ │
│ ║ 64GB RAM     ║ │ │ │ Replica │ │ │ ║ Backups  ║ │ │ ║ Prometheus +    ║ │
│ ║ 2TB SSD      ║ │ │ │ 16GB    │ │ │ ╚══════════╝ │ │ ║ Grafana         ║ │
│ ╚══════════════╝ │ │ └─────────┘ │ │              │ │ ║ • Metrics       ║ │
│        │         │ │             │ │ Total: 1TB   │ │ ║ • Dashboards    ║ │
│        ↓         │ │ Uses:       │ │              │ │ ╚═════════════════╝ │
│ ╔══════════════╗ │ │ • Cache     │ │ Features:    │ │                     │
│ ║  REPLICA 2   ║ │ │ • Session   │ │ • Encrypted  │ │ ╔═════════════════╗ │
│ ║   (READ)     ║ │ │ • Queue     │ │ • Versioned  │ │ ║ Sentry          ║ │
│ ║              ║ │ │ • Limits    │ │ • Lifecycle  │ │ ║ Error Tracking  ║ │
│ ║ 16 CPU       ║ │ │             │ │ • CDN        │ │ ║ • Real-time     ║ │
│ ║ 64GB RAM     ║ │ │ Total:      │ │              │ │ ║ • Alerts        ║ │
│ ║ 2TB SSD      ║ │ │ 48GB RAM    │ │              │ │ ╚═════════════════╝ │
│ ╚══════════════╝ │ │             │ │              │ │                     │
│                  │ │             │ │              │ │ Real-time Alerts    │
│ + PgBouncer      │ │             │ │              │ │ Email/SMS/Slack     │
│ Connection Pool  │ │             │ │              │ │                     │
│ 500-1000 conns   │ │             │ │              │ │                     │
└──────────────────┘ └─────────────┘ └──────────────┘ └─────────────────────┘
```

---

## Request Flow Diagram

```
USER REQUEST FLOW (Typical Web Request):
═══════════════════════════════════════════

Step 1: User Action
┌──────────┐
│  User    │  Clicks "View Vehicles" button
│ Browser  │
└────┬─────┘
     │
     ↓
Step 2: CDN Check
┌──────────────┐
│  CloudFlare  │  Static assets? → Return cached (CSS, JS, images)
│     CDN      │  Dynamic request? → Pass through
└──────┬───────┘
       │
       ↓
Step 3: Load Balancer
┌──────────────┐
│     ALB      │  • Check health of app servers
│Load Balancer │  • Route to available server
└──────┬───────┘  • Apply sticky session if needed
       │
       ↓
Step 4: Django Application
┌────────────────────────────────────────────────────────────┐
│  Django App Server                                         │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 1. Check Redis Cache                                 │ │
│  │    Key: "vehicles_list_user_123"                     │ │
│  │    ├─ HIT? → Return cached data (fast!)             │ │
│  │    └─ MISS? → Continue to database                  │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 2. Query Database                                    │ │
│  │    • SELECT * FROM vehicles WHERE owner_id = 123     │ │
│  │    • Use Read Replica (not Primary)                  │ │
│  │    • Apply select_related() for optimization         │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 3. Process Data                                      │ │
│  │    • Apply business logic                            │ │
│  │    • Format for template                             │ │
│  │    • Store in Redis cache (5 min TTL)               │ │
│  └──────────────────────────────────────────────────────┘ │
│                                                            │
│  ┌──────────────────────────────────────────────────────┐ │
│  │ 4. Render Template                                   │ │
│  │    • Use cached template (production)                │ │
│  │    • Inject data                                     │ │
│  │    • Generate HTML                                   │ │
│  └──────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────┘
       │
       ↓
Step 5: Return Response
┌──────────────┐
│   Browser    │  Receives HTML + references to CDN assets
│   Renders    │  Total time: 50-200ms
└──────────────┘
```

---

## Background Task Flow

```
BACKGROUND TASK PROCESSING (OCR Example):
═══════════════════════════════════════════

Step 1: User Uploads Document
┌──────────────┐
│    User      │  Uploads carte grise image
└──────┬───────┘
       │
       ↓
Step 2: Django Receives Upload
┌────────────────────────────────────────────────────────┐
│  Django App Server                                     │
│                                                        │
│  1. Validate file (size, type)                        │
│  2. Save to S3: /ocr/pending/doc_12345.jpg            │
│  3. Create database record: status="pending"          │
│  4. Queue Celery task: process_ocr.delay(doc_id)      │
│  5. Return immediately: "Processing..."               │
│                                                        │
│  Response time: < 1 second                            │
└────────────────────────────────────────────────────────┘
       │
       ↓
Step 3: Task Queued in Redis
┌────────────────┐
│  Redis Broker  │  Task: {"task": "process_ocr", "args": [12345]}
│  (Queue)       │  Priority: "low_priority" queue
└────────┬───────┘
         │
         ↓
Step 4: Celery Worker Picks Up Task
┌────────────────────────────────────────────────────────┐
│  Celery Worker                                         │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 1. Download from S3                              │ │
│  │    GET /ocr/pending/doc_12345.jpg                │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 2. Process with OCR Engine                       │ │
│  │    • Detect text regions                         │ │
│  │    • Extract: plate, owner, date, etc.           │ │
│  │    • Validate extracted data                     │ │
│  │    Processing time: 5-15 seconds                 │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 3. Save Results                                  │ │
│  │    • Update database: status="completed"         │ │
│  │    • Save extracted data                         │ │
│  │    • Upload processed image to S3                │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ 4. Notify User                                   │ │
│  │    • Create notification record                  │ │
│  │    • Send WebSocket message (if online)          │ │
│  │    • Queue email task (if configured)            │ │
│  └──────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────┘
       │
       ↓
Step 5: User Sees Result
┌──────────────┐
│   Browser    │  Real-time notification: "OCR Complete!"
│   Updates    │  Can now view extracted data
└──────────────┘
```

---

## Database Replication Flow

```
DATABASE WRITE & REPLICATION:
═══════════════════════════════

Write Operation (e.g., Create Payment):
┌────────────────────────────────────────────────────────┐
│  Django App Server                                     │
│  payment = Payment.objects.create(...)                 │
└────────────────┬───────────────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────────────────┐
│  PostgreSQL PRIMARY (Write)                            │
│                                                        │
│  1. Receive INSERT query                              │
│  2. Write to WAL (Write-Ahead Log)                    │
│  3. Write to data files                               │
│  4. Commit transaction                                │
│  5. Return success to Django                          │
│                                                        │
│  Write time: 5-20ms                                   │
└────────────────┬───────────────────────────────────────┘
                 │
                 ├─────────────────┬─────────────────┐
                 ↓                 ↓                 ↓
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│  Replica 1 (Read)    │  │  Replica 2 (Read)    │  │  Replica 3 (Read)    │
│                      │  │                      │  │                      │
│  1. Stream WAL       │  │  1. Stream WAL       │  │  1. Stream WAL       │
│  2. Apply changes    │  │  2. Apply changes    │  │  2. Apply changes    │
│  3. Ready for reads  │  │  3. Ready for reads  │  │  3. Ready for reads  │
│                      │  │                      │  │                      │
│  Lag: < 100ms        │  │  Lag: < 100ms        │  │  Lag: < 100ms        │
└──────────────────────┘  └──────────────────────┘  └──────────────────────┘


Read Operation (e.g., List Vehicles):
┌────────────────────────────────────────────────────────┐
│  Django App Server                                     │
│  vehicles = Vehicle.objects.using('replica').all()     │
└────────────────┬───────────────────────────────────────┘
                 │
                 ↓
┌────────────────────────────────────────────────────────┐
│  PostgreSQL REPLICA (Read)                             │
│                                                        │
│  1. Receive SELECT query                              │
│  2. Read from data files                              │
│  3. Return results                                    │
│                                                        │
│  Read time: 2-10ms                                    │
│  No impact on Primary                                 │
└────────────────────────────────────────────────────────┘
```

---
## Network Architecture (Multi-AZ Deployment)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              AWS REGION (e.g., us-east-1)                        │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         AVAILABILITY ZONE 1                                 │ │
│  │                                                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                        PUBLIC SUBNET (10.0.1.0/24)                     │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────────┐         ┌──────────────────┐                   │ │ │
│  │  │  │  Load Balancer 1 │         │  NAT Gateway 1   │                   │ │ │
│  │  │  │  (ALB)           │         │                  │                   │ │ │
│  │  │  └──────────────────┘         └──────────────────┘                   │ │ │
│  │  │                                                                        │ │ │
│  │  └───────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                      PRIVATE SUBNET (10.0.2.0/24)                      │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │ │ │
│  │  │  │  App Server  │  │  App Server  │  │  App Server  │               │ │ │
│  │  │  │      1       │  │      2       │  │      3       │               │ │ │
│  │  │  │  10.0.2.10   │  │  10.0.2.11   │  │  10.0.2.12   │               │ │ │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘               │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐                                 │ │ │
│  │  │  │Celery Worker │  │Celery Worker │                                 │ │ │
│  │  │  │      1       │  │      2       │                                 │ │ │
│  │  │  │  10.0.2.20   │  │  10.0.2.21   │                                 │ │ │
│  │  │  └──────────────┘  └──────────────┘                                 │ │ │
│  │  │                                                                        │ │ │
│  │  └───────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                     DATABASE SUBNET (10.0.3.0/24)                      │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────────┐         ┌──────────────────┐                   │ │ │
│  │  │  │  PostgreSQL      │         │    Redis         │                   │ │ │
│  │  │  │  PRIMARY         │         │    Node 1        │                   │ │ │
│  │  │  │  10.0.3.10       │         │    10.0.3.20     │                   │ │ │
│  │  │  └──────────────────┘         └──────────────────┘                   │ │ │
│  │  │                                                                        │ │ │
│  │  └───────────────────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         AVAILABILITY ZONE 2                                 │ │
│  │                                                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                        PUBLIC SUBNET (10.0.11.0/24)                    │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────────┐         ┌──────────────────┐                   │ │ │
│  │  │  │  Load Balancer 2 │         │  NAT Gateway 2   │                   │ │ │
│  │  │  │  (ALB)           │         │                  │                   │ │ │
│  │  │  └──────────────────┘         └──────────────────┘                   │ │ │
│  │  │                                                                        │ │ │
│  │  └───────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                      PRIVATE SUBNET (10.0.12.0/24)                     │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │ │ │
│  │  │  │  App Server  │  │  App Server  │  │  App Server  │               │ │ │
│  │  │  │      4       │  │      5       │  │      6       │               │ │ │
│  │  │  │  10.0.12.10  │  │  10.0.12.11  │  │  10.0.12.12  │               │ │ │
│  │  │  └──────────────┘  └──────────────┘  └──────────────┘               │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────┐  ┌──────────────┐                                 │ │ │
│  │  │  │Celery Worker │  │Celery Worker │                                 │ │ │
│  │  │  │      3       │  │      4       │                                 │ │ │
│  │  │  │  10.0.12.20  │  │  10.0.12.21  │                                 │ │ │
│  │  │  └──────────────┘  └──────────────┘                                 │ │ │
│  │  │                                                                        │ │ │
│  │  └───────────────────────────────────────────────────────────────────────┘ │ │
│  │                                                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                     DATABASE SUBNET (10.0.13.0/24)                     │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────────┐         ┌──────────────────┐                   │ │ │
│  │  │  │  PostgreSQL      │         │    Redis         │                   │ │ │
│  │  │  │  REPLICA 1       │         │    Node 2        │                   │ │ │
│  │  │  │  10.0.13.10      │         │    10.0.13.20    │                   │ │ │
│  │  │  └──────────────────┘         └──────────────────┘                   │ │ │
│  │  │                                                                        │ │ │
│  │  └───────────────────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
│  ┌────────────────────────────────────────────────────────────────────────────┐ │
│  │                         AVAILABILITY ZONE 3                                 │ │
│  │                                                                             │ │
│  │  ┌───────────────────────────────────────────────────────────────────────┐ │ │
│  │  │                     DATABASE SUBNET (10.0.23.0/24)                     │ │ │
│  │  │                                                                        │ │ │
│  │  │  ┌──────────────────┐         ┌──────────────────┐                   │ │ │
│  │  │  │  PostgreSQL      │         │    Redis         │                   │ │ │
│  │  │  │  REPLICA 2       │         │    Node 3        │                   │ │ │
│  │  │  │  10.0.23.10      │         │    10.0.23.20    │                   │ │ │
│  │  │  └──────────────────┘         └──────────────────┘                   │ │ │
│  │  │                                                                        │ │ │
│  │  └───────────────────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────────────────────────┐
                    │         AWS S3 (Cross-Region)        │
                    │  • Vehicle Documents                 │
                    │  • OCR Files                         │
                    │  • Reports                           │
                    │  • Backups                           │
                    │  • Encrypted at rest                 │
                    │  • Versioning enabled                │
                    └──────────────────────────────────────┘

Security Groups:
• ALB: Allow 80, 443 from 0.0.0.0/0
• App Servers: Allow 8000 from ALB only
• Database: Allow 5432 from App Servers only
• Redis: Allow 6379 from App Servers only
```

---

## Infrastructure Components Detail

### 1. Load Balancer Layer

**Technology:** AWS Application Load Balancer (ALB) or Nginx

**Configuration:**
- 2 instances across 2 availability zones
- SSL/TLS termination (TLS 1.3)
- Health checks every 30 seconds
- Automatic failover (< 30 seconds)
- Sticky sessions for WebSocket connections
- Request timeout: 60 seconds
- Connection draining: 300 seconds

**Features:**
- Geographic load distribution
- DDoS protection (via CloudFlare)
- Rate limiting at edge
- Request routing based on URL patterns
- HTTP/2 and HTTP/3 support

---

### 2. Application Layer (Django)

**Servers:** 8-12 application servers

**Server Specifications (per instance):**
- CPU: 4-8 cores (c5.2xlarge or equivalent)
- RAM: 16-32 GB
- Storage: 50-100 GB SSD
- Network: 10 Gbps

**Application Server Stack:**
- OS: Ubuntu 22.04 LTS or Amazon Linux 2
- Python: 3.11+
- Django: 4.2+ (LTS)
- WSGI Server: Gunicorn
- Worker Class: gevent (for async I/O)

**Gunicorn Configuration:**

```python
# gunicorn.conf.py
import multiprocessing

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1  # 9-17 workers per server
worker_class = 'gevent'
worker_connections = 1000

# Performance tuning
max_requests = 1000
max_requests_jitter = 50
timeout = 30
keepalive = 5
graceful_timeout = 30

# Logging
accesslog = '/var/log/gunicorn/access.log'
errorlog = '/var/log/gunicorn/error.log'
loglevel = 'info'

# Security
limit_request_line = 4096
limit_request_fields = 100
```

**Auto-scaling Configuration:**
- Scale up: CPU > 70% for 5 minutes
- Scale down: CPU < 30% for 10 minutes
- Min instances: 6
- Max instances: 16
- Cooldown period: 5 minutes

---
### 3. Database Layer (PostgreSQL)

**Architecture:** Primary-Replica Setup

**Primary Database (Write Operations):**
- Instance: db.r5.4xlarge or equivalent
- CPU: 16-32 cores
- RAM: 64-128 GB
- Storage: 200-500 GB SSD (IOPS: 10,000+)
  - Current data: ~20 GB
  - Growth capacity: 5-10 years
  - Working space: 50 GB
  - Temp tables & indexes: 30 GB
- Backup: Automated daily snapshots + WAL archiving
- Retention: 30 days

**Read Replicas (Read Operations):**
- Count: 2-3 replicas
- Instance: db.r5.2xlarge per replica
- CPU: 8-16 cores per replica
- RAM: 32-64 GB per replica
- Storage: 200-500 GB SSD (same as primary)
- Replication lag: < 1 second
- Automatic failover enabled

**Connection Pooling (PgBouncer):**
- Max connections: 500-1000
- Pool mode: Transaction
- Default pool size: 25 per database
- Reserve pool: 5 connections

**PostgreSQL Configuration:**

```ini
# postgresql.conf (optimized for high load)
max_connections = 500
shared_buffers = 16GB
effective_cache_size = 48GB
maintenance_work_mem = 2GB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 32MB
min_wal_size = 2GB
max_wal_size = 8GB
max_worker_processes = 8
max_parallel_workers_per_gather = 4
max_parallel_workers = 8
```

**Database Optimization for 528K Vehicles:**

```sql
-- Partitioning strategy for large tables
-- Partition payments by year for better performance
CREATE TABLE payments_2024 PARTITION OF payments
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01');

CREATE TABLE payments_2025 PARTITION OF payments
    FOR VALUES FROM ('2025-01-01') TO ('2026-01-01');

-- Indexes for common queries
CREATE INDEX idx_vehicles_plate ON vehicles(plate_number);
CREATE INDEX idx_vehicles_owner ON vehicles(owner_id);
CREATE INDEX idx_vehicles_status_created ON vehicles(status, created_at DESC);
CREATE INDEX idx_payments_vehicle_year ON payments(vehicle_id, payment_year);
CREATE INDEX idx_payments_status_due ON payments(status, due_date);

-- Full-text search for vehicle/owner search
CREATE INDEX idx_vehicles_search ON vehicles 
    USING gin(to_tsvector('french', plate_number || ' ' || COALESCE(owner_name, '')));

-- Materialized view for dashboard statistics
CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT 
    COUNT(*) as total_vehicles,
    COUNT(CASE WHEN status = 'active' THEN 1 END) as active_vehicles,
    SUM(CASE WHEN payment_status = 'paid' THEN amount ELSE 0 END) as total_collected,
    COUNT(CASE WHEN payment_status = 'pending' THEN 1 END) as pending_payments
FROM vehicles v
LEFT JOIN payments p ON v.id = p.vehicle_id AND p.payment_year = EXTRACT(YEAR FROM CURRENT_DATE);

-- Refresh materialized view hourly via cron
REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;
```

**Query Performance Targets:**

| Query Type | Target Time | Example |
|------------|-------------|---------|
| Vehicle lookup by plate | < 10ms | Single vehicle details |
| Owner's vehicles list | < 50ms | List of 1-50 vehicles |
| Payment history | < 100ms | 5 years of payments |
| Search (10 results) | < 200ms | Full-text search |
| Dashboard stats | < 50ms | From materialized view |
| Bulk operations | < 5s | 1000 records |

---

### 4. Caching Layer (Redis)

**Architecture:** Redis Cluster

**Configuration:**
- Nodes: 3-5 nodes (1 master + 2-4 replicas)
- Instance: cache.r5.large per node
- RAM per node: 8-16 GB
- Persistence: RDB + AOF
- Eviction policy: allkeys-lru
- Cluster mode: Enabled

**Use Cases:**

1. **Session Storage**
   - User sessions
   - Authentication tokens
   - CSRF tokens
   - TTL: 24 hours

2. **Query Result Caching**
   - Vehicle lookups
   - Price grid calculations
   - User permissions
   - TTL: 5-15 minutes

3. **Rate Limiting**
   - API endpoint throttling
   - Login attempt tracking
   - OCR request limiting
   - TTL: 1 hour

4. **Real-time Features**
   - Notification queues
   - WebSocket message broker
   - Live dashboard updates
   - TTL: Variable

**Redis Configuration:**

```conf
# redis.conf
maxmemory 8gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
tcp-keepalive 300
timeout 0
```

---

### 5. Task Queue (Celery)

**Workers:** 4-6 Celery worker instances

**Worker Specifications:**
- Instance: c5.xlarge
- CPU: 4 cores
- RAM: 8 GB
- Concurrency: 8-16 tasks per worker
- Total capacity: 32-96 concurrent tasks

**Message Broker:** Redis

**Task Categories:**

1. **High Priority Queue** (processed first)
   - Payment processing
   - User notifications
   - Critical updates
   - Workers: 2 dedicated

2. **Medium Priority Queue**
   - Email sending
   - Report generation
   - Data exports
   - Workers: 2 dedicated

3. **Low Priority Queue**
   - OCR processing
   - Image optimization
   - Batch operations
   - Cleanup tasks
   - Workers: 2 dedicated

**Celery Configuration:**

```python
# celery.py
from celery import Celery

app = Celery('tax_platform')

app.conf.update(
    broker_url='redis://redis-cluster:6379/0',
    result_backend='redis://redis-cluster:6379/0',
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Performance
    worker_prefetch_multiplier=4,
    worker_max_tasks_per_child=1000,
    task_acks_late=True,
    
    # Queues
    task_routes={
        'payments.*': {'queue': 'high_priority'},
        'notifications.*': {'queue': 'high_priority'},
        'emails.*': {'queue': 'medium_priority'},
        'reports.*': {'queue': 'medium_priority'},
        'ocr.*': {'queue': 'low_priority'},
        'images.*': {'queue': 'low_priority'},
    },
    
    # Retry policy
    task_default_retry_delay=60,
    task_max_retries=3,
)
```

---

### 6. File Storage (AWS S3)

**Primary Storage:** AWS S3

**Bucket Structure:**
```
tax-platform-production/
├── media/
│   ├── vehicle-documents/
│   │   ├── recto/
│   │   └── verso/
│   ├── ocr-uploads/
│   │   ├── pending/
│   │   ├── processed/
│   │   └── failed/
│   ├── reports/
│   │   ├── daily/
│   │   ├── monthly/
│   │   └── annual/
│   └── user-uploads/
└── backups/
    ├── database/
    └── application/
```

**CDN:** CloudFront or CloudFlare

**Static Assets Configuration:**
- CSS, JavaScript, images, fonts
- Cache TTL: 1 year (with versioning)
- Gzip/Brotli compression enabled
- HTTP/2 enabled
- Edge locations: Global

**Storage Policies:**
- Lifecycle rules:
  - Move to Glacier after 90 days (backups)
  - Delete after 1 year (temp files)
- Versioning enabled (critical buckets)
- Cross-region replication (disaster recovery)
- Encryption at rest (AES-256)
- Encryption in transit (TLS 1.3)

---

### 7. Monitoring & Logging

**Application Performance Monitoring:**
- Tool: New Relic, DataDog, or Sentry
- Metrics tracked:
  - Response time (p50, p95, p99)
  - Error rate (4xx, 5xx)
  - Throughput (requests/second)
  - Apdex score
- Alerts: Email/SMS/Slack for critical issues
- Cost: ~$200/month

**Log Aggregation:**
- Tool: ELK Stack (Elasticsearch, Logstash, Kibana) or CloudWatch
- Log sources:
  - Application logs (Django)
  - Web server logs (Gunicorn)
  - Database logs (PostgreSQL)
  - System logs (syslog)
- Retention: 30 days hot, 90 days cold
- Log levels: INFO (production), DEBUG (staging)
- Cost: ~$100-150/month

**Metrics & Dashboards:**
- Tool: Prometheus + Grafana
- System metrics:
  - CPU utilization
  - Memory usage
  - Disk I/O
  - Network throughput
- Application metrics:
  - Request rate
  - Response latency
  - Error rate
  - Cache hit ratio
- Business metrics:
  - Payments processed
  - New registrations
  - OCR success rate
  - Active users
- Cost: ~$50/month (self-hosted)

**Key Metrics to Monitor:**

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| Response time (p95) | < 500ms | > 1000ms |
| Error rate | < 0.1% | > 1% |
| Database CPU | < 70% | > 85% |
| Cache hit ratio | > 80% | < 60% |
| Queue length | < 100 | > 500 |
| Disk usage | < 80% | > 90% |
| Memory usage | < 80% | > 90% |

---

## Django Application Optimization

### Database Configuration

```python
# settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tax_platform',
        'USER': 'app_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'db-primary.internal',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,  # Connection pooling
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30 seconds
        },
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tax_platform',
        'USER': 'app_user',
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': 'db-replica.internal',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}

# Database router for read/write splitting
DATABASE_ROUTERS = ['core.db_router.ReadReplicaRouter']
```

### Cache Configuration

```python
# settings.py

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis-cluster:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            },
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        },
        'KEY_PREFIX': 'tax_platform',
        'TIMEOUT': 300,  # 5 minutes default
    }
}

# Session storage in Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 hours
```

### Performance Settings

```python
# settings.py

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATIC_URL = 'https://cdn.example.com/static/'

# Media files
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = 'https://cdn.example.com/media/'

# Template caching
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
    },
}]
```

---

## Financial Summary - Infrastructure Costs

### Monthly Cost Breakdown (AWS)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE COST SUMMARY                              │
│                    Tax Collection Platform (20K Users)                       │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║                          COMPUTE RESOURCES                                 ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Component                    │ Quantity │ Unit Price │ Monthly Cost        ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ Django App Servers           │    8     │   $150     │    $1,200          ║
║ (c5.2xlarge - 8CPU/16GB)     │          │            │                    ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ Celery Workers               │    4     │   $100     │      $400          ║
║ (c5.xlarge - 4CPU/8GB)       │          │            │                    ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ Load Balancers (ALB)         │    2     │    $25     │       $50          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║                              │          │   SUBTOTAL │    $1,650          ║
╚═══════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════╗
║                          DATABASE RESOURCES                                ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Component                    │ Quantity │ Unit Price │ Monthly Cost        ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ PostgreSQL Primary           │    1     │  $1,200    │    $1,200          ║
║ (db.r5.4xlarge - 32CPU/128GB)│          │            │                    ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ PostgreSQL Read Replicas     │    2     │   $400     │      $800          ║
║ (db.r5.2xlarge - 16CPU/64GB) │          │            │                    ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ Database Backup Storage      │  500GB   │   $0.10/GB │       $50          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║                              │          │   SUBTOTAL │    $2,050          ║
╚═══════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════╗
║                          CACHING & QUEUE                                   ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Component                    │ Quantity │ Unit Price │ Monthly Cost        ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ Redis Cluster                │    3     │   $133     │      $400          ║
║ (cache.r5.large - 16GB)      │  nodes   │            │                    ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║                              │          │   SUBTOTAL │      $400          ║
╚═══════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════╗
║                          STORAGE & FILES                                   ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Component                    │ Quantity │ Unit Price │ Monthly Cost        ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ S3 Storage (Vehicle Docs)    │   3 TB   │  $0.023/GB │       $70          ║
║ • Original images            │          │            │                    ║
║ • Optimized WebP             │          │            │                    ║
║ • Thumbnails                 │          │            │                    ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ S3 Requests                  │   ~1M    │  $0.005/1K │        $5          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ S3 Glacier (Backups)         │  1.4 TB  │  $0.004/GB │        $6          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ EBS Volumes (App Servers)    │  800 GB  │  $0.10/GB  │       $80          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║                              │          │   SUBTOTAL │      $161          ║
╚═══════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════╗
║                          NETWORK & CDN                                     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Component                    │ Quantity │ Unit Price │ Monthly Cost        ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ CloudFront CDN               │   5 TB   │  $0.085/GB │      $425          ║
║ (Static assets delivery)     │          │            │                    ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ Data Transfer Out            │   2 TB   │  $0.09/GB  │      $180          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ CloudFlare (DDoS Protection) │    1     │    $200    │      $200          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║                              │          │   SUBTOTAL │      $805          ║
╚═══════════════════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════════════════╗
║                       MONITORING & SECURITY                                ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Component                    │ Quantity │ Unit Price │ Monthly Cost        ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ CloudWatch Logs & Metrics    │    -     │     -      │      $100          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ DataDog / New Relic (APM)    │    1     │    $200    │      $200          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ Sentry (Error Tracking)      │    1     │     $50    │       $50          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║ AWS WAF (Web Firewall)       │    1     │     $50    │       $50          ║
╟───────────────────────────────┼──────────┼────────────┼─────────────────────╢
║                              │          │   SUBTOTAL │      $400          ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────────┐
│                         TOTAL MONTHLY COST                                   │
│                                                                              │
│  Compute Resources:                                        $1,650            │
│  Database Resources:                                       $2,050            │
│  Caching & Queue:                                            $400            │
│  Storage & Files:                                            $161            │
│  Network & CDN:                                              $805            │
│  Monitoring & Security:                                      $400            │
│  ─────────────────────────────────────────────────────────────────          │
│  TOTAL (Standard Pricing):                                 $5,466            │
│                                                                              │
│  With Reserved Instances (1-year):                         $4,200            │
│  With Reserved Instances (3-year):                         $3,500            │
│  With Full Optimization:                                   $3,200            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Annual Cost Projection

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ANNUAL COST PROJECTION                               │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║ Pricing Model              │ Monthly Cost │ Annual Cost │ Savings          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ On-Demand (Standard)       │   $5,466     │  $65,592    │      -          ║
╟───────────────────────────────────────────────────────────────────────────╢
║ 1-Year Reserved Instances  │   $4,200     │  $50,400    │  $15,192 (23%)  ║
╟───────────────────────────────────────────────────────────────────────────╢
║ 3-Year Reserved Instances  │   $3,500     │  $42,000    │  $23,592 (36%)  ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Fully Optimized            │   $3,200     │  $38,400    │  $27,192 (41%)  ║
╚═══════════════════════════════════════════════════════════════════════════╝

Recommended: Start with 1-Year Reserved Instances
```

### Cost Optimization Strategies

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      COST OPTIMIZATION OPPORTUNITIES                         │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║ Strategy                   │ Savings/Month │ Savings/Year │ Difficulty     ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Reserved Instances         │    $1,266     │   $15,192    │   Easy        ║
║ (1-year commitment)        │               │              │               ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Auto-Scaling               │      $800     │    $9,600    │   Medium      ║
║ (off-peak scale down)      │               │              │               ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Spot Instances (Celery)    │      $200     │    $2,400    │   Medium      ║
║ (50-70% discount)          │               │              │               ║
╟───────────────────────────────────────────────────────────────────────────╢
║ S3 Lifecycle Policies      │       $50     │      $600    │   Easy        ║
║ (move to Glacier)          │               │              │               ║
╟───────────────────────────────────────────────────────────────────────────╢
║ CDN Optimization           │      $150     │    $1,800    │   Easy        ║
║ (better caching)           │               │              │               ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Database Right-Sizing      │      $300     │    $3,600    │   Medium      ║
║ (after load testing)       │               │              │               ║
╟───────────────────────────────────────────────────────────────────────────╢
║ TOTAL POTENTIAL SAVINGS    │    $2,766     │   $33,192    │               ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### Cost Per User Analysis

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         COST PER USER BREAKDOWN                              │
└─────────────────────────────────────────────────────────────────────────────┘

Total Users: 20,000 concurrent users
Total Vehicles: 528,000 registered vehicles

╔═══════════════════════════════════════════════════════════════════════════╗
║ Metric                     │ Standard      │ Optimized    │ Notes          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Cost per Concurrent User   │    $0.27      │    $0.16     │ Per month     ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Cost per Vehicle           │    $0.01      │    $0.006    │ Per month     ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Cost per Transaction       │    $0.003     │    $0.002    │ Estimated     ║
╚═══════════════════════════════════════════════════════════════════════════╝

At optimized pricing ($3,200/month):
• $0.16 per concurrent user per month
• $0.006 per registered vehicle per month
• $38,400 per year total infrastructure cost
```

### One-Time Setup Costs

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ONE-TIME SETUP COSTS                                 │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║ Item                       │ Cost          │ Notes                          ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ AWS Account Setup          │    $0         │ Free                          ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Domain Registration        │   $12         │ .com domain (annual)          ║
╟───────────────────────────────────────────────────────────────────────────╢
║ SSL Certificate            │    $0         │ AWS Certificate Manager       ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Initial Data Migration     │  $500         │ Professional services         ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Load Testing               │  $200         │ Tools & testing time          ║
╟───────────────────────────────────────────────────────────────────────────╢
║ DevOps Setup & Config      │ $2,000        │ Infrastructure as Code        ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Training & Documentation   │ $1,000        │ Team onboarding               ║
╟───────────────────────────────────────────────────────────────────────────╢
║ TOTAL ONE-TIME COST        │ $3,712        │                               ║
╚═══════════════════════════════════════════════════════════════════════════╝
```

### 3-Year Total Cost of Ownership (TCO)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    3-YEAR TOTAL COST OF OWNERSHIP                            │
└─────────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║ Cost Category              │ Year 1   │ Year 2   │ Year 3   │ Total        ║
╠═══════════════════════════════════════════════════════════════════════════╣
║ Infrastructure (Optimized) │ $38,400  │ $38,400  │ $38,400  │ $115,200    ║
╟───────────────────────────────────────────────────────────────────────────╢
║ One-Time Setup             │  $3,712  │      $0  │      $0  │   $3,712    ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Support & Maintenance      │  $6,000  │  $6,000  │  $6,000  │  $18,000    ║
╟───────────────────────────────────────────────────────────────────────────╢
║ Growth Buffer (20%)        │  $7,680  │  $7,680  │  $7,680  │  $23,040    ║
╟───────────────────────────────────────────────────────────────────────────╢
║ TOTAL                      │ $55,792  │ $52,080  │ $52,080  │ $159,952    ║
╚═══════════════════════════════════════════════════════════════════════════╝

Average Monthly Cost: $4,443
Average Annual Cost: $53,317
```

### Budget Recommendations

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BUDGET RECOMMENDATIONS                               │
└─────────────────────────────────────────────────────────────────────────────┘

Phase 1: Launch (Months 1-3)
├─ Budget: $6,000/month
├─ Configuration: Minimum viable infrastructure
└─ Users: 5,000-10,000 concurrent

Phase 2: Growth (Months 4-12)
├─ Budget: $4,500/month
├─ Configuration: Optimized with reserved instances
└─ Users: 10,000-20,000 concurrent

Phase 3: Stable (Year 2+)
├─ Budget: $3,500/month
├─ Configuration: Fully optimized with 3-year reserved
└─ Users: 20,000+ concurrent

Emergency Buffer: $5,000 (one-time)
├─ For unexpected traffic spikes
└─ Additional storage needs
```

---

## Performance Optimization Strategies

### 1. Database Query Optimization

**Best Practices:**

```python
# Use select_related for foreign keys (1 query instead of N+1)
vehicles = Vehicle.objects.select_related('owner', 'price_grid').all()

# Use prefetch_related for many-to-many and reverse foreign keys
users = User.objects.prefetch_related('vehicles', 'payments').all()

# Use only() to fetch specific fields
vehicles = Vehicle.objects.only('plate_number', 'owner__name').all()

# Use defer() to exclude heavy fields
vehicles = Vehicle.objects.defer('document_recto', 'document_verso').all()

# Bulk operations (much faster than loops)
Vehicle.objects.bulk_create(vehicle_list, batch_size=1000)
Vehicle.objects.bulk_update(vehicle_list, ['status'], batch_size=1000)

# Aggregate at database level
from django.db.models import Count, Sum, Avg
stats = Payment.objects.aggregate(
    total=Sum('amount'),
    count=Count('id'),
    average=Avg('amount')
)

# Use iterator() for large querysets
for vehicle in Vehicle.objects.iterator(chunk_size=1000):
    process_vehicle(vehicle)
```

**Indexing Strategy:**

```python
# models.py
class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20, db_index=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
    status = models.CharField(max_length=20, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        indexes = [
            # Composite indexes for common queries
            models.Index(fields=['plate_number', 'status']),
            models.Index(fields=['owner', 'created_at']),
            models.Index(fields=['-created_at']),  # For ordering
            models.Index(fields=['status', 'created_at']),
        ]
```

---

### 2. Caching Strategy

**View Caching:**

```python
from django.views.decorators.cache import cache_page

# Cache entire view for 15 minutes
@cache_page(60 * 15)
def vehicle_list(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicles/list.html', {'vehicles': vehicles})

# Cache with user-specific key
@cache_page(60 * 15, key_prefix='user_%(user_id)s')
def user_dashboard(request):
    return render(request, 'dashboard.html')
```

**Template Fragment Caching:**

```django
{% load cache %}

{% cache 600 sidebar request.user.id %}
    <div class="sidebar">
        ... expensive sidebar rendering ...
    </div>
{% endcache %}

{% cache 3600 price_grid vehicle.type %}
    <div class="price-info">
        ... price calculation ...
    </div>
{% endcache %}
```

**Low-level Caching:**

```python
from django.core.cache import cache

def get_price_grid(vehicle_type):
    cache_key = f'price_grid_{vehicle_type}'
    price_grid = cache.get(cache_key)
    
    if price_grid is None:
        price_grid = PriceGrid.objects.get(vehicle_type=vehicle_type)
        cache.set(cache_key, price_grid, 3600)  # 1 hour
    
    return price_grid

# Cache with multiple keys
def get_user_vehicles(user_id):
    cache_key = f'user_vehicles_{user_id}'
    vehicles = cache.get(cache_key)
    
    if vehicles is None:
        vehicles = list(Vehicle.objects.filter(owner_id=user_id).values())
        cache.set(cache_key, vehicles, 300)  # 5 minutes
    
    return vehicles

# Invalidate cache on update
def update_vehicle(vehicle_id, data):
    vehicle = Vehicle.objects.get(id=vehicle_id)
    vehicle.status = data['status']
    vehicle.save()
    
    # Invalidate related caches
    cache.delete(f'vehicle_{vehicle_id}')
    cache.delete(f'user_vehicles_{vehicle.owner_id}')
```

---

### 3. Async Processing

**Move Heavy Tasks to Celery:**

```python
# tasks.py
from celery import shared_task
from django.core.mail import send_mail

@shared_task(bind=True, max_retries=3)
def process_ocr(self, document_id):
    try:
        document = VehicleDocument.objects.get(id=document_id)
        # OCR processing logic
        result = perform_ocr(document.image.path)
        document.extracted_data = result
        document.status = 'completed'
        document.save()
        return result
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

@shared_task
def send_payment_reminder(payment_id):
    payment = Payment.objects.get(id=payment_id)
    send_mail(
        subject='Payment Reminder',
        message=f'Your payment of {payment.amount} is due',
        from_email='noreply@example.com',
        recipient_list=[payment.user.email],
    )
    return True

@shared_task
def optimize_image(image_path):
    from PIL import Image
    img = Image.open(image_path)
    img.thumbnail((1920, 1080))
    optimized_path = image_path.replace('.jpg', '_optimized.webp')
    img.save(optimized_path, 'WEBP', quality=85)
    return optimized_path

@shared_task
def generate_monthly_report(month, year):
    # Heavy report generation
    data = Payment.objects.filter(
        created_at__month=month,
        created_at__year=year
    ).aggregate(
        total=Sum('amount'),
        count=Count('id')
    )
    # Generate PDF, save to S3
    return data
```

**Usage in Views:**

```python
def upload_document(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save()
            
            # Process asynchronously
            process_ocr.delay(document.id)
            
            messages.success(request, 'Document uploaded. Processing...')
            return redirect('document_list')
    
    return render(request, 'upload.html', {'form': form})

def send_reminders(request):
    # Queue all reminders
    overdue_payments = Payment.objects.filter(
        status='pending',
        due_date__lt=timezone.now()
    )
    
    for payment in overdue_payments:
        send_payment_reminder.delay(payment.id)
    
    messages.success(request, f'{overdue_payments.count()} reminders queued')
    return redirect('admin_dashboard')
```

---

### 4. Static File Optimization

**Asset Compression:**

```bash
# Install compression tools
npm install --save-dev webpack webpack-cli terser-webpack-plugin css-minimizer-webpack-plugin

# webpack.config.js
const TerserPlugin = require('terser-webpack-plugin');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');

module.exports = {
  mode: 'production',
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin(),
      new CssMinimizerPlugin(),
    ],
  },
};
```

**Image Optimization:**

```python
# Use WebP format
from PIL import Image

def convert_to_webp(image_path):
    img = Image.open(image_path)
    webp_path = image_path.rsplit('.', 1)[0] + '.webp'
    img.save(webp_path, 'WEBP', quality=85, method=6)
    return webp_path

# Generate multiple sizes (responsive images)
def generate_thumbnails(image_path):
    img = Image.open(image_path)
    sizes = [(320, 240), (640, 480), (1280, 960), (1920, 1080)]
    
    for width, height in sizes:
        thumb = img.copy()
        thumb.thumbnail((width, height))
        thumb_path = f"{image_path.rsplit('.', 1)[0]}_{width}x{height}.webp"
        thumb.save(thumb_path, 'WEBP', quality=85)
```

**Lazy Loading:**

```html
<!-- Lazy load images -->
<img src="placeholder.jpg" 
     data-src="actual-image.jpg" 
     loading="lazy" 
     alt="Vehicle document">

<script>
// Intersection Observer for lazy loading
const images = document.querySelectorAll('img[data-src]');
const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
        }
    });
});

images.forEach(img => imageObserver.observe(img));
</script>
```

---

### 5. Rate Limiting

**Django Ratelimit:**

```python
from django_ratelimit.decorators import ratelimit

# Limit by IP address
@ratelimit(key='ip', rate='100/h', method='POST')
def api_endpoint(request):
    # API logic
    pass

# Limit by user
@ratelimit(key='user', rate='10/m', method='POST')
def ocr_upload(request):
    # OCR upload logic
    pass

# Limit by user or IP
@ratelimit(key='user_or_ip', rate='50/h')
def search_vehicles(request):
    # Search logic
    pass

# Custom rate limit key
@ratelimit(key=lambda g, r: r.user.email, rate='5/m')
def send_email(request):
    # Email sending logic
    pass
```

**Redis-based Rate Limiting:**

```python
from django.core.cache import cache
from django.http import HttpResponseForbidden

def rate_limit(key, limit, period):
    """
    Rate limit using Redis
    key: unique identifier (user_id, ip, etc.)
    limit: max requests
    period: time window in seconds
    """
    cache_key = f'rate_limit_{key}'
    current = cache.get(cache_key, 0)
    
    if current >= limit:
        return False
    
    cache.set(cache_key, current + 1, period)
    return True

# Usage in view
def api_view(request):
    user_id = request.user.id
    if not rate_limit(user_id, limit=100, period=3600):
        return HttpResponseForbidden('Rate limit exceeded')
    
    # Process request
    return JsonResponse({'status': 'success'})
```

---

## Security Considerations

### Network Security
- VPC with private subnets for databases
- Security groups with minimal access
- WAF (Web Application Firewall)
- DDoS protection via CloudFlare
- Intrusion detection system (IDS)

### Application Security
- HTTPS only (TLS 1.3)
- CSRF protection enabled
- XSS protection headers
- SQL injection prevention (ORM)
- Rate limiting on sensitive endpoints
- Input validation and sanitization
- Content Security Policy (CSP)

### Data Security
- Encryption at rest (database, S3)
- Encryption in transit (TLS)
- Regular security audits
- Automated vulnerability scanning
- Secrets management (AWS Secrets Manager)
- PII data masking in logs

### Access Control
- Role-based access control (RBAC)
- Multi-factor authentication (MFA)
- API key rotation
- Audit logging for sensitive operations
- Principle of least privilege

---

## Backup & Disaster Recovery

### Database Backups
- Automated daily snapshots (3 AM UTC)
- Point-in-time recovery (PITR)
- Cross-region replication
- Retention: 30 days
- Monthly archival to S3 Glacier
- Backup testing: Monthly

### Application Backups
- Infrastructure as Code (Terraform/CloudFormation)
- Configuration in version control (Git)
- Docker images in registry (ECR)
- Automated deployment pipelines (CI/CD)

### Recovery Procedures
- RTO (Recovery Time Objective): 1 hour
- RPO (Recovery Point Objective): 15 minutes
- Documented runbooks
- Regular disaster recovery drills (quarterly)
- Failover testing

---

## Scaling Roadmap

### Phase 1: Current (20K users)
- 8-12 application servers
- 1 primary + 2 read replicas
- 3-node Redis cluster
- 4-6 Celery workers
- Single region deployment

### Phase 2: Growth (50K users)
- 16-24 application servers
- 1 primary + 4 read replicas
- 5-node Redis cluster
- 8-10 Celery workers
- Database sharding consideration
- Multi-region CDN

### Phase 3: Scale (100K+ users)
- Multi-region deployment
- Database sharding by geography
- Microservices architecture
- Kubernetes orchestration
- Advanced caching (Varnish)
- Message queue (RabbitMQ/Kafka)

---

## Monitoring Checklist

### Daily Monitoring
- [ ] Error rate < 0.1%
- [ ] Response time p95 < 500ms
- [ ] Database CPU < 70%
- [ ] Cache hit ratio > 80%
- [ ] Queue length < 100
- [ ] Disk usage < 80%
- [ ] No critical alerts

### Weekly Review
- [ ] Slow query analysis
- [ ] Disk usage trends
- [ ] Cost analysis
- [ ] Security alerts review
- [ ] Backup verification
- [ ] Performance trends

### Monthly Review
- [ ] Capacity planning
- [ ] Performance optimization
- [ ] Security audit
- [ ] Disaster recovery test
- [ ] Cost optimization
- [ ] Infrastructure updates

---

## Deployment Strategy

### Blue-Green Deployment
1. Deploy new version to "green" environment
2. Run automated tests
3. Switch load balancer to green (10% traffic)
4. Monitor for 30 minutes
5. Gradually increase to 100%
6. Keep blue as rollback option for 24 hours

### Rolling Deployment
1. Deploy to 25% of servers
2. Monitor for 15 minutes
3. Deploy to 50% of servers
4. Monitor for 15 minutes
5. Deploy to 100% of servers
6. Total deployment time: ~45 minutes

### Database Migrations
- Run migrations during low-traffic periods (2-4 AM)
- Use backward-compatible migrations
- Test on staging environment first
- Have rollback plan ready
- Monitor replication lag during migration

---

## Data Migration Strategy (528K Vehicles)

### Initial Data Import

**Scenario:** Importing existing 528,000 vehicle records into the system

**Migration Approach:**

```
Phase 1: Preparation (Week 1)
┌────────────────────────────────────────────────────────┐
│ 1. Data Cleanup & Validation                          │
│    • Normalize plate numbers                          │
│    • Validate owner information                       │
│    • Check for duplicates                             │
│    • Prepare CSV/Excel files                          │
│                                                        │
│ 2. Database Preparation                               │
│    • Create tables with indexes                       │
│    • Set up partitioning                              │
│    • Configure connection pooling                     │
│    • Disable non-essential triggers                   │
└────────────────────────────────────────────────────────┘

Phase 2: Bulk Import (Week 2)
┌────────────────────────────────────────────────────────┐
│ 1. Import in Batches                                  │
│    • Batch size: 10,000 records                       │
│    • Total batches: 53 batches                        │
│    • Time per batch: ~5-10 minutes                    │
│    • Total time: 4-9 hours                            │
│                                                        │
│ 2. Import Order                                       │
│    a. Users/Owners (300K records) - 3 hours           │
│    b. Vehicles (528K records) - 5 hours               │
│    c. Historical Payments (optional) - 2 hours        │
│                                                        │
│ 3. Validation After Each Batch                        │
│    • Count records                                    │
│    • Check data integrity                             │
│    • Log errors                                       │
└────────────────────────────────────────────────────────┘

Phase 3: Post-Import (Week 3)
┌────────────────────────────────────────────────────────┐
│ 1. Index Rebuilding                                   │
│    • Rebuild all indexes - 2 hours                    │
│    • Analyze tables - 30 minutes                      │
│    • Update statistics - 15 minutes                   │
│                                                        │
│ 2. Data Verification                                  │
│    • Run validation queries                           │
│    • Check relationships                              │
│    • Verify totals                                    │
│    • Sample data review                               │
│                                                        │
│ 3. Performance Testing                                │
│    • Test common queries                              │
│    • Load testing                                     │
│    • Optimize slow queries                            │
└────────────────────────────────────────────────────────┘
```

**Django Management Command for Import:**

```python
# vehicles/management/commands/import_vehicles.py
from django.core.management.base import BaseCommand
from django.db import transaction
from vehicles.models import Vehicle, Owner
import csv
from tqdm import tqdm

class Command(BaseCommand):
    help = 'Import vehicles from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to CSV file')
        parser.add_argument('--batch-size', type=int, default=10000)

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        batch_size = options['batch_size']
        
        vehicles_to_create = []
        total_imported = 0
        errors = []
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            total_rows = sum(1 for _ in open(csv_file)) - 1  # Exclude header
            
            with tqdm(total=total_rows, desc="Importing vehicles") as pbar:
                for row in reader:
                    try:
                        # Get or create owner
                        owner, _ = Owner.objects.get_or_create(
                            name=row['owner_name'],
                            defaults={
                                'email': row.get('owner_email', ''),
                                'phone': row.get('owner_phone', ''),
                            }
                        )
                        
                        # Prepare vehicle
                        vehicle = Vehicle(
                            plate_number=row['plate_number'].upper().strip(),
                            owner=owner,
                            vehicle_type=row['vehicle_type'],
                            brand=row.get('brand', ''),
                            model=row.get('model', ''),
                            year=row.get('year'),
                            status='active',
                        )
                        vehicles_to_create.append(vehicle)
                        
                        # Bulk create when batch is full
                        if len(vehicles_to_create) >= batch_size:
                            with transaction.atomic():
                                Vehicle.objects.bulk_create(
                                    vehicles_to_create,
                                    ignore_conflicts=True
                                )
                            total_imported += len(vehicles_to_create)
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'Imported {total_imported} vehicles'
                                )
                            )
                            vehicles_to_create = []
                        
                        pbar.update(1)
                        
                    except Exception as e:
                        errors.append({
                            'row': row,
                            'error': str(e)
                        })
                        pbar.update(1)
                        continue
                
                # Import remaining vehicles
                if vehicles_to_create:
                    with transaction.atomic():
                        Vehicle.objects.bulk_create(
                            vehicles_to_create,
                            ignore_conflicts=True
                        )
                    total_imported += len(vehicles_to_create)
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Successfully imported {total_imported} vehicles'
            )
        )
        
        if errors:
            self.stdout.write(
                self.style.WARNING(
                    f'⚠ {len(errors)} errors occurred'
                )
            )
            # Write errors to file
            with open('import_errors.log', 'w') as f:
                for error in errors:
                    f.write(f"{error}\n")

# Usage:
# python manage.py import_vehicles vehicles.csv --batch-size=10000
```

**PostgreSQL COPY Command (Faster Alternative):**

```python
# For maximum speed, use PostgreSQL COPY
from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fast import using PostgreSQL COPY'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Import owners
            cursor.execute("""
                COPY owners(name, email, phone, created_at)
                FROM '/tmp/owners.csv'
                DELIMITER ','
                CSV HEADER;
            """)
            
            # Import vehicles
            cursor.execute("""
                COPY vehicles(plate_number, owner_id, vehicle_type, 
                             brand, model, year, status, created_at)
                FROM '/tmp/vehicles.csv'
                DELIMITER ','
                CSV HEADER;
            """)
            
            # Rebuild indexes
            cursor.execute("REINDEX TABLE vehicles;")
            cursor.execute("ANALYZE vehicles;")
        
        self.stdout.write(self.style.SUCCESS('Import completed!'))

# This method can import 528K records in 10-15 minutes
```

**Import Performance Estimates:**

| Method | Speed | Time for 528K | Pros | Cons |
|--------|-------|---------------|------|------|
| Django ORM (single) | 100/sec | 88 min | Simple, validated | Very slow |
| Django bulk_create | 5,000/sec | 1.8 min | Good balance | Some overhead |
| PostgreSQL COPY | 50,000/sec | 10 sec | Very fast | Less validation |
| Celery parallel | 10,000/sec | 53 sec | Scalable | Complex setup |

**Recommended:** Use Django bulk_create with batch size of 10,000 for good balance of speed and data validation.

---

## Ongoing Data Management

### Daily Operations

**New Vehicle Registrations:**
- Expected: 50-200 new vehicles/day
- Processing time: < 1 second per vehicle
- Validation: Automatic duplicate detection
- Notification: Real-time to admin dashboard

**Data Cleanup Tasks:**

```python
# Run nightly via cron
# vehicles/management/commands/cleanup_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Nightly data cleanup tasks'

    def handle(self, *args, **options):
        # 1. Remove old temporary files
        old_date = timezone.now() - timedelta(days=7)
        deleted = TempFile.objects.filter(created_at__lt=old_date).delete()
        self.stdout.write(f'Deleted {deleted[0]} old temp files')
        
        # 2. Archive old audit logs
        archive_date = timezone.now() - timedelta(days=90)
        AuditLog.objects.filter(created_at__lt=archive_date).update(
            archived=True
        )
        
        # 3. Update materialized views
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute('REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;')
        
        # 4. Vacuum analyze (weekly)
        if timezone.now().weekday() == 0:  # Monday
            with connection.cursor() as cursor:
                cursor.execute('VACUUM ANALYZE vehicles;')
                cursor.execute('VACUUM ANALYZE payments;')
        
        self.stdout.write(self.style.SUCCESS('Cleanup completed!'))
```

### Search Optimization for 528K Records

**Full-Text Search Setup:**

```python
# vehicles/models.py
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20, db_index=True)
    owner_name = models.CharField(max_length=200)
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
        ]

# Update search vector
from django.contrib.postgres.search import SearchVector

Vehicle.objects.update(
    search_vector=SearchVector('plate_number', 'owner_name')
)

# Search usage
from django.contrib.postgres.search import SearchQuery, SearchRank

query = SearchQuery('ABC123')
vehicles = Vehicle.objects.annotate(
    rank=SearchRank(F('search_vector'), query)
).filter(search_vector=query).order_by('-rank')[:10]

# Search time: < 50ms for 528K records
```

**Elasticsearch Alternative (for complex search):**

```python
# If you need advanced search features
from elasticsearch_dsl import Document, Text, Keyword, Integer

class VehicleDocument(Document):
    plate_number = Keyword()
    owner_name = Text()
    vehicle_type = Keyword()
    brand = Text()
    model = Text()
    year = Integer()
    
    class Index:
        name = 'vehicles'
    
    def save(self, **kwargs):
        return super().save(**kwargs)

# Index all vehicles (one-time)
for vehicle in Vehicle.objects.iterator(chunk_size=1000):
    doc = VehicleDocument(
        meta={'id': vehicle.id},
        plate_number=vehicle.plate_number,
        owner_name=vehicle.owner_name,
        # ... other fields
    )
    doc.save()

# Search (very fast, < 10ms)
s = VehicleDocument.search().query("match", owner_name="John")
results = s[:10].execute()
```

---

## Conclusion

This architecture provides a robust, scalable foundation for supporting 20,000 concurrent users with room to grow. Key success factors:

1. **Horizontal scaling** - Add more servers as needed
2. **Database optimization** - Read replicas and caching reduce load
3. **Async processing** - Offload heavy tasks to Celery workers
4. **Monitoring** - Proactive issue detection and resolution
5. **Cost efficiency** - Right-sized resources with auto-scaling

The architecture can scale to 50K+ users with incremental upgrades. Start with the minimum viable infrastructure and scale based on actual metrics and user growth.

---

## Next Steps

1. **Load Testing**
   - Use tools like Locust, JMeter, or k6
   - Simulate 20K concurrent users
   - Identify bottlenecks
   - Validate auto-scaling

2. **Staging Environment**
   - Mirror production architecture
   - Test deployments
   - Validate performance
   - Practice disaster recovery

3. **Documentation**
   - Runbooks for common operations
   - Incident response procedures
   - Architecture diagrams (keep updated)
   - Onboarding guides

4. **Training**
   - DevOps team on infrastructure management
   - Development team on optimization techniques
   - Support team on monitoring and alerting
   - Regular knowledge sharing sessions

---

**Document Owner:** DevOps Team  
**Review Cycle:** Quarterly  
**Last Updated:** November 7, 2025  
**Next Review:** February 7, 2026
