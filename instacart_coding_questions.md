# Instacart Virtual Onsite Coding Questions

This document contains a comprehensive collection of coding questions asked during Instacart's virtual onsite interviews, primarily sourced from 1point3acres (一亩三分地) forum.

## Overview
Instacart's virtual onsite typically includes multiple coding rounds focusing on:
- Algorithmic problem-solving
- Data structure manipulation
- System design (for senior positions)
- Real-world problem simulation

## Detailed Coding Questions

### 1. Longest Common Subarray (Dynamic Programming)
**Problem:** Find the longest contiguous subarray that appears in two given arrays.

**Example:**
```
Input: arr1 = [1, 2, 3, 2, 1], arr2 = [3, 2, 1, 4, 7]
Output: [3, 2, 1] (length = 3)
```

**Approach:** Use dynamic programming with a 2D table to track matching subarrays.

**Time Complexity:** O(n × m) where n and m are the lengths of the arrays
**Space Complexity:** O(n × m)

---

### 2. Ad Click Analysis
**Problem:** Analyze ad click data to determine click counts and conversion rates.

**Given Data:**
- List of user IDs who completed purchases
- Raw log data: ad clicks with IP addresses and timestamps
- Mapping of user IDs to IP addresses

**Task:** For each ad, return:
- Ad text
- Total number of clicks
- Number of clicks that resulted in purchases

**Example Format:**
```
purchaseUserIds = ["user1", "user2", "user3"]
adClicks = [
    "122.121.0.1,2016-11-03 11:41:19,Buy wool coats for your pets",
    "96.3.199.11,2016-10-15 20:18:31,2900 fish tanks on sale",
    "122.121.0.1,2016-11-03 11:41:35,Buy wool coats for your pets"
]
userIpMap = {
    "user1": "122.121.0.1",
    "user2": "96.3.199.11",
    "user3": "10.0.0.1"
}
```

**Approach:** Parse logs, correlate IPs with users, count clicks and conversions.

---

### 3. Badge In/Out Records Analysis
**Problem:** Identify employees who forgot to badge in or out.

**Input Format:**
```
records = [
    ["Martha", "exit"],
    ["Paul", "enter"],
    ["Martha", "enter"],
    ["Martha", "exit"],
    ["Jennifer", "enter"],
    ["Paul", "enter"],
    ["Curtis", "enter"],
    ["Paul", "exit"],
    ["Martha", "enter"],
    ["Martha", "exit"],
    ["Jennifer", "exit"]
]
```

**Expected Output:**
- People who entered without exiting
- People who exited without entering

**Approach:** Track state for each person, validate enter/exit sequences.

---

### 4. Frequent Access Detection
**Problem:** Find users who accessed the system more than 3 times within any 1-hour window.

**Input Format:**
```
access_logs = [
    ["James", "1300"],
    ["Martha", "1600"],
    ["Martha", "1620"],
    ["Martha", "1530"],
    ["James", "1315"],
    ["Martha", "1615"],
    ["James", "1305"]
]
```

**Output:** Users and their access times within the 1-hour windows where they exceeded 3 accesses.

**Approach:** Use sliding window technique, sort by timestamp per user.

---

### 5. Valid Sudoku Variant
**Problem:** Validate a Sudoku board configuration.

**Rules:**
- Each row must contain unique digits 1-9
- Each column must contain unique digits 1-9
- Each 3×3 sub-box must contain unique digits 1-9

**Approach:** Use hash sets to track seen numbers in rows, columns, and boxes.

---

### 6. Password Decryption
**Problem:** Decrypt passwords from a file based on given indices.

**Example:**
```
File content: "helloworld"
Indices: [1, 5, 3, 9, 0]
Result: "ewdlh"
```

**Approach:** Read file, extract characters at specified indices.

---

### 7. Banking System Design
**Problem:** Implement a simple banking system with the following features:
- Create account
- Deposit money
- Transfer funds between accounts
- Get top K transactions by amount

**Key Methods:**
```python
class BankingSystem:
    def createAccount(self, accountId: str) -> bool
    def deposit(self, accountId: str, amount: int) -> bool
    def transfer(self, fromAccount: str, toAccount: str, amount: int) -> bool
    def getTopKTransactions(self, k: int) -> List[Transaction]
```

**Approach:** Use dictionaries for accounts, heap for top K transactions.

---

### 8. Formula Evaluation (Graph-Based)
**Problem:** Evaluate formulas with variable dependencies.

**Example:**
```
formulas = [
    "T1 = T2 + T3",
    "T2 = 3",
    "T3 = 5",
    "T4 = T1 * 2"
]
target = "T4"
Output: 16
```

**Approach:** Build dependency graph, topological sort or DFS evaluation.

---

### 9. Tile Movement Simulation
**Problem:** Simulate red and black tile movements on a 1D board.

**Rules:**
- Red tiles move right only
- Black tiles move left only
- Tiles can move to adjacent empty space
- Tiles can jump over one opposite-color tile to empty space

**Example:**
```
Initial: [R, B, _, R, B]
Possible moves for red tiles, possible moves for black tiles
```

**Approach:** Generate all valid moves, implement game state transitions.

---

### 10. Job Scheduling Optimization
**Problem:** Select jobs to maximize profit within time constraint (Knapsack variant).

**Input:**
```
jobs = [(duration1, profit1), (duration2, profit2), ...]
totalTime = T
```

**Task:** Select subset of jobs to maximize profit without exceeding total time.

**Approach:** Dynamic programming, similar to 0/1 knapsack problem.

---

## Additional Patterns Observed

### Common Topics:
1. **String/Array Manipulation** - Parsing, searching, pattern matching
2. **Hash Tables** - Counting, grouping, deduplication
3. **Dynamic Programming** - Optimization problems, subsequence problems
4. **Graph Algorithms** - Dependency resolution, traversal
5. **System Design** - Object-oriented design, data structures
6. **Time-based Analysis** - Sliding windows, interval problems

### Difficulty Level:
- Most problems are LeetCode Medium level
- Some Easy problems for warm-up
- Occasionally Hard problems for senior positions

### Interview Format:
- Usually 2-3 coding rounds
- 45-60 minutes per round
- Expected to write working code
- Discussion of time/space complexity
- Follow-up questions on optimization

## Preparation Tips

1. **Practice on LeetCode** - Focus on Medium difficulty problems
2. **Time Management** - Aim to solve problems in 30-40 minutes
3. **Communication** - Explain your approach before coding
4. **Edge Cases** - Always consider and handle edge cases
5. **Testing** - Write test cases to validate your solution
6. **Optimization** - Be prepared to discuss and implement optimizations

## LeetCode Equivalents and Similar Problems

### Problem Mappings:
1. **Longest Common Subarray** → Similar to LeetCode #718 "Maximum Length of Repeated Subarray"
2. **Valid Sudoku** → LeetCode #36 "Valid Sudoku"
3. **Badge In/Out** → Similar to LeetCode #1396 "Design Underground System"
4. **Frequent Access** → Similar to sliding window problems like LeetCode #438
5. **Banking System** → Similar to LeetCode #1396, #2043 "Simple Bank System"
6. **Job Scheduling** → LeetCode #1235 "Maximum Profit in Job Scheduling"
7. **Formula Evaluation** → Similar to LeetCode #399 "Evaluate Division"

### Additional Problems Reported:
- **Key-Value Store Implementation** - Design problem similar to LeetCode #146 "LRU Cache"
- **Graph Traversal Problems** - Various dependency resolution problems
- **String Parsing and Manipulation** - Custom problems not directly on LeetCode

## Interview Experience Insights

### From Recent Candidates (2023-2024):
1. **Round Structure:**
   - Usually 3-4 rounds total
   - 2-3 coding rounds (45-60 minutes each)
   - 1 system design (for senior roles)
   - 1 behavioral round

2. **Coding Environment:**
   - CoderPad or similar online IDE
   - Expected to write compilable code
   - Test cases often provided
   - Discussion of complexity expected

3. **Difficulty Distribution:**
   - Round 1: Usually easier (LeetCode Easy-Medium)
   - Round 2: Medium-Hard difficulty
   - Focus on practical problems over pure algorithms

## Notes
- Questions may vary by position level and team
- Recent interviews (2023-2024) show consistent patterns
- Real-world problem scenarios are common
- Clean, readable code is valued
- They appreciate candidates who ask clarifying questions
- Edge case handling is important

---

*Source: Compiled from multiple interview experiences shared on 1point3acres.com*
*Last Updated: Based on available information through 2024*