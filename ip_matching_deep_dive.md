# IP Matching Deep Dive - Problem 3: IP Blocking System

## Overview
The IP blocking system needs to efficiently match incoming IP addresses against various blocking rules including individual IPs, IP ranges, CIDR blocks, and geographic locations. Here's how the matching works:

## Data Model Review
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

┌─────────────────┐    ┌─────────────────┐
│  BlockingRule   │    │   Whitelist     │
├─────────────────┤    ├─────────────────┤
│ rule_id (PK)    │    │ whitelist_id    │
│ name            │    │ ip_id (FK)      │
│ rule_type       │    │ rule_id (FK)    │
│ priority        │    │ reason          │
│ conditions      │    │ created_by      │
│ action          │    │ expires_at      │
│ is_active       │    │ is_permanent    │
└─────────────────┘    └─────────────────┘
```

## IP Matching Implementation

### 1. IP Address Storage and Indexing

```python
class IPMatcher:
    def __init__(self):
        # Trie structure for efficient IP lookups
        self.ipv4_trie = IPv4Trie()
        self.ipv6_trie = IPv6Trie()
        
        # Cache for frequently accessed IPs
        self.cache = LRUCache(maxsize=100000)
        
        # Bloom filter for quick negative lookups
        self.blocked_ips_bloom = BloomFilter(capacity=10000000, error_rate=0.001)
    
    def is_ip_blocked(self, ip_address: str) -> bool:
        """
        Main entry point for IP blocking check
        Returns True if IP should be blocked
        """
        # Step 1: Quick bloom filter check (eliminates most clean IPs instantly)
        if not self.blocked_ips_bloom.might_contain(ip_address):
            return False
        
        # Step 2: Cache lookup
        cache_key = f"ip_block:{ip_address}"
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Step 3: Check whitelist first (highest priority)
        if self.is_whitelisted(ip_address):
            self.cache.set(cache_key, False, ttl=300)
            return False
        
        # Step 4: Comprehensive blocking check
        result = self._comprehensive_ip_check(ip_address)
        self.cache.set(cache_key, result, ttl=60)
        return result
```

### 2. Multi-Layer Matching Strategy

```python
def _comprehensive_ip_check(self, ip_address: str) -> bool:
    """
    Multi-layer IP matching with priority order:
    1. Exact IP match
    2. IP range match
    3. CIDR block match
    4. Geographic match
    5. Behavioral pattern match
    """
    ip_obj = ipaddress.ip_address(ip_address)
    
    # Priority 1: Exact IP match
    if self._exact_ip_match(ip_address):
        return True
    
    # Priority 2: IP Range match
    if self._ip_range_match(ip_obj):
        return True
    
    # Priority 3: CIDR block match
    if self._cidr_match(ip_obj):
        return True
    
    # Priority 4: Geographic match
    if self._geographic_match(ip_address):
        return True
    
    # Priority 5: Behavioral pattern match
    if self._behavioral_match(ip_address):
        return True
    
    return False
```

### 3. Exact IP Matching

```python
def _exact_ip_match(self, ip_address: str) -> bool:
    """
    Direct hash table lookup for exact IP matches
    O(1) complexity
    """
    query = """
    SELECT status, blocked_until 
    FROM IPAddress 
    WHERE ip_address = %s 
    AND status IN ('blocked', 'suspicious')
    AND (blocked_until IS NULL OR blocked_until > NOW())
    """
    
    result = self.db.execute(query, (ip_address,))
    return bool(result)
```

### 4. IP Range Matching

```python
def _ip_range_match(self, ip_obj) -> bool:
    """
    Check if IP falls within any blocked ranges
    Uses interval tree for efficient range queries
    """
    # Convert IP to integer for range comparison
    ip_int = int(ip_obj)
    
    query = """
    SELECT range_id, start_ip, end_ip
    FROM IPRange 
    WHERE start_ip <= %s AND end_ip >= %s
    AND is_active = true
    """
    
    # Use IP integer representation for efficient comparison
    ranges = self.db.execute(query, (ip_int, ip_int))
    return bool(ranges)

# Alternative: Interval Tree Implementation for better performance
class IntervalTree:
    def __init__(self):
        self.intervals = []
    
    def add_range(self, start_ip: int, end_ip: int, rule_id: str):
        self.intervals.append((start_ip, end_ip, rule_id))
        self.intervals.sort()  # Keep sorted for binary search
    
    def find_overlapping(self, ip_int: int) -> List[str]:
        """Find all ranges that contain the given IP"""
        result = []
        for start, end, rule_id in self.intervals:
            if start <= ip_int <= end:
                result.append(rule_id)
            elif start > ip_int:
                break  # No more possible matches
        return result
```

### 5. CIDR Block Matching

```python
def _cidr_match(self, ip_obj) -> bool:
    """
    Check if IP belongs to any blocked CIDR blocks
    Uses network containment check
    """
    # Get all active CIDR blocks from database
    query = """
    SELECT cidr_notation 
    FROM IPRange 
    WHERE cidr_notation IS NOT NULL 
    AND is_active = true
    """
    
    cidr_blocks = self.db.execute(query)
    
    for cidr_row in cidr_blocks:
        cidr_notation = cidr_row['cidr_notation']
        network = ipaddress.ip_network(cidr_notation, strict=False)
        
        if ip_obj in network:
            return True
    
    return False

# Optimized CIDR matching using Trie structure
class CIDRTrie:
    def __init__(self):
        self.root = {}
    
    def add_cidr(self, cidr: str, rule_id: str):
        """Add CIDR block to trie for fast lookup"""
        network = ipaddress.ip_network(cidr, strict=False)
        
        # Convert network to binary representation
        network_bits = format(int(network.network_address), '032b')[:network.prefixlen]
        
        current = self.root
        for bit in network_bits:
            if bit not in current:
                current[bit] = {}
            current = current[bit]
        
        current['_rule'] = rule_id
    
    def find_matching_cidr(self, ip: str) -> Optional[str]:
        """Find if IP matches any CIDR block"""
        ip_obj = ipaddress.ip_address(ip)
        ip_bits = format(int(ip_obj), '032b')
        
        current = self.root
        last_rule = None
        
        for bit in ip_bits:
            if '_rule' in current:
                last_rule = current['_rule']
            
            if bit not in current:
                break
            current = current[bit]
        
        # Check final position
        if '_rule' in current:
            last_rule = current['_rule']
        
        return last_rule
```

### 6. Geographic Matching

```python
def _geographic_match(self, ip_address: str) -> bool:
    """
    Check if IP's geographic location is blocked
    Uses MaxMind GeoIP database
    """
    # Get geographic information for IP
    geo_info = self.geoip_service.get_location(ip_address)
    
    if not geo_info:
        return False
    
    # Check country-level blocking
    query = """
    SELECT gr.rule_id 
    FROM GeoLocation gl
    JOIN BlockingRule br ON gl.geo_id = br.geo_location_id
    WHERE gl.country_code = %s 
    AND br.is_active = true
    AND br.rule_type = 'geographic'
    """
    
    country_block = self.db.execute(query, (geo_info.country_code,))
    if country_block:
        return True
    
    # Check region/city level blocking
    if geo_info.region or geo_info.city:
        region_query = """
        SELECT gr.rule_id 
        FROM GeoLocation gl
        JOIN BlockingRule br ON gl.geo_id = br.geo_location_id
        WHERE gl.country_code = %s 
        AND (gl.region = %s OR gl.city = %s)
        AND br.is_active = true
        """
        
        region_block = self.db.execute(region_query, 
                                     (geo_info.country_code, 
                                      geo_info.region, 
                                      geo_info.city))
        if region_block:
            return True
    
    # Check ISP-level blocking
    if geo_info.isp:
        isp_query = """
        SELECT gr.rule_id 
        FROM GeoLocation gl
        JOIN BlockingRule br ON gl.geo_id = br.geo_location_id
        WHERE gl.isp_name = %s 
        AND br.is_active = true
        """
        
        isp_block = self.db.execute(isp_query, (geo_info.isp,))
        if isp_block:
            return True
    
    return False
```

### 7. Behavioral Pattern Matching

```python
def _behavioral_match(self, ip_address: str) -> bool:
    """
    Check if IP exhibits suspicious behavioral patterns
    """
    # Get recent traffic patterns for this IP
    pattern_query = """
    SELECT tp.request_count, tp.violation_count, tp.risk_score
    FROM TrafficPattern tp
    WHERE tp.ip_address = %s 
    AND tp.time_window >= NOW() - INTERVAL 1 HOUR
    """
    
    patterns = self.db.execute(pattern_query, (ip_address,))
    
    for pattern in patterns:
        # Check rate limiting violations
        if pattern['violation_count'] > 5:
            return True
        
        # Check risk score threshold
        if pattern['risk_score'] > 0.8:
            return True
        
        # Check request rate (more than 100 requests per minute)
        if pattern['request_count'] > 100:
            return True
    
    return False
```

### 8. Whitelist Checking

```python
def is_whitelisted(self, ip_address: str) -> bool:
    """
    Check if IP is in whitelist (highest priority)
    """
    query = """
    SELECT w.whitelist_id 
    FROM Whitelist w
    JOIN IPAddress ip ON w.ip_id = ip.ip_id
    WHERE ip.ip_address = %s 
    AND (w.expires_at IS NULL OR w.expires_at > NOW())
    AND w.is_permanent = true
    """
    
    result = self.db.execute(query, (ip_address,))
    return bool(result)
```

### 9. Performance Optimizations

```python
class IPMatchingOptimizations:
    
    def __init__(self):
        # Redis-based caching for hot IPs
        self.redis_cache = RedisCache()
        
        # Pre-computed IP ranges in memory
        self.ip_ranges_cache = self._load_ip_ranges()
        
        # Bloom filters for different rule types
        self.exact_ip_bloom = BloomFilter(capacity=1000000)
        self.cidr_bloom = BloomFilter(capacity=100000)
        self.geo_bloom = BloomFilter(capacity=500000)
    
    def _load_ip_ranges(self):
        """Pre-load all IP ranges into memory for fast lookup"""
        ranges = []
        query = "SELECT start_ip, end_ip, rule_id FROM IPRange WHERE is_active = true"
        
        for row in self.db.execute(query):
            ranges.append({
                'start': row['start_ip'],
                'end': row['end_ip'],
                'rule_id': row['rule_id']
            })
        
        # Sort ranges by start IP for binary search
        return sorted(ranges, key=lambda x: x['start'])
    
    def binary_search_ranges(self, ip_int: int) -> bool:
        """Binary search through sorted IP ranges"""
        left, right = 0, len(self.ip_ranges_cache) - 1
        
        while left <= right:
            mid = (left + right) // 2
            range_obj = self.ip_ranges_cache[mid]
            
            if range_obj['start'] <= ip_int <= range_obj['end']:
                return True
            elif ip_int < range_obj['start']:
                right = mid - 1
            else:
                left = mid + 1
        
        return False
```

### 10. Real-time Updates

```python
class RealTimeIPUpdates:
    
    def __init__(self):
        self.kafka_consumer = KafkaConsumer('ip_rule_updates')
        self.ip_matcher = IPMatcher()
    
    def process_rule_updates(self):
        """Process real-time rule updates from Kafka"""
        for message in self.kafka_consumer:
            update = json.loads(message.value)
            
            if update['type'] == 'ip_block':
                self._update_ip_block(update)
            elif update['type'] == 'range_block':
                self._update_range_block(update)
            elif update['type'] == 'geo_block':
                self._update_geo_block(update)
    
    def _update_ip_block(self, update):
        """Update exact IP blocking rules"""
        ip_address = update['ip_address']
        action = update['action']  # 'block' or 'unblock'
        
        if action == 'block':
            # Add to bloom filter
            self.ip_matcher.blocked_ips_bloom.add(ip_address)
            
            # Update database
            self.db.execute("""
                INSERT INTO IPAddress (ip_address, status, created_at)
                VALUES (%s, 'blocked', NOW())
                ON DUPLICATE KEY UPDATE status = 'blocked'
            """, (ip_address,))
        
        # Invalidate cache
        self.ip_matcher.cache.delete(f"ip_block:{ip_address}")
```

## Performance Characteristics

### Lookup Time Complexity:
- **Exact IP**: O(1) with hash table + bloom filter
- **IP Range**: O(log n) with binary search or interval tree
- **CIDR**: O(k) where k is number of CIDR blocks (optimized with trie)
- **Geographic**: O(1) with proper indexing
- **Overall**: O(log n) worst case, O(1) average case with caching

### Memory Usage:
- **Bloom Filter**: ~10MB for 10M IPs (0.1% false positive rate)
- **IP Range Cache**: ~100MB for 1M ranges
- **Redis Cache**: Configurable (recommended 1-5GB)

### Throughput:
- **Cached Lookups**: 100,000+ requests/second
- **Database Lookups**: 10,000+ requests/second
- **Geographic Lookups**: 5,000+ requests/second

This multi-layered approach ensures both high performance and comprehensive coverage for IP blocking while maintaining sub-millisecond response times for most requests.