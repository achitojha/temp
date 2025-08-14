# Dropbox Architecture Interview Problems - Complete Solutions

This document contains detailed solutions for all commonly asked Dropbox architecture interview problems, including functional/non-functional requirements, data models, component diagrams, and key flows.

## Table of Contents
1. [File Storage and Synchronization Service (Dropbox-like)](#problem-1)
2. [Database System with Low Latency](#problem-2)
3. [IP Blocking System](#problem-3)
4. [Voting System](#problem-4)
5. [E-commerce System for Top-Selling Products](#problem-5)
6. [Online Bookstore](#problem-6)
7. [Building Occupancy System](#problem-7)
8. [Image Upload and Tagging System](#problem-8)
9. [Notification Service](#problem-9)
10. [Chatbot Service](#problem-10)
11. [Scheduler Service](#problem-11)
12. [Folder Access System](#problem-12)
13. [Scalable Web Application](#problem-13)
14. [Secure File Sharing Feature](#problem-14)

---

## Problem 1: File Storage and Synchronization Service (Dropbox-like) {#problem-1}

### Problem Statement
Design a file storage and synchronization service like Dropbox that allows users to upload, download, and synchronize files across multiple devices with features like file versioning, sharing, and offline access.

### Functional Requirements
1. **File Operations**
   - Upload files from any device
   - Download files to any device
   - Delete files and folders
   - Create folder hierarchies

2. **Synchronization**
   - Real-time sync across all user devices
   - Conflict resolution for simultaneous edits
   - Offline file access and sync when back online

3. **File Versioning**
   - Maintain file version history
   - Restore previous versions
   - View version diffs

4. **Sharing & Collaboration**
   - Share files/folders with other users
   - Set permissions (read, write, admin)
   - Public link sharing with expiration

5. **User Management**
   - User registration and authentication
   - Account management
   - Storage quota management

### Non-Functional Requirements
1. **Scalability**
   - Support 500M+ users
   - Handle 100M+ files
   - Support files up to 10GB each

2. **Performance**
   - Upload/download latency < 200ms for small files
   - 99.9% uptime availability
   - Sync propagation within 1 second

3. **Consistency**
   - Strong consistency for metadata
   - Eventual consistency for file content across devices

4. **Security**
   - End-to-end encryption for file content
   - Secure authentication (OAuth, 2FA)
   - Data integrity validation

5. **Storage Efficiency**
   - File deduplication
   - Compression
   - Delta sync for large files

### Data Model (UML)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      User       │    │     Device      │    │    FileNode     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ user_id (PK)    │    │ device_id (PK)  │    │ node_id (PK)    │
│ email           │◄───┤ user_id (FK)    │    │ parent_id (FK)  │
│ password_hash   │    │ device_name     │    │ name            │
│ created_at      │    │ device_type     │    │ type (file/dir) │
│ storage_used    │    │ last_sync       │    │ owner_id (FK)   │
│ storage_quota   │    │ is_active       │    │ created_at      │
│ subscription    │    │ auth_token      │    │ modified_at     │
└─────────────────┘    └─────────────────┘    │ size            │
                                              │ is_deleted      │
┌─────────────────┐    ┌─────────────────┐    └─────────────────┘
│   FileVersion   │    │  FileBlock      │            │
├─────────────────┤    ├─────────────────┤            │
│ version_id (PK) │    │ block_id (PK)   │            │
│ node_id (FK)    │◄───┤ version_id (FK) │            │
│ version_number  │    │ block_hash      │            │
│ file_hash       │    │ block_data      │            │
│ created_at      │    │ block_size      │            │
│ created_by      │    │ compression     │            │
│ commit_message  │    └─────────────────┘            │
│ size            │                                   │
└─────────────────┘    ┌─────────────────┐            │
                       │ SharedPermission│            │
┌─────────────────┐    ├─────────────────┤            │
│   SyncRecord    │    │ permission_id   │            │
├─────────────────┤    │ node_id (FK)    │◄───────────┘
│ sync_id (PK)    │    │ user_id (FK)    │
│ device_id (FK)  │    │ permission_type │
│ node_id (FK)    │    │ granted_by      │
│ version_id (FK) │    │ granted_at      │
│ sync_status     │    │ expires_at      │
│ last_sync       │    └─────────────────┘
│ conflict_flag   │
└─────────────────┘
```

### Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                   Client Tier                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│  │   Web App   │  │ Mobile App  │  │Desktop App  │  │   API SDK   │           │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘           │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                Load Balancer                                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  API Gateway                                     │
│                          (Authentication, Rate Limiting)                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               Application Tier                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │    Auth     │ │    File     │ │    Sync     │ │   Sharing   │ │ Notification││
│ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │  Service    ││
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                        │                                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │
│ │  Metadata   │ │   Version   │ │Compression/ │ │  Analytics  │                │
│ │  Service    │ │  Service    │ │Dedup Service│ │  Service    │                │
│ │             │ │             │ │             │ │             │                │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                Message Queue                                     │
│                              (Kafka/RabbitMQ)                                   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  Data Tier                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐│
│ │   User DB   │ │ Metadata DB │ │  Version DB │ │   Cache     │ │   Search    ││
│ │ (PostgreSQL)│ │ (PostgreSQL)│ │ (PostgreSQL)│ │   (Redis)   │ │(Elasticsearch│
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘│
│                                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                          Object Storage                                     │ │
│ │                         (AWS S3/Azure Blob)                                │ │
│ │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐        │ │
│ │  │   Region 1  │ │   Region 2  │ │   Region 3  │ │   CDN Cache │        │ │
│ │  │   Primary   │ │   Replica   │ │   Replica   │ │ (CloudFront)│        │ │
│ │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘        │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Flows

#### 1. File Upload Flow
```
Client → API Gateway → File Service → Compression/Dedup → Object Storage
   ↓                      ↓              ↓                    ↓
Cache ← Metadata Service ← Version Service ← Block Storage ← S3 Bucket
   ↓
Message Queue → Sync Service → Other Devices
```

#### 2. File Synchronization Flow
```
Device A (File Change) → Sync Service → Version Service → Metadata Service
                             ↓              ↓              ↓
                      Message Queue ← Block Analysis ← Delta Calculation
                             ↓
                      Device B, C, D (Receive Sync Events)
```

#### 3. File Sharing Flow
```
User A → Sharing Service → Permission Service → Metadata Service
    ↓           ↓               ↓                   ↓
Notification ← User B ← Email/Push ← Permission Grant
Service        ↓
               File Access (Based on Permissions)
```

### Key Technical Decisions

1. **File Storage Strategy**
   - Block-level storage for efficient delta sync
   - Deduplication at block level to save storage
   - Content-addressed storage using hash-based naming

2. **Consistency Model**
   - Strong consistency for metadata operations
   - Eventual consistency for file synchronization
   - Vector clocks for conflict resolution

3. **Scalability Patterns**
   - Microservices architecture for independent scaling
   - Database sharding by user_id
   - CDN for global file distribution

4. **Security Implementation**
   - Client-side encryption before upload
   - Zero-knowledge architecture
   - JWT tokens for authentication

---

## Problem 2: Database System with Low Latency {#problem-2}

### Problem Statement
Design a database system that stores information in memory and processes data with minimal latency. The system should provide high availability, consistency, and handle high-throughput operations with sub-millisecond response times.

### Functional Requirements
1. **Data Operations**
   - CRUD operations (Create, Read, Update, Delete)
   - Complex queries with joins and aggregations
   - Atomic transactions with ACID properties
   - Batch operations for bulk data processing

2. **Query Capabilities**
   - SQL-like query language support
   - Index-based fast lookups
   - Range queries and filtering
   - Real-time analytics queries

3. **Data Management**
   - Schema evolution and migration
   - Data validation and constraints
   - Backup and restore functionality
   - Data compression for memory efficiency

4. **Monitoring & Analytics**
   - Query performance metrics
   - Memory usage tracking
   - Real-time system health monitoring
   - Query plan optimization

### Non-Functional Requirements
1. **Performance**
   - Read latency: < 1ms (p99)
   - Write latency: < 5ms (p99)
   - Throughput: 1M+ operations per second
   - Query response time: < 10ms for complex queries

2. **Availability**
   - 99.99% uptime (< 1 hour downtime per year)
   - Zero-downtime deployments
   - Automatic failover within 30 seconds
   - Cross-region disaster recovery

3. **Scalability**
   - Handle 10TB+ of in-memory data
   - Support 10,000+ concurrent connections
   - Horizontal scaling capabilities
   - Dynamic resource allocation

4. **Consistency**
   - Strong consistency for critical operations
   - Configurable consistency levels
   - Multi-version concurrency control (MVCC)
   - Deadlock detection and resolution

5. **Durability**
   - Persistent storage for crash recovery
   - Write-ahead logging (WAL)
   - Point-in-time recovery
   - Data replication across nodes

### Data Model (UML)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Database     │    │      Table      │    │     Column      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ db_id (PK)      │    │ table_id (PK)   │    │ column_id (PK)  │
│ name            │◄───┤ db_id (FK)      │◄───┤ table_id (FK)   │
│ charset         │    │ name            │    │ name            │
│ created_at      │    │ schema_version  │    │ data_type       │
│ size_bytes      │    │ row_count       │    │ is_nullable     │
│ status          │    │ created_at      │    │ default_value   │
└─────────────────┘    │ last_updated    │    │ constraints     │
                       └─────────────────┘    └─────────────────┘
                                │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Index      │    │       Row       │    │   Transaction   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ index_id (PK)   │    │ row_id (PK)     │    │ txn_id (PK)     │
│ table_id (FK)   │◄───┤ table_id (FK)   │    │ session_id      │
│ name            │    │ version         │    │ start_time      │
│ type            │    │ data_blob       │    │ end_time        │
│ columns         │    │ created_at      │    │ status          │
│ is_unique       │    │ updated_at      │    │ isolation_level │
│ statistics      │    │ txn_id (FK)     │◄───┤ operations      │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MemoryPool    │    │   QueryPlan     │    │    Session      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ pool_id (PK)    │    │ plan_id (PK)    │    │ session_id (PK) │
│ node_id         │    │ query_hash      │    │ user_id         │
│ total_memory    │    │ execution_plan  │    │ connection_time │
│ used_memory     │    │ estimated_cost  │    │ last_activity   │
│ free_memory     │    │ actual_cost     │    │ active_txns     │
│ fragmentation   │    │ cache_hits      │    │ query_count     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 Client Tier                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    SQL      │ │    REST     │ │   GraphQL   │ │   gRPC      │ │   Native    │ │
│ │   Client    │ │   Client    │ │   Client    │ │   Client    │ │    SDK      │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Connection Load Balancer                              │
│                        (HAProxy/NGINX with Health Checks)                       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               Query Gateway                                     │
│              (Authentication, Rate Limiting, Query Routing)                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Application Tier                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Query     │ │   Query     │ │ Transaction │ │    Lock     │ │   Schema    │ │
│ │   Parser    │ │  Optimizer  │ │   Manager   │ │   Manager   │ │   Manager   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                        │                                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │  Execution  │ │    Index    │ │   Memory    │ │    WAL      │ │ Replication │ │
│ │   Engine    │ │   Manager   │ │   Manager   │ │   Manager   │ │   Manager   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              In-Memory Storage                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                              Memory Pools                                   │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│ │ │   Node 1    │ │   Node 2    │ │   Node 3    │ │   Node N    │          │ │
│ │ │  (Primary)  │ │ (Secondary) │ │ (Secondary) │ │ (Secondary) │          │ │
│ │ │             │ │             │ │             │ │             │          │ │
│ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │          │ │
│ │ │ │  Data   │ │ │ │  Data   │ │ │ │  Data   │ │ │ │  Data   │ │          │ │
│ │ │ │  Pool   │ │ │ │  Pool   │ │ │ │  Pool   │ │ │ │  Pool   │ │          │ │
│ │ │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │          │ │
│ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │ │ ┌─────────┐ │          │ │
│ │ │ │ Index   │ │ │ │ Index   │ │ │ │ Index   │ │ │ │ Index   │ │          │ │
│ │ │ │  Pool   │ │ │ │  Pool   │ │ │ │  Pool   │ │ │ │  Pool   │ │          │ │
│ │ │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │ │ └─────────┘ │          │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             Persistent Storage                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │     WAL     │ │  Checkpoint │ │   Backup    │ │    Logs     │ │  Metadata   │ │
│ │   Storage   │ │   Storage   │ │   Storage   │ │   Storage   │ │   Storage   │ │
│ │    (SSD)    │ │    (SSD)    │ │    (S3)     │ │   (SSD)     │ │    (SSD)    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Flows

#### 1. Read Query Execution Flow
```
Client → Query Gateway → Query Parser → Query Optimizer → Execution Engine
   ↓              ↓             ↓             ↓               ↓
Session ← Connection Pool ← Query Plan Cache ← Index Manager ← Memory Pool
Manager                                          ↓               ↓
   ↓                                        Result Set ← Data Retrieval
Result → Client
```

#### 2. Write Transaction Flow
```
Client → Transaction Manager → Lock Manager → WAL Manager → Memory Manager
   ↓            ↓                  ↓             ↓             ↓
Isolation ← Lock Acquisition ← Write Lock ← WAL Entry ← In-Memory Update
Level                              ↓             ↓             ↓
   ↓                          Commit/Rollback ← Persistence ← Index Update
Transaction Complete ← Unlock Resources ← WAL Sync ← Memory Commit
```

#### 3. Replication Flow
```
Primary Node (Write) → WAL Entry → Replication Manager → Secondary Nodes
        ↓                  ↓             ↓                    ↓
   Memory Update ← WAL Sync ← Async Replication ← Memory Application
        ↓                                                    ↓
   Commit Response                                    Replication ACK
```

### Key Technical Decisions

1. **Memory Management Strategy**
   - **NUMA-Aware Allocation**: Optimize for CPU cache locality
   - **Memory Pools**: Pre-allocated pools for different data types
   - **Garbage Collection**: Custom GC optimized for database workloads
   - **Memory Mapping**: Use mmap for large datasets

2. **Indexing Strategy**
   - **B+ Trees**: Primary indexes for range queries
   - **Hash Indexes**: Secondary indexes for exact matches
   - **Bitmap Indexes**: For low-cardinality columns
   - **LSM Trees**: For write-heavy workloads

3. **Concurrency Control**
   - **MVCC**: Multi-version concurrency control
   - **Optimistic Locking**: For read-heavy workloads
   - **Lock-Free Data Structures**: For critical paths
   - **Fine-Grained Locking**: Row-level and page-level locks

4. **Storage Engine Design**
   - **Columnar Storage**: For analytical queries
   - **Row Storage**: For transactional queries
   - **Compression**: Dictionary encoding and delta compression
   - **Partitioning**: Horizontal and vertical partitioning

### Performance Optimizations

1. **Query Optimization**
   - **Cost-Based Optimizer**: Statistics-driven query planning
   - **Plan Caching**: Cache execution plans for repeated queries
   - **Adaptive Optimization**: Runtime plan adjustment
   - **Parallel Execution**: Multi-threaded query processing

2. **Memory Optimization**
   - **Data Compression**: In-memory compression techniques
   - **Prefetching**: Predictive data loading
   - **Cache Management**: LRU with frequency-based eviction
   - **Memory Defragmentation**: Background compaction

3. **Network Optimization**
   - **Connection Pooling**: Reuse database connections
   - **Result Set Streaming**: Avoid large result buffering
   - **Binary Protocols**: Efficient data serialization
   - **Compression**: Network-level compression

### Monitoring & Observability

```python
class DatabaseMetrics:
    def __init__(self):
        self.metrics = {
            'query_latency_p99': HistogramMetric(),
            'memory_usage': GaugeMetric(),
            'transaction_throughput': CounterMetric(),
            'cache_hit_ratio': GaugeMetric(),
            'connection_count': GaugeMetric(),
            'replication_lag': GaugeMetric()
        }
    
    def track_query_execution(self, query_time, query_type):
        self.metrics['query_latency_p99'].observe(query_time)
        
    def monitor_memory_usage(self):
        total_memory = self.get_total_memory()
        used_memory = self.get_used_memory()
                 self.metrics['memory_usage'].set(used_memory / total_memory * 100)
```

---

## Problem 3: IP Blocking System {#problem-3}

### Problem Statement
Design a system that can block IP addresses from specific locations or based on suspicious behavior patterns. The system should handle high traffic volumes, provide real-time updates, and support geographic filtering with minimal latency impact.

### Functional Requirements
1. **IP Management**
   - Add/remove IP addresses to/from blocklist
   - Bulk import/export of IP ranges
   - Support for CIDR notation and IP ranges
   - Whitelist management for trusted IPs

2. **Geographic Filtering**
   - Block entire countries or regions
   - City-level blocking capabilities
   - ISP-based blocking
   - Custom geographic zones

3. **Behavior-Based Blocking**
   - Rate-limiting based blocking
   - Suspicious pattern detection
   - DDoS attack mitigation
   - Bot detection and blocking

4. **Rule Management**
   - Time-based blocking rules
   - Conditional blocking logic
   - Rule priority and inheritance
   - Custom blocking policies

### Non-Functional Requirements
1. **Performance**
   - IP lookup latency: < 1ms
   - Support 100K+ requests per second
   - Rule updates propagated within 5 seconds
   - 99.9% availability

2. **Scalability**
   - Handle 100M+ IP addresses
   - Support 10K+ blocking rules
   - Global distribution across regions
   - Auto-scaling capabilities

3. **Reliability**
   - Zero false positives for whitelisted IPs
   - Graceful degradation during overload
   - Automatic failover
   - Data consistency across nodes

4. **Security**
   - Encrypted rule storage
   - Audit logging for all changes
   - Role-based access control
   - Protection against rule tampering

### Data Model (UML)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   IPAddress     │    │    IPRange      │    │   GeoLocation   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ ip_id (PK)      │    │ range_id (PK)   │    │ geo_id (PK)     │
│ ip_address      │    │ start_ip        │    │ country_code    │
│ ip_type (v4/v6) │    │ end_ip          │    │ region          │
│ status          │    │ cidr_notation   │    │ city            │
│ created_at      │    │ description     │    │ latitude        │
│ updated_at      │    │ created_at      │    │ longitude       │
│ blocked_until   │    │ is_active       │    │ isp_name        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  BlockingRule   │    │   Whitelist     │    │   AuditLog      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ rule_id (PK)    │    │ whitelist_id    │    │ log_id (PK)     │
│ name            │    │ ip_id (FK)      │    │ action          │
│ rule_type       │    │ rule_id (FK)    │    │ entity_id       │
│ priority        │    │ reason          │    │ user_id         │
│ conditions      │    │ created_by      │    │ timestamp       │
│ action          │    │ expires_at      │    │ old_value       │
│ is_active       │    │ is_permanent    │    │ new_value       │
│ created_by      │    └─────────────────┘    │ ip_address      │
│ created_at      │                           └─────────────────┘
└─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ TrafficPattern  │    │   AlertRule     │    │   Performance   │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ pattern_id (PK) │    │ alert_id (PK)   │    │ metric_id (PK)  │
│ ip_id (FK)      │    │ rule_name       │    │ node_id         │
│ request_count   │    │ condition       │    │ requests_per_sec│
│ time_window     │    │ threshold       │    │ latency_avg     │
│ violation_count │    │ severity        │    │ memory_usage    │
│ last_violation  │    │ notification    │    │ cache_hit_ratio │
│ risk_score      │    │ is_active       │    │ timestamp       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 Client Tier                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Web      │ │   Admin     │ │    API      │ │   Mobile    │ │    CLI      │ │
│ │    App      │ │   Portal    │ │   Client    │ │    App      │ │    Tool     │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Edge CDN Layer                                     │
│                        (CloudFlare/AWS CloudFront)                             │
│                      ┌─────────────────────────────────┐                       │
│                      │        IP Filtering             │                       │
│                      │     (Edge Processing)           │                       │
│                      └─────────────────────────────────┘                       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               Load Balancer                                     │
│                      (Geographic Traffic Routing)                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               API Gateway                                       │
│                   (Rate Limiting, Authentication, Logging)                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Application Tier                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    IP       │ │    Rule     │ │  Geolocation│ │  Pattern    │ │   Alert     │ │
│ │  Lookup     │ │  Engine     │ │   Service   │ │ Detection   │ │  Service    │ │
│ │  Service    │ │             │ │             │ │   Service   │ │             │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                        │                                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │  Whitelist  │ │  Analytics  │ │    Audit    │ │    Cache    │ │    Sync     │ │
│ │  Service    │ │   Service   │ │   Service   │ │   Service   │ │   Service   │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Message Queue                                      │
│                           (Kafka/Redis Streams)                                │
│                     ┌─────────────────────────────────┐                        │
│                     │      Real-time Updates         │                        │
│                     │   (Rule Changes, Alerts)       │                        │
│                     └─────────────────────────────────┘                        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  Data Tier                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   IP Cache  │ │  Rule Cache │ │   Geo DB    │ │ Pattern DB  │ │   Audit     │ │
│ │   (Redis)   │ │   (Redis)   │ │(PostgreSQL) │ │(TimeSeries) │ │Database     │ │
│ │             │ │             │ │             │ │ (InfluxDB)  │ │(PostgreSQL) │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                                 │
│ ┌─────────────────────────────────────────────────────────────────────────────┐ │
│ │                          Distributed Storage                                │ │
│ │ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐          │ │
│ │ │   Region 1  │ │   Region 2  │ │   Region 3  │ │  Backup S3  │          │ │
│ │ │  (Primary)  │ │ (Secondary) │ │ (Secondary) │ │   Storage   │          │ │
│ │ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘          │ │
│ └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Flows

#### 1. IP Lookup Flow (Real-time Blocking)
```
Incoming Request → Edge CDN → Load Balancer → API Gateway → IP Lookup Service
        ↓               ↓           ↓              ↓               ↓
   Client IP ← Edge Filter ← Geo Route ← Rate Limit ← Cache Check ← Redis Lookup
        ↓                                                           ↓
   Allow/Block ← Decision Engine ← Rule Evaluation ← Pattern Match ← Database Query
```

#### 2. Rule Update Flow
```
Admin Portal → API Gateway → Rule Engine → Database Update → Cache Invalidation
      ↓             ↓            ↓             ↓                ↓
  Validation ← Auth Check ← Rule Parse ← Transaction ← Sync Service → Message Queue
      ↓                                                              ↓
  Success Response ← Audit Log ← Change Tracking ← Global Sync ← Edge Nodes
```

#### 3. Pattern Detection Flow
```
Traffic Monitor → Pattern Service → Analytics Engine → Alert Service → Notification
        ↓               ↓                ↓                ↓             ↓
   Log Events ← Behavior Analysis ← Risk Scoring ← Threshold Check ← Admin Alert
        ↓                                                             ↓
   Time Series DB ← Pattern Storage ← Rule Creation ← Auto-block ← Rule Engine
```

### Key Technical Decisions

1. **IP Storage Strategy**
   - **Trie Data Structure**: Efficient IP range lookups
   - **CIDR Optimization**: Compressed storage for IP ranges  
   - **Redis Clustering**: Distributed caching for speed
   - **Bloom Filters**: Quick negative lookups

2. **Geographic Data**
   - **MaxMind GeoIP**: Industry-standard IP geolocation
   - **Real-time Updates**: Continuous geo-database updates
   - **Custom Zones**: User-defined geographic regions
   - **ISP Mapping**: Provider-based blocking

3. **Performance Optimization**
   - **Edge Computing**: CDN-level IP filtering
   - **Multi-level Caching**: L1 (Edge), L2 (Regional), L3 (Database)
   - **Precomputed Results**: Common IP range calculations
   - **Async Processing**: Non-blocking rule updates

4. **Scalability Design**
   - **Horizontal Sharding**: IP ranges across multiple nodes
   - **Read Replicas**: Geographic distribution of read nodes
   - **Event Sourcing**: Change history for audit and rollback
   - **Circuit Breakers**: Prevent cascade failures

---

## Problem 4: Voting System {#problem-4}

### Problem Statement
Design a secure and scalable voting system where users can view candidate details, cast votes, and ensure accurate vote tallying. The system must prevent fraud, handle high concurrency during elections, and provide real-time results while maintaining voter privacy.

### Functional Requirements
1. **Voter Management**
   - Voter registration and verification
   - Unique voter identification
   - Eligibility verification
   - Voter authentication

2. **Candidate Management**
   - Candidate registration and profiles
   - Campaign information display
   - Candidate categorization by election/position
   - Media content management

3. **Voting Process**
   - Secure vote casting interface
   - Multiple election support
   - Ballot validation and submission
   - Vote confirmation receipts

4. **Election Management**
   - Election creation and configuration
   - Voting period management
   - Real-time vote counting
   - Results publication and reporting

### Non-Functional Requirements
1. **Security**
   - Voter anonymity and privacy
   - Vote integrity and tamper-proof storage
   - End-to-end encryption
   - Fraud detection and prevention

2. **Performance**
   - Support 10M+ concurrent voters
   - Sub-second vote submission
   - Real-time result updates
   - 99.99% uptime during elections

3. **Reliability**
   - Zero vote loss tolerance
   - Audit trail for all operations
   - Disaster recovery capabilities
   - Redundant storage and processing

4. **Scalability**
   - Handle national-scale elections
   - Auto-scaling during peak times
   - Geographic distribution
   - Database partitioning

### Data Model (UML)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Voter      │    │    Election     │    │   Candidate     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ voter_id (PK)   │    │ election_id(PK) │    │ candidate_id(PK)│
│ national_id     │◄───┤ name            │◄───┤ election_id(FK) │
│ email           │    │ description     │    │ name            │
│ phone           │    │ start_date      │    │ party           │
│ address         │    │ end_date        │    │ biography       │
│ is_verified     │    │ status          │    │ platform        │
│ registration_dt │    │ election_type   │    │ photo_url       │
│ last_login      │    │ created_by      │    │ created_at      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Vote       │    │     Ballot      │    │   VoteRecord    │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ vote_id (PK)    │    │ ballot_id (PK)  │    │ record_id (PK)  │
│ voter_id (FK)   │    │ election_id(FK) │    │ election_id(FK) │
│ election_id(FK) │    │ voter_id (FK)   │    │ candidate_id(FK)│
│ candidate_id(FK)│    │ submission_time │    │ vote_count      │
│ vote_hash       │    │ is_submitted    │    │ timestamp       │
│ timestamp       │    │ ip_address      │    │ batch_id        │
│ encrypted_vote  │    │ device_info     │    │ verification    │
│ digital_signature│   │ ballot_hash     │    │ is_final        │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AuditTrail    │    │   ElectionResult│    │  SecurityEvent  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ audit_id (PK)   │    │ result_id (PK)  │    │ event_id (PK)   │
│ entity_type     │    │ election_id(FK) │    │ event_type      │
│ entity_id       │    │ candidate_id(FK)│    │ severity        │
│ action          │    │ total_votes     │    │ description     │
│ user_id         │    │ percentage      │    │ source_ip       │
│ timestamp       │    │ rank            │    │ user_agent      │
│ old_value       │    │ is_winner       │    │ timestamp       │
│ new_value       │    │ certified_at    │    │ resolved_at     │
│ ip_address      │    │ certified_by    │    │ action_taken    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 Client Tier                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Voter     │ │   Admin     │ │  Election   │ │   Mobile    │ │   Kiosk     │ │
│ │   Portal    │ │   Portal    │ │  Observer   │ │    App      │ │ Terminal    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  CDN Layer                                      │
│                           (Static Content Delivery)                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               Load Balancer                                     │
│                      (Geographic & Load Distribution)                          │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               API Gateway                                       │
│              (Authentication, Rate Limiting, Request Routing)                  │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Application Tier                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Voter    │ │  Election   │ │  Candidate  │ │   Voting    │ │   Result    │ │
│ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                        │                                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Auth     │ │    Audit    │ │  Security   │ │ Notification│ │  Analytics  │ │
│ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Message Queue                                      │
│                           (Kafka for Event Streaming)                          │
│               ┌─────────────────────────────────────────────────┐               │
│               │    Real-time Events (Votes, Results, Alerts)   │               │
│               └─────────────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Security Layer                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │  Encryption │ │ Digital     │ │  Blockchain │ │    HSM      │ │   Fraud     │ │
│ │   Service   │ │ Signature   │ │  Ledger     │ │  (Hardware  │ │ Detection   │ │
│ │             │ │   Service   │ │             │ │ Security)   │ │   Engine    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  Data Tier                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Voter DB  │ │ Election DB │ │   Vote DB   │ │  Audit DB   │ │ Analytics   │ │
│ │(PostgreSQL) │ │(PostgreSQL) │ │(PostgreSQL) │ │(PostgreSQL) │ │DB (ClickHse)│ │
│ │             │ │             │ │ (Encrypted) │ │             │ │             │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Cache    │ │  Blockchain │ │   Backup    │ │    Log      │ │   Media     │ │
│ │   (Redis)   │ │   Storage   │ │  Storage    │ │  Storage    │ │  Storage    │ │
│ │             │ │             │ │    (S3)     │ │   (ELK)     │ │    (S3)     │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Flows

#### 1. Vote Casting Flow
```
Voter Portal → Authentication → Ballot Display → Vote Selection → Encryption
      ↓              ↓               ↓              ↓              ↓
  Login Check ← Identity Verify ← Election Load ← Candidate List ← Vote Encrypt
      ↓                                                              ↓
  Vote Submit → Digital Signature → Blockchain Record → Database Store → Confirmation
      ↓               ↓                  ↓                 ↓             ↓
  Audit Log ← Security Check ← Immutable Hash ← Encrypted Store ← Receipt Generate
```

#### 2. Result Tallying Flow
```
Vote Database → Aggregation Service → Verification Engine → Result Service → Publication
       ↓              ↓                    ↓                  ↓             ↓
  Real-time ← Batch Processing ← Integrity Check ← Statistics ← Public API
  Updates                             ↓                                     ↓
       ↓                        Blockchain Verify                   Live Dashboard
  Analytics Service ← Audit Trail ← Consensus Check ← Final Results ← Media Feed
```

#### 3. Security Monitoring Flow
```
All Operations → Security Service → Fraud Detection → Alert Service → Response Team
        ↓              ↓                ↓               ↓             ↓
   Event Log ← Pattern Analysis ← Risk Scoring ← Notification ← Investigation
        ↓                              ↓                              ↓
   SIEM System ← Threat Intelligence ← Anomaly Detection ← Auto Block ← Incident Report
```

### Key Technical Decisions

1. **Security Architecture**
   - **End-to-End Encryption**: Votes encrypted from client to storage
   - **Blockchain Integration**: Immutable vote records for transparency
   - **Digital Signatures**: PKI-based vote authentication
   - **Hardware Security Modules**: Tamper-proof key management

2. **Vote Storage Strategy**
   - **Encrypted Database**: AES-256 encryption for vote data
   - **Separation of Concerns**: Voter identity separate from vote content
   - **Redundant Storage**: Multiple geographically distributed copies
   - **Immutable Records**: Write-once, read-many vote storage

3. **Scalability Design**
   - **Microservices**: Independent scaling of components
   - **Database Sharding**: Votes partitioned by geographic region
   - **Caching Strategy**: Redis for session and candidate data
   - **CDN Distribution**: Global content delivery for static assets

4. **Fraud Prevention**
   - **Multi-Factor Authentication**: Strong voter identity verification
   - **Rate Limiting**: Prevent automated voting attacks
   - **Behavioral Analysis**: Machine learning for anomaly detection
   - **Audit Trails**: Complete operation history for forensics

---

## Problem 5: E-commerce System for Top-Selling Products {#problem-5}

### Problem Statement
Design an e-commerce system that can identify and track the top 50 selling products in the last hour. The system should handle large-scale data processing, provide real-time analytics, and support high-traffic shopping operations with accurate sales tracking.

### Functional Requirements
1. **Product Management**
   - Product catalog with detailed information
   - Inventory tracking and management
   - Price management and promotions
   - Product categorization and search

2. **Sales Tracking**
   - Real-time sales data collection
   - Hourly top 50 product identification
   - Sales analytics and reporting
   - Revenue tracking and calculation

3. **Customer Operations**
   - User registration and authentication
   - Shopping cart and checkout
   - Order processing and fulfillment
   - Payment processing integration

4. **Analytics & Reporting**
   - Real-time sales dashboards
   - Top products trending analysis
   - Sales performance metrics
   - Business intelligence reporting

### Non-Functional Requirements
1. **Performance**
   - Handle 100K+ concurrent users
   - Sub-second product search results
   - Real-time top products updates (< 5 minutes)
   - 99.9% uptime for critical operations

2. **Scalability**
   - Support millions of products
   - Handle 10K+ orders per minute
   - Process 1M+ product views per hour
   - Auto-scaling during traffic spikes

3. **Data Processing**
   - Real-time stream processing
   - Large-scale data aggregation
   - Historical data analysis
   - Machine learning integration

4. **Reliability**
   - Zero data loss for sales transactions
   - Consistent inventory management
   - Disaster recovery capabilities
   - Data backup and restoration

### Data Model (UML)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Product      │    │    Category     │    │   Inventory     │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ product_id (PK) │    │ category_id(PK) │    │ inventory_id(PK)│
│ name            │◄───┤ name            │◄───┤ product_id (FK) │
│ description     │    │ description     │    │ warehouse_id    │
│ category_id(FK) │    │ parent_id (FK)  │    │ quantity        │
│ price           │    │ is_active       │    │ reserved_qty    │
│ weight          │    │ created_at      │    │ min_threshold   │
│ dimensions      │    │ updated_at      │    │ last_updated    │
│ brand           │    └─────────────────┘    │ location        │
│ sku             │                           └─────────────────┘
│ is_active       │
│ created_at      │    ┌─────────────────┐    ┌─────────────────┐
└─────────────────┘    │     Customer    │    │      Order      │
         │              ├─────────────────┤    ├─────────────────┤
         ▼              │ customer_id(PK) │    │ order_id (PK)   │
┌─────────────────┐    │ email           │◄───┤ customer_id(FK) │
│   OrderItem     │    │ first_name      │    │ order_date      │
├─────────────────┤    │ last_name       │    │ total_amount    │
│ order_item_id   │    │ phone           │    │ status          │
│ order_id (FK)   │    │ address         │    │ shipping_addr   │
│ product_id (FK) │    │ created_at      │    │ payment_method  │
│ quantity        │    │ last_login      │    │ tracking_number │
│ unit_price      │    └─────────────────┘    │ created_at      │
│ total_price     │                           │ updated_at      │
│ discount        │    ┌─────────────────┐    └─────────────────┘
└─────────────────┘    │  SalesMetrics   │
                       ├─────────────────┤    ┌─────────────────┐
┌─────────────────┐    │ metric_id (PK)  │    │ TopProductHour  │
│  ProductView    │    │ product_id (FK) │    ├─────────────────┤
├─────────────────┤    │ hour_bucket     │    │ ranking_id (PK) │
│ view_id (PK)    │    │ sales_count     │    │ product_id (FK) │
│ product_id (FK) │    │ revenue         │    │ hour_bucket     │
│ customer_id(FK) │    │ view_count      │    │ sales_count     │
│ session_id      │    │ conversion_rate │    │ revenue         │
│ timestamp       │    │ avg_price       │    │ rank_position   │
│ user_agent      │    │ created_at      │    │ created_at      │
│ ip_address      │    └─────────────────┘    │ is_current      │
└─────────────────┘                           └─────────────────┘
```

### Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 Client Tier                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Web      │ │   Mobile    │ │   Admin     │ │ Analytics   │ │   Partner   │ │
│ │ Application │ │    App      │ │   Portal    │ │ Dashboard   │ │    API      │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  CDN Layer                                      │
│                        (CloudFront/CloudFlare)                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               Load Balancer                                     │
│                       (Application Load Balancer)                              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               API Gateway                                       │
│                    (Rate Limiting, Authentication, Routing)                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Application Tier                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Product   │ │   Order     │ │  Customer   │ │  Inventory  │ │   Search    │ │
│ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                        │                                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │  Payment    │ │ Analytics   │ │Notification │ │    Auth     │ │    Cart     │ │
│ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Message Streaming                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Kafka     │ │  Sales      │ │   Views     │ │  Inventory  │ │   User      │ │
│ │  Cluster    │ │  Stream     │ │   Stream    │ │   Stream    │ │  Stream     │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           Real-time Processing                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Apache    │ │   Spark     │ │    Top      │ │   Sales     │ │  Machine    │ │
│ │   Flink     │ │ Streaming   │ │  Products   │ │Aggregation  │ │ Learning    │ │
│ │  (Stream)   │ │             │ │  Calculator │ │   Engine    │ │   Engine    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  Data Tier                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Product DB  │ │ Customer DB │ │  Order DB   │ │ Analytics   │ │   Search    │ │
│ │(PostgreSQL) │ │(PostgreSQL) │ │(PostgreSQL) │ │DB (ClickHse)│ │(Elasticsearch│
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Cache    │ │  Time Series│ │   Data      │ │   Backup    │ │    Logs     │ │
│ │   (Redis)   │ │DB (InfluxDB)│ │  Warehouse  │ │  Storage    │ │  (ELK)      │ │
│ │             │ │             │ │  (Snowflake)│ │    (S3)     │ │             │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Flows

#### 1. Real-time Top Products Calculation Flow
```
Sales Events → Kafka Stream → Flink Processing → Aggregation Engine → Top Products Ranking
      ↓              ↓              ↓                 ↓                    ↓
   Event Log ← Stream Partition ← Windowing ← Hourly Buckets ← Ranking Algorithm
      ↓                                                                   ↓
   InfluxDB ← Time Series Store ← Metric Calculation ← Cache Update ← API Response
```

#### 2. Order Processing Flow
```
Add to Cart → Checkout → Payment Processing → Order Creation → Inventory Update
      ↓           ↓             ↓                 ↓              ↓
  Cart Service ← Order Service ← Payment Service ← Database ← Sales Event
      ↓                                                         ↓
  Session Store ← Order Confirmation ← Email Service ← Kafka Stream ← Analytics
```

#### 3. Product Search and View Flow
```
Search Query → Search Service → Elasticsearch → Results Ranking → Response
      ↓             ↓                ↓               ↓             ↓
  User Input ← Query Processing ← Index Search ← ML Scoring ← Cached Results
      ↓                                                         ↓
  View Event → Kafka Stream → Analytics Pipeline → Recommendation Engine
```

### Key Technical Decisions

1. **Real-time Processing Architecture**
   - **Apache Flink**: Stream processing for real-time aggregations
   - **Kafka Streams**: Event streaming and message queuing
   - **Sliding Windows**: Hourly buckets for top products calculation
   - **ClickHouse**: Columnar database for fast analytical queries

2. **Top Products Algorithm**
   - **Time-based Windows**: Rolling 1-hour windows for calculations
   - **Weighted Scoring**: Revenue + quantity + views with configurable weights
   - **Cache Strategy**: Redis caching of top 50 results with 5-minute TTL
   - **Batch + Stream**: Combination of real-time streams and batch processing

3. **Scalability Strategy**
   - **Microservices**: Independent scaling of each business domain
   - **Database Sharding**: Products and orders partitioned by region/category
   - **CDN**: Global content delivery for product images and static content
   - **Auto-scaling**: Kubernetes HPA based on CPU/memory and custom metrics

4. **Data Storage Strategy**
   - **OLTP Databases**: PostgreSQL for transactional data (products, orders)
   - **OLAP Database**: ClickHouse for analytical workloads
   - **Time Series**: InfluxDB for metrics and time-based data
   - **Search Engine**: Elasticsearch for product search and recommendations

---

## Problem 6: Online Bookstore {#problem-6}

### Problem Statement
Design an online bookstore platform that allows users to browse books, view prices, make purchases through multiple payment methods, and provides features like search, recommendations, and user reviews. The system should handle large catalogs and provide personalized experiences.

### Functional Requirements
1. **Book Catalog Management**
   - Book information (title, author, ISBN, genre, price)
   - Book search and filtering capabilities
   - Category-based browsing
   - Book availability and inventory tracking

2. **User Management**
   - User registration and authentication
   - User profiles and preferences
   - Purchase history and wishlists
   - Address and payment method management

3. **Shopping Experience**
   - Shopping cart functionality
   - Multiple payment methods (credit/debit, PayPal, digital wallets)
   - Order processing and tracking
   - Digital and physical book delivery

4. **Social Features**
   - Book reviews and ratings
   - Reading lists and recommendations
   - Social sharing capabilities
   - Author profiles and following

### Non-Functional Requirements
1. **Performance**
   - Support 100K+ concurrent users
   - Sub-second search response times
   - Page load times < 2 seconds
   - 99.9% uptime availability

2. **Scalability**
   - Handle millions of books in catalog
   - Support 1M+ registered users
   - Process 10K+ orders per day
   - Auto-scaling during peak periods

3. **User Experience**
   - Personalized recommendations
   - Mobile-responsive design
   - Offline reading capabilities (digital books)
   - Multi-language support

4. **Security**
   - Secure payment processing
   - User data protection
   - Fraud detection and prevention
   - Content piracy protection

### Data Model (UML)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      Book       │    │     Author      │    │     Genre       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ book_id (PK)    │    │ author_id (PK)  │    │ genre_id (PK)   │
│ title           │◄───┤ name            │◄───┤ name            │
│ isbn            │    │ biography       │    │ description     │
│ description     │    │ birth_date      │    │ parent_id (FK)  │
│ price           │    │ nationality     │    │ is_active       │
│ pages           │    │ photo_url       │    │ created_at      │
│ language        │    │ created_at      │    └─────────────────┘
│ publication_date│    │ is_active       │
│ publisher       │    └─────────────────┘    ┌─────────────────┐
│ format (ebook/  │                           │   BookAuthor    │
│ paperback/hard) │    ┌─────────────────┐    ├─────────────────┤
│ cover_image_url │    │   BookGenre     │    │ book_id (FK)    │
│ stock_quantity  │    ├─────────────────┤    │ author_id (FK)  │
│ is_active       │    │ book_id (FK)    │    │ author_type     │
│ created_at      │    │ genre_id (FK)   │    │ created_at      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼              ┌─────────────────┐    ┌─────────────────┐
┌─────────────────┐    │      User       │    │     Order       │
│     Review      │    ├─────────────────┤    ├─────────────────┤
├─────────────────┤    │ user_id (PK)    │    │ order_id (PK)   │
│ review_id (PK)  │    │ email           │◄───┤ user_id (FK)    │
│ book_id (FK)    │    │ password_hash   │    │ order_date      │
│ user_id (FK)    │    │ first_name      │    │ total_amount    │
│ rating (1-5)    │    │ last_name       │    │ status          │
│ title           │    │ phone           │    │ shipping_addr   │
│ content         │    │ date_of_birth   │    │ billing_addr    │
│ helpful_votes   │    │ created_at      │    │ payment_method  │
│ verified_purchase│   │ last_login      │    │ tracking_number │
│ created_at      │    │ is_active       │    │ created_at      │
└─────────────────┘    └─────────────────┘    │ updated_at      │
                                              └─────────────────┘
┌─────────────────┐    ┌─────────────────┐           │
│   OrderItem     │    │    Wishlist     │           ▼
├─────────────────┤    ├─────────────────┤    ┌─────────────────┐
│ order_item_id   │    │ wishlist_id(PK) │    │    Payment      │
│ order_id (FK)   │    │ user_id (FK)    │    ├─────────────────┤
│ book_id (FK)    │    │ book_id (FK)    │    │ payment_id (PK) │
│ quantity        │    │ created_at      │    │ order_id (FK)   │
│ unit_price      │    │ priority        │    │ amount          │
│ format          │    └─────────────────┘    │ payment_method  │
│ discount        │                           │ transaction_id  │
│ created_at      │    ┌─────────────────┐    │ status          │
└─────────────────┘    │ Recommendation  │    │ processed_at    │
                       ├─────────────────┤    │ gateway         │
                       │ rec_id (PK)     │    └─────────────────┘
                       │ user_id (FK)    │
                       │ book_id (FK)    │
                       │ score           │
                       │ reason          │
                       │ created_at      │
                       └─────────────────┘
```

### Component Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                 Client Tier                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Web      │ │   Mobile    │ │   Tablet    │ │   Admin     │ │   Author    │ │
│ │Application  │ │    App      │ │    App      │ │   Portal    │ │   Portal    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  CDN Layer                                      │
│                     (CloudFront for Static Content)                            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               Load Balancer                                     │
│                          (Application Load Balancer)                           │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                               API Gateway                                       │
│                    (Rate Limiting, Authentication, Routing)                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Application Tier                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Book     │ │    User     │ │    Order    │ │   Search    │ │   Review    │ │
│ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                        │                                        │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Recommenda- │ │   Payment   │ │ Notification│ │ Inventory   │ │  Analytics  │ │
│ │tion Service │ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Message Queue                                      │
│                              (RabbitMQ/SQS)                                    │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              External Services                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Payment   │ │   Shipping  │ │    Email    │ │     ML      │ │   Content   │ │
│ │  Gateways   │ │  Services   │ │   Service   │ │  Platform   │ │ Delivery    │ │
│ │(Stripe/PP)  │ │(FedEx/UPS)  │ │(SendGrid)   │ │(TensorFlow) │ │  Network    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
                                        │
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                  Data Tier                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Book DB   │ │   User DB   │ │  Order DB   │ │  Review DB  │ │ Analytics   │ │
│ │(PostgreSQL) │ │(PostgreSQL) │ │(PostgreSQL) │ │(PostgreSQL) │ │DB (ClickHse)│ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
│                                                                                 │
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Cache    │ │   Search    │ │   Content   │ │   Session   │ │    Logs     │ │
│ │   (Redis)   │ │(Elasticsearch│ │  Storage    │ │   Store     │ │   (ELK)     │ │
│ │             │ │             │ │    (S3)     │ │  (Redis)    │ │             │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Key Flows

#### 1. Book Search and Discovery Flow
```
User Query → Search Service → Elasticsearch → Results Ranking → Recommendation Engine
     ↓             ↓                ↓              ↓                    ↓
Search Intent ← Query Processing ← Index Search ← ML Scoring ← Personalization
     ↓                                                                  ↓
Book Details ← Product Service ← Cache Lookup ← Database Query ← Related Books
```

#### 2. Purchase Flow
```
Add to Cart → Cart Service → Checkout → Payment Processing → Order Creation
     ↓            ↓            ↓              ↓                  ↓
Cart Storage ← Session Store ← Order Service ← Payment Gateway ← Order Database
     ↓                                                          ↓
Inventory Update ← Stock Check ← Fulfillment ← Email Notification ← Analytics
```

#### 3. Recommendation Flow
```
User Behavior → Analytics Service → ML Pipeline → Recommendation Service → Personalized Results
      ↓               ↓                ↓                ↓                      ↓
Event Tracking ← Behavior Analysis ← Model Training ← Score Calculation ← API Response
      ↓                                                                       ↓
Feature Store ← Data Pipeline ← Collaborative Filtering ← Content Filtering ← A/B Testing
```

### Key Technical Decisions

1. **Search and Discovery**
   - **Elasticsearch**: Full-text search with fuzzy matching and faceted search
   - **Recommendation Engine**: Collaborative filtering + content-based filtering
   - **Caching Strategy**: Redis for search results and book metadata
   - **Personalization**: ML-based recommendations using user behavior data

2. **Content Management**
   - **Multi-format Support**: Physical books, eBooks, audiobooks
   - **Content Delivery**: CDN for book covers, samples, and digital content
   - **DRM Protection**: Digital rights management for eBooks
   - **Metadata Management**: Rich book information with author relationships

3. **Payment and Order Processing**
   - **Multiple Payment Methods**: Credit cards, PayPal, digital wallets, gift cards
   - **Order State Management**: Complex order workflows with inventory reservations
   - **Fraud Detection**: ML-based fraud prevention for payments
   - **International Support**: Multi-currency and tax calculation

4. **Scalability Architecture**
   - **Microservices**: Domain-driven service boundaries (Books, Users, Orders, Reviews)
   - **Database Sharding**: User data sharded by user ID, books by category
   - **Read Replicas**: Separate read replicas for analytics and reporting
   - **Event-Driven**: Asynchronous processing for reviews, recommendations, notifications

---

## Problem 7: Building Occupancy System {#problem-7}

### Problem Statement
Design a system to track the number of people present on each floor of a multi-story building in real-time. The system should provide accurate occupancy counts, ensure compliance with safety regulations, and offer analytics for space utilization optimization.

### Functional Requirements
1. **Occupancy Tracking**
   - Real-time people counting per floor
   - Entry/exit detection and tracking
   - Maximum capacity enforcement
   - Historical occupancy data

2. **Safety Compliance**
   - Emergency evacuation assistance
   - Fire safety regulation compliance
   - Automatic alerts for overcrowding
   - Emergency personnel notifications

3. **Access Control Integration**
   - Badge/card reader integration
   - Visitor management system
   - Employee check-in/check-out
   - Unauthorized access detection

4. **Analytics & Reporting**
   - Peak usage analysis
   - Space utilization reports
   - Trend analysis over time
   - Cost optimization insights

### Non-Functional Requirements
1. **Real-time Processing**: Updates within 5 seconds of occupancy changes
2. **Accuracy**: 95%+ accuracy in people counting
3. **Scalability**: Support buildings with 50+ floors and 10K+ occupants
4. **Reliability**: 99.9% uptime with redundant sensors

### Data Model (UML)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Building     │    │      Floor      │    │      Zone       │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ building_id(PK) │    │ floor_id (PK)   │    │ zone_id (PK)    │
│ name            │◄───┤ building_id(FK) │◄───┤ floor_id (FK)   │
│ address         │    │ floor_number    │    │ name            │
│ max_occupancy   │    │ max_occupancy   │    │ max_occupancy   │
│ total_floors    │    │ area_sqft       │    │ area_sqft       │
│ created_at      │    │ is_active       │    │ zone_type       │
└─────────────────┘    └─────────────────┘    └─────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Sensor      │    │ OccupancyEvent  │    │  PersonTracker  │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ sensor_id (PK)  │    │ event_id (PK)   │    │ tracker_id (PK) │
│ zone_id (FK)    │    │ sensor_id (FK)  │    │ person_id       │
│ sensor_type     │    │ event_type      │    │ current_floor   │
│ location        │    │ person_count    │    │ entry_time      │
│ is_active       │    │ timestamp       │    │ last_seen       │
│ last_ping       │    │ confidence      │    │ status          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        IoT Sensor Layer                        │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Camera    │ │  Infrared   │ │   Badge     │ │   Motion    │ │
│ │  Sensors    │ │  Sensors    │ │  Readers    │ │  Detectors  │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Data Collection                           │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│ │   MQTT      │ │ Data        │ │ Real-time   │               │
│ │  Broker     │ │ Aggregator  │ │ Processor   │               │
│ └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                    Application Services                        │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ Occupancy   │ │   Alert     │ │ Analytics   │ │   Report    │ │
│ │  Service    │ │  Service    │ │  Service    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## Problem 8: Image Upload and Tagging System {#problem-8}

### Problem Statement
Design a system where users can upload images with tags and search for images by entering tags. The system should support automatic tag generation, image processing, and efficient search capabilities.

### Functional Requirements
1. **Image Upload & Storage**
   - Multi-format image upload (JPEG, PNG, WebP, etc.)
   - Image validation and processing
   - Thumbnail generation
   - Metadata extraction

2. **Tagging System**
   - Manual tag assignment by users
   - Auto-tagging using ML/computer vision
   - Tag suggestions and auto-complete
   - Tag hierarchy and categories

3. **Search & Discovery**
   - Tag-based image search
   - Advanced filtering options
   - Similar image recommendations
   - Full-text search in descriptions

4. **User Management**
   - User accounts and authentication
   - Image ownership and permissions
   - Sharing and collaboration features
   - Privacy controls

### Non-Functional Requirements
1. **Performance**: Upload processing < 10 seconds, search results < 1 second
2. **Scalability**: Handle millions of images and tags
3. **Storage**: Efficient image storage with CDN delivery
4. **ML Processing**: Real-time auto-tagging capabilities

### Data Model (UML)
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      User       │    │     Image       │    │      Tag        │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ user_id (PK)    │    │ image_id (PK)   │    │ tag_id (PK)     │
│ username        │◄───┤ user_id (FK)    │    │ name            │
│ email           │    │ filename        │    │ category        │
│ created_at      │    │ original_url    │    │ usage_count     │
└─────────────────┘    │ thumbnail_url   │    │ created_at      │
                       │ file_size       │    └─────────────────┘
┌─────────────────┐    │ width           │             │
│   ImageTag      │    │ height          │             │
├─────────────────┤    │ format          │             │
│ image_id (FK)   │    │ uploaded_at     │             │
│ tag_id (FK)     │◄───┤ is_public       │             │
│ confidence      │    │ description     │             │
│ source          │    └─────────────────┘             │
│ created_at      │                                    │
└─────────────────┘    ┌─────────────────┐             │
                       │  ImageSearch    │             │
                       ├─────────────────┤             │
                       │ search_id (PK)  │             │
                       │ user_id (FK)    │             │
                       │ query           │             │
                       │ results_count   │             │
                       │ timestamp       │             │
                       └─────────────────┘
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Applications                     │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │    Web      │ │   Mobile    │ │    API      │ │   Admin     │ │
│ │    App      │ │    App      │ │  Client     │ │  Portal     │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                      Processing Pipeline                       │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │   Upload    │ │   Image     │ │     ML      │ │   Search    │ │
│ │  Service    │ │ Processing  │ │  Tagging    │ │  Service    │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                         Data Storage                           │
├─────────────────────────────────────────────────────────────────┤
│ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │  Metadata   │ │   Object    │ │   Search    │ │   Cache     │ │
│ │ Database    │ │  Storage    │ │   Index     │ │  (Redis)    │ │
│ │(PostgreSQL) │ │    (S3)     │ │(Elasticsearch│ │             │ │
│ └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---