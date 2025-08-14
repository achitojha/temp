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