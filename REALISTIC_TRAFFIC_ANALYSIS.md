# Realistic Traffic Analysis - Tax Collection Platform

**Total Vehicles:** 528,000  
**Analysis Date:** November 7, 2025

---

## User Behavior Patterns

### User Types

1. **Vehicle Owners (Citizens)**
   - Register vehicles
   - Pay taxes
   - Check payment status
   - Download receipts

2. **Tax Collection Agents**
   - Scan QR codes for verification
   - Process payments
   - Verify vehicle documents

3. **Administrators**
   - Manage system
   - Generate reports
   - Monitor payments

---

## Traffic Pattern Analysis

### Monthly Payment Cycle

```
Assumption: Most people pay at the beginning of the month

Month Timeline:
┌─────────────────────────────────────────────────────────────────┐
│ Days 1-5:  PEAK PERIOD (60% of monthly traffic)                 │
│ Days 6-15: HIGH PERIOD (25% of monthly traffic)                 │
│ Days 16-30: NORMAL PERIOD (15% of monthly traffic)              │
└─────────────────────────────────────────────────────────────────┘

Annual Pattern:
┌─────────────────────────────────────────────────────────────────┐
│ January-March:   HIGH (Tax deadline season) - 40% of annual     │
│ April-June:      MEDIUM - 25% of annual                         │
│ July-September:  MEDIUM - 20% of annual                         │
│ October-December: NORMAL - 15% of annual                        │
└─────────────────────────────────────────────────────────────────┘
```

### Realistic User Calculations

**Total Vehicles:** 528,000

**Assumption 1: Not everyone pays online**
- Online payment adoption: 70% (368,000 vehicles)
- In-person payment: 30% (160,000 vehicles)

**Assumption 2: Payment frequency**
- Annual payment: 1 time per year
- Average session: 10 minutes
- Pages per session: 5-8 pages

**Assumption 3: Peak day traffic (Day 1-5 of month)**
- 60% of monthly payers = 60% × (368,000 ÷ 12) = 18,400 users/day
- Spread over 12 hours (8 AM - 8 PM) = 1,533 users/hour
- Average session: 10 minutes
- **Concurrent users during peak hour: 1,533 × (10/60) = 256 concurrent users**

**Assumption 4: Tax agents scanning QR codes**
- Number of agents: 50-100 agents
- Each agent scans: 20-30 vehicles/hour during peak
- Agent session time: Continuous (8 hours)
- **Concurrent agents: 50-100**

---

## Realistic Concurrent User Estimates

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CONCURRENT USER ESTIMATES                             │
└─────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════╗
║ Scenario                │ Citizens │ Agents │ Admins │ Total Concurrent ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Normal Day              │    50    │   20   │    5   │      75         ║
║ (Days 16-30)            │          │        │        │                 ║
╟───────────────────────────────────────────────────────────────────────╢
║ Busy Day                │   150    │   40   │   10   │     200         ║
║ (Days 6-15)             │          │        │        │                 ║
╟───────────────────────────────────────────────────────────────────────╢
║ Peak Day                │   300    │   80   │   20   │     400         ║
║ (Days 1-5 of month)     │          │        │        │                 ║
╟───────────────────────────────────────────────────────────────────────╢
║ Extreme Peak            │   500    │  100   │   30   │     630         ║
║ (Day 1, Tax deadline)   │          │        │        │                 ║
╟───────────────────────────────────────────────────────────────────────╢
║ Marketing Campaign      │   800    │  100   │   30   │     930         ║
║ (Special promotion)     │          │        │        │                 ║
╚═══════════════════════════════════════════════════════════════════════╝

Recommended Design Capacity: 1,000-1,500 concurrent users
Safety Buffer: 2,000 concurrent users (for unexpected spikes)
```

---

## Detailed Traffic Breakdown

### Peak Day Analysis (First 5 days of month)

```
Time Distribution (Peak Day):
┌─────────────────────────────────────────────────────────────────┐
│ Time Period    │ Citizens │ Agents │ Total │ % of Day          │
├────────────────┼──────────┼────────┼───────┼───────────────────┤
│ 00:00 - 06:00  │    10    │    0   │   10  │  2% (Night)       │
│ 06:00 - 08:00  │    30    │   10   │   40  │  8% (Early)       │
│ 08:00 - 10:00  │   150    │   50   │  200  │ 30% (Morning Peak)│
│ 10:00 - 12:00  │   250    │   80   │  330  │ 50% (Peak Hour)   │
│ 12:00 - 14:00  │   200    │   60   │  260  │ 40% (Lunch)       │
│ 14:00 - 16:00  │   180    │   70   │  250  │ 38% (Afternoon)   │
│ 16:00 - 18:00  │   220    │   80   │  300  │ 45% (Evening Peak)│
│ 18:00 - 20:00  │   150    │   40   │  190  │ 28% (Late)        │
│ 20:00 - 24:00  │    50    │    5   │   55  │  8% (Night)       │
└─────────────────────────────────────────────────────────────────┘

Peak Hour: 10:00 - 12:00 with 330 concurrent users
```

### Agent Activity Pattern

```
Tax Collection Agent Workflow:
┌─────────────────────────────────────────────────────────────────┐
│ Activity                    │ Time/Action │ Frequency           │
├─────────────────────────────┼─────────────┼─────────────────────┤
│ Scan QR Code                │   5 sec     │ 20-30 per hour      │
│ Verify Vehicle Info         │  10 sec     │ 20-30 per hour      │
│ Process Payment             │  30 sec     │ 15-20 per hour      │
│ Print Receipt               │  10 sec     │ 15-20 per hour      │
│ Handle Issues               │ 2-5 min     │ 2-3 per hour        │
└─────────────────────────────────────────────────────────────────┘

Agent Concurrent Sessions:
• Each agent: 1 active session (continuous)
• Peak agents online: 80-100 agents
• Each agent generates: 3-5 requests per minute
• Total agent requests: 240-500 requests/minute
```

---

## Request Load Analysis

### Requests Per Second (RPS)

```
╔═══════════════════════════════════════════════════════════════════════╗
║ Scenario          │ Concurrent │ Avg Requests │ Total RPS │ Peak RPS  ║
║                   │   Users    │  per User    │           │           ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Normal Day        │     75     │    0.5/sec   │    38     │    75     ║
╟───────────────────────────────────────────────────────────────────────╢
║ Busy Day          │    200     │    0.5/sec   │   100     │   200     ║
╟───────────────────────────────────────────────────────────────────────╢
║ Peak Day          │    400     │    0.5/sec   │   200     │   400     ║
╟───────────────────────────────────────────────────────────────────────╢
║ Extreme Peak      │    630     │    0.5/sec   │   315     │   630     ║
╟───────────────────────────────────────────────────────────────────────╢
║ Design Capacity   │  1,500     │    0.5/sec   │   750     │ 1,500     ║
╚═══════════════════════════════════════════════════════════════════════╝

Note: 0.5 requests/sec = 1 request every 2 seconds (typical user behavior)
```

### Database Query Load

```
╔═══════════════════════════════════════════════════════════════════════╗
║ Scenario          │ Total RPS │ Queries/Req │ DB Queries/Sec         ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Normal Day        │    38     │      5      │      190               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Busy Day          │   100     │      5      │      500               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Peak Day          │   200     │      5      │    1,000               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Extreme Peak      │   315     │      5      │    1,575               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Design Capacity   │   750     │      5      │    3,750               ║
╚═══════════════════════════════════════════════════════════════════════╝

With caching (80% hit rate):
• Peak Day: 200 queries/sec (80% reduction)
• Design Capacity: 750 queries/sec
```

---

## Revised Infrastructure Requirements

### Right-Sized Architecture for 400-1,500 Concurrent Users

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REVISED INFRASTRUCTURE                                │
└─────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════╗
║ Component              │ Original (20K) │ Revised (1.5K) │ Savings    ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Django App Servers     │    8-12        │      3-4       │   -60%     ║
║ (c5.2xlarge)           │                │                │            ║
╟───────────────────────────────────────────────────────────────────────╢
║ Celery Workers         │     4-6        │      2-3       │   -50%     ║
║ (c5.xlarge)            │                │                │            ║
╟───────────────────────────────────────────────────────────────────────╢
║ PostgreSQL Primary     │ db.r5.4xlarge  │ db.r5.2xlarge  │   -50%     ║
╟───────────────────────────────────────────────────────────────────────╢
║ Read Replicas          │     2-3        │      1-2       │   -50%     ║
║ (db.r5.2xlarge)        │                │                │            ║
╟───────────────────────────────────────────────────────────────────────╢
║ Redis Cluster          │    3-5 nodes   │    2-3 nodes   │   -40%     ║
║ (cache.r5.large)       │                │                │            ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### Capacity Planning

```
╔═══════════════════════════════════════════════════════════════════════╗
║ Metric                 │ Per Server │ Total (4 servers) │ Utilization ║
╠═══════════════════════════════════════════════════════════════════════╣
║ Concurrent Users       │    375     │      1,500        │    27%      ║
║ (at peak)              │            │                   │ (400/1500)  ║
╟───────────────────────────────────────────────────────────────────────╢
║ Requests/Second        │    188     │        750        │    27%      ║
║ (at peak)              │            │                   │ (200/750)   ║
╟───────────────────────────────────────────────────────────────────────╢
║ Database Queries/Sec   │    938     │      3,750        │    27%      ║
║ (at peak, no cache)    │            │                   │ (1000/3750) ║
╚═══════════════════════════════════════════════════════════════════════╝

Conclusion: System has 3-4x capacity headroom for growth
```

---

## Revised Cost Estimate

### Monthly Infrastructure Costs (Optimized for Actual Load)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    REVISED MONTHLY COSTS                                 │
└─────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════╗
║ Component                    │ Quantity │ Unit Price │ Monthly Cost   ║
╠═══════════════════════════════════════════════════════════════════════╣
║ COMPUTE RESOURCES                                                      ║
╟───────────────────────────────────────────────────────────────────────╢
║ Django App Servers           │    4     │   $150     │    $600       ║
║ (c5.2xlarge)                 │          │            │               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Celery Workers               │    2     │   $100     │    $200       ║
║ (c5.xlarge)                  │          │            │               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Load Balancers               │    1     │    $25     │     $25       ║
╟───────────────────────────────────────────────────────────────────────╢
║ Subtotal                     │          │            │    $825       ║
╠═══════════════════════════════════════════════════════════════════════╣
║ DATABASE RESOURCES                                                     ║
╟───────────────────────────────────────────────────────────────────────╢
║ PostgreSQL Primary           │    1     │   $600     │    $600       ║
║ (db.r5.2xlarge)              │          │            │               ║
╟───────────────────────────────────────────────────────────────────────╢
║ PostgreSQL Read Replica      │    1     │   $400     │    $400       ║
║ (db.r5.2xlarge)              │          │            │               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Database Backup Storage      │  100GB   │  $0.10/GB  │     $10       ║
╟───────────────────────────────────────────────────────────────────────╢
║ Subtotal                     │          │            │  $1,010       ║
╠═══════════════════════════════════════════════════════════════════════╣
║ CACHING & QUEUE                                                        ║
╟───────────────────────────────────────────────────────────────────────╢
║ Redis Cluster                │    2     │   $133     │    $266       ║
║ (cache.r5.large)             │  nodes   │            │               ║
╟───────────────────────────────────────────────────────────────────────╢
║ Subtotal                     │          │            │    $266       ║
╠═══════════════════════════════════════════════════════════════════════╣
║ STORAGE & FILES                                                        ║
╟───────────────────────────────────────────────────────────────────────╢
║ S3 Storage (3TB)             │   3 TB   │  $0.023/GB │     $70       ║
║ S3 Requests                  │   ~500K  │  $0.005/1K │      $3       ║
║ S3 Glacier (Backups)         │  1.4 TB  │  $0.004/GB │      $6       ║
║ EBS Volumes                  │  400 GB  │  $0.10/GB  │     $40       ║
╟───────────────────────────────────────────────────────────────────────╢
║ Subtotal                     │          │            │    $119       ║
╠═══════════════════════════════════════════════════════════════════════╣
║ NETWORK & CDN                                                          ║
╟───────────────────────────────────────────────────────────────────────╢
║ CloudFront CDN               │   2 TB   │  $0.085/GB │    $170       ║
║ Data Transfer Out            │   1 TB   │  $0.09/GB  │     $90       ║
║ CloudFlare (DDoS)            │    1     │    $100    │    $100       ║
╟───────────────────────────────────────────────────────────────────────╢
║ Subtotal                     │          │            │    $360       ║
╠═══════════════════════════════════════════════════════════════════════╣
║ MONITORING & SECURITY                                                  ║
╟───────────────────────────────────────────────────────────────────────╢
║ CloudWatch                   │    -     │     -      │     $50       ║
║ DataDog / New Relic          │    1     │    $100    │    $100       ║
║ Sentry                       │    1     │     $29    │     $29       ║
║ AWS WAF                      │    1     │     $30    │     $30       ║
╟───────────────────────────────────────────────────────────────────────╢
║ Subtotal                     │          │            │    $209       ║
╠═══════════════════════════════════════════════════════════════════════╣
║ TOTAL MONTHLY COST           │          │            │  $2,789       ║
╠═══════════════════════════════════════════════════════════════════════╣
║ With Reserved Instances (1Y) │          │            │  $2,100       ║
║ With Reserved Instances (3Y) │          │            │  $1,800       ║
╚═══════════════════════════════════════════════════════════════════════╝

SAVINGS vs Original Estimate:
• Standard: $5,466 → $2,789 (49% reduction)
• Optimized: $3,200 → $1,800 (44% reduction)
```

---

## Scaling Strategy

### Auto-Scaling Configuration

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AUTO-SCALING RULES                                    │
└─────────────────────────────────────────────────────────────────────────┘

Application Servers:
├─ Minimum: 2 servers (always running)
├─ Normal: 3 servers (days 16-30)
├─ Busy: 4 servers (days 6-15)
├─ Peak: 5-6 servers (days 1-5)
└─ Maximum: 8 servers (emergency)

Scaling Triggers:
├─ Scale UP when:
│  ├─ CPU > 70% for 5 minutes
│  ├─ Memory > 80% for 5 minutes
│  └─ Request queue > 100
│
└─ Scale DOWN when:
   ├─ CPU < 30% for 15 minutes
   ├─ Memory < 50% for 15 minutes
   └─ Request queue < 20

Cost Impact:
├─ Normal days (25 days): 3 servers × $150 = $3,750/month
├─ Busy days (4 days): 4 servers × $150 = $600/month
├─ Peak days (1 day): 6 servers × $150 = $300/month
└─ Average: $4,650/month ÷ 30 days = $155/day
```

---

## Recommendations

### Phase 1: Launch (Months 1-3)

```
Configuration:
├─ App Servers: 3 (c5.2xlarge)
├─ Celery Workers: 2 (c5.xlarge)
├─ Database: 1 Primary + 1 Replica (db.r5.2xlarge)
├─ Redis: 2 nodes (cache.r5.large)
└─ Monthly Cost: ~$2,500

Expected Load:
├─ Concurrent Users: 100-300
├─ Peak RPS: 150-200
└─ Database Queries: 750-1,000/sec
```

### Phase 2: Growth (Months 4-12)

```
Configuration:
├─ App Servers: 4 with auto-scaling to 6
├─ Celery Workers: 2-3
├─ Database: 1 Primary + 1-2 Replicas
├─ Redis: 2-3 nodes
└─ Monthly Cost: ~$2,100 (with reserved instances)

Expected Load:
├─ Concurrent Users: 300-500
├─ Peak RPS: 250-400
└─ Database Queries: 1,250-2,000/sec
```

### Phase 3: Stable (Year 2+)

```
Configuration:
├─ App Servers: 4-5 with auto-scaling to 8
├─ Celery Workers: 3
├─ Database: 1 Primary + 2 Replicas
├─ Redis: 3 nodes
└─ Monthly Cost: ~$1,800 (with 3-year reserved)

Expected Load:
├─ Concurrent Users: 400-630
├─ Peak RPS: 300-500
└─ Database Queries: 1,500-2,500/sec
```

---

## Key Insights

1. **Realistic Peak Load: 400-630 concurrent users** (not 20,000)
   - 300-500 citizens
   - 80-100 agents
   - 20-30 admins

2. **Traffic is Seasonal**
   - Peak: First 5 days of month
   - Peak hours: 10 AM - 12 PM, 4 PM - 6 PM
   - Low traffic: Nights and weekends

3. **Agent Activity is Significant**
   - 80-100 agents during peak
   - Continuous sessions (8 hours)
   - High request frequency (QR scanning)

4. **Cost Savings: 49% reduction**
   - Original estimate: $5,466/month
   - Realistic estimate: $2,789/month
   - Optimized: $1,800/month

5. **Capacity Headroom: 3-4x**
   - Design for 1,500 concurrent users
   - Current peak: 400-630 users
   - Room for 2-3x growth

---

## Monitoring Priorities

```
Critical Metrics to Watch:
├─ Concurrent users (real-time)
├─ Response time (< 500ms target)
├─ Error rate (< 0.1% target)
├─ Database CPU (< 70% target)
├─ Cache hit ratio (> 80% target)
└─ Queue length (< 50 target)

Alert Thresholds:
├─ Concurrent users > 800 (approaching capacity)
├─ Response time > 1 second (performance issue)
├─ Error rate > 1% (critical issue)
├─ Database CPU > 85% (scale up needed)
└─ Queue length > 100 (backlog building)
```

---

**Conclusion:** The system should be designed for **1,000-1,500 concurrent users** with auto-scaling, not 20,000. This provides adequate capacity for peak loads while keeping costs reasonable at **$1,800-2,800/month**.
