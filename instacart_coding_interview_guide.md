# Instacart Virtual Onsite Coding Interview Guide

## Overview
Congratulations on qualifying for Instacart's virtual onsite! Based on extensive research, here's a comprehensive guide to the coding questions and patterns you can expect in your two coding rounds.

## Interview Structure
- **2 Coding Rounds**: 45-60 minutes each
- **Focus**: Practical problem-solving, clean code, and efficient solutions
- **Difficulty**: Medium to Hard LeetCode level
- **Languages**: Python, Java, JavaScript, or your preferred language

## Common Coding Questions by Category

### 1. Array and String Manipulation

#### Two Sum
**Frequency**: Very High
**Description**: Find two integers in a list that sum to a target value.
```python
def two_sum(nums, target):
    num_dict = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in num_dict:
            return [num_dict[complement], i]
        num_dict[num] = i
    return []
```

#### Merge Intervals
**Frequency**: High
**Description**: Merge overlapping intervals.
```python
def merge_intervals(intervals):
    if not intervals:
        return []
    
    intervals.sort(key=lambda x: x[0])
    merged = [intervals[0]]
    
    for interval in intervals[1:]:
        if interval[0] <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], interval[1])
        else:
            merged.append(interval)
    
    return merged
```

#### Data Pivoting
**Frequency**: Medium
**Description**: Transform data structures (e.g., converting between row/column formats)
- Think about hash maps and nested structures
- Consider time/space complexity trade-offs

### 2. Pattern Matching and String Processing

#### Wildcard Pattern Matching
**Frequency**: High
**Description**: Implement pattern matching with '?' (single char) and '*' (any sequence)
```python
def is_match(string, pattern):
    m, n = len(string), len(pattern)
    dp = [[False] * (n + 1) for _ in range(m + 1)]
    dp[0][0] = True
    
    # Handle patterns starting with *
    for j in range(1, n + 1):
        if pattern[j - 1] == '*':
            dp[0][j] = dp[0][j - 1]
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if pattern[j - 1] == '*':
                dp[i][j] = dp[i - 1][j] or dp[i][j - 1]
            elif pattern[j - 1] == '?' or string[i - 1] == pattern[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
    
    return dp[m][n]
```

#### Anagram Detection
**Frequency**: Medium
**Description**: Check if two strings are anagrams
```python
def is_anagram(s1, s2):
    return sorted(s1) == sorted(s2)
    # OR use character frequency counting for O(n) solution
```

### 3. Data Structure Design

#### LRU Cache
**Frequency**: High
**Description**: Implement Least Recently Used cache with O(1) get/put
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)
```

#### Key-Value Store with Timestamps
**Frequency**: High
**Description**: Store historical values with timestamp-based queries
```python
from collections import defaultdict
import bisect
import time

class KVStore:
    def __init__(self):
        self.store = defaultdict(list)
    
    def set(self, key, value):
        timestamp = time.time()
        self.store[key].append((timestamp, value))
        return timestamp
    
    def get(self, key, timestamp=None):
        if key not in self.store:
            return None
        values = self.store[key]
        if timestamp is None:
            return values[-1][1]
        # Binary search for the right timestamp
        i = bisect.bisect_right(values, (timestamp, chr(255)))
        if i == 0:
            return None
        return values[i - 1][1]
```

### 4. Algorithm Implementation

#### Flood Fill Algorithm
**Frequency**: Medium
**Description**: Change color of a region (like paint bucket tool)
```python
def flood_fill(image, sr, sc, new_color):
    if not image or image[sr][sc] == new_color:
        return image
    
    old_color = image[sr][sc]
    rows, cols = len(image), len(image[0])
    
    def dfs(r, c):
        if r < 0 or r >= rows or c < 0 or c >= cols or image[r][c] != old_color:
            return
        image[r][c] = new_color
        dfs(r+1, c)
        dfs(r-1, c)
        dfs(r, c+1)
        dfs(r, c-1)
    
    dfs(sr, sc)
    return image
```

#### Expression Evaluation
**Frequency**: Medium
**Description**: Evaluate mathematical expressions with operators
- Use stack-based approach
- Handle operator precedence
- Consider parentheses

### 5. E-commerce Specific Problems

#### Delivery Route Optimization (TSP variant)
**Frequency**: Medium
**Description**: Find shortest path visiting all delivery locations
```python
# Simplified approach using nearest neighbor heuristic
def optimize_delivery_route(locations):
    if len(locations) <= 1:
        return locations
    
    route = [locations[0]]
    unvisited = set(locations[1:])
    
    while unvisited:
        current = route[-1]
        nearest = min(unvisited, key=lambda loc: distance(current, loc))
        route.append(nearest)
        unvisited.remove(nearest)
    
    return route

def distance(loc1, loc2):
    return ((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)**0.5
```

#### Inventory Management
**Frequency**: Low-Medium
**Description**: Track product quantities across stores
- Consider concurrent updates
- Handle out-of-stock scenarios
- Implement reservation systems

### 6. Parsing and Input Processing

#### Password Generator
**Frequency**: Medium
**Description**: Parse input and generate passwords based on rules
```python
import random
import string

def generate_password(length=12, use_digits=True, use_special=True):
    chars = string.ascii_letters
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    
    # Ensure at least one of each required type
    password = []
    password.append(random.choice(string.ascii_lowercase))
    password.append(random.choice(string.ascii_uppercase))
    if use_digits:
        password.append(random.choice(string.digits))
    if use_special:
        password.append(random.choice(string.punctuation))
    
    # Fill remaining length
    for _ in range(len(password), length):
        password.append(random.choice(chars))
    
    random.shuffle(password)
    return ''.join(password)
```

#### Card Game Winning Hand
**Frequency**: Low
**Description**: Determine winning hand (3 cards with all same or all different properties)
```python
def is_winning_hand(cards):
    # Assuming cards have properties like color, shape, number
    if len(cards) != 3:
        return False
    
    properties = ['color', 'shape', 'number']
    
    for prop in properties:
        values = [getattr(card, prop) for card in cards]
        # Check if all same or all different
        if not (len(set(values)) == 1 or len(set(values)) == 3):
            return False
    
    return True
```

### 7. Tree and Graph Problems

#### Binary Search Tree Operations
**Frequency**: Medium
**Description**: Implement BST with insert, search, delete
```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class BST:
    def __init__(self):
        self.root = None
    
    def insert(self, val):
        self.root = self._insert_helper(self.root, val)
    
    def _insert_helper(self, node, val):
        if not node:
            return TreeNode(val)
        if val < node.val:
            node.left = self._insert_helper(node.left, val)
        else:
            node.right = self._insert_helper(node.right, val)
        return node
    
    def search(self, val):
        return self._search_helper(self.root, val)
    
    def _search_helper(self, node, val):
        if not node:
            return False
        if node.val == val:
            return True
        if val < node.val:
            return self._search_helper(node.left, val)
        return self._search_helper(node.right, val)
```

## Key Tips for Success

### 1. Communication
- **Think out loud**: Explain your approach before coding
- **Ask clarifying questions**: Input constraints, edge cases, expected output
- **Discuss trade-offs**: Time vs space complexity

### 2. Problem-Solving Approach
1. **Understand the problem** completely
2. **Work through examples** on the whiteboard/screen
3. **Start with brute force**, then optimize
4. **Consider edge cases**: empty input, single element, duplicates
5. **Test your solution** with examples

### 3. Code Quality
- Write **clean, readable code**
- Use **meaningful variable names**
- Add **comments** for complex logic
- Consider **error handling**
- Follow language-specific **conventions**

### 4. Time Management
- Spend 5-10 minutes understanding and planning
- Leave 5-10 minutes for testing and optimization
- Don't get stuck - ask for hints if needed

### 5. Common Pitfalls to Avoid
- Don't jump to coding immediately
- Don't ignore edge cases
- Don't forget to analyze complexity
- Don't use obscure language features
- Don't panic if you don't know the optimal solution immediately

## Practice Resources

### LeetCode Problems to Focus On
1. **Arrays**: #1, #15, #56, #57, #88, #169
2. **Strings**: #125, #242, #438, #567, #647
3. **Hash Tables**: #1, #49, #146, #380
4. **Trees**: #94, #98, #102, #104, #226
5. **Dynamic Programming**: #70, #121, #198, #300
6. **Design**: #146 (LRU), #380 (Insert Delete GetRandom)

### System Design Topics
- Database design for e-commerce
- Caching strategies
- Load balancing
- Microservices architecture
- Real-time inventory tracking
- Payment processing systems

## Final Interview Day Checklist
- [ ] Test your setup (camera, microphone, internet)
- [ ] Have water and notepad ready
- [ ] Review this guide and your practice problems
- [ ] Prepare questions about Instacart's tech stack
- [ ] Get good rest the night before
- [ ] Join 5 minutes early

## Behavioral Round Preparation
Be ready to discuss:
- Your experience with large-scale systems
- How you handle technical challenges
- Examples of leadership and collaboration
- Why Instacart specifically
- Your approach to code reviews and mentoring

## Architecture Round Preparation
Common topics:
- Design an inventory management system
- Design a real-time order tracking system
- Design a recommendation engine for groceries
- Design a shopper assignment algorithm
- Scalability considerations for peak hours

Good luck with your interviews! Remember, they're evaluating not just your coding ability but also your problem-solving approach, communication skills, and how you handle feedback.