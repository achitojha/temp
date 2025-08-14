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