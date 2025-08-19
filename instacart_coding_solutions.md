# Instacart Coding Interview Solutions

This document provides sample implementations for common Instacart coding interview questions.

## 1. Longest Common Subarray

```python
def longest_common_subarray(arr1, arr2):
    """
    Find the longest contiguous subarray that appears in both arrays.
    Time: O(n * m), Space: O(n * m)
    """
    if not arr1 or not arr2:
        return []
    
    n, m = len(arr1), len(arr2)
    # dp[i][j] = length of common subarray ending at arr1[i-1] and arr2[j-1]
    dp = [[0] * (m + 1) for _ in range(n + 1)]
    
    max_length = 0
    ending_pos = 0
    
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if arr1[i-1] == arr2[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
                if dp[i][j] > max_length:
                    max_length = dp[i][j]
                    ending_pos = i
    
    return arr1[ending_pos - max_length:ending_pos]

# Test
arr1 = [1, 2, 3, 2, 1]
arr2 = [3, 2, 1, 4, 7]
print(longest_common_subarray(arr1, arr2))  # [3, 2, 1]
```

## 2. Ad Click Analysis

```python
def analyze_ad_clicks(purchase_user_ids, ad_clicks, user_ip_map):
    """
    Analyze ad clicks to determine click counts and conversions.
    Returns: Dict[ad_text] -> (total_clicks, purchase_clicks)
    """
    # Create reverse mapping: IP -> UserID
    ip_to_user = {ip: user for user, ip in user_ip_map.items()}
    
    # Track purchaser set
    purchasers = set(purchase_user_ids)
    
    # Parse ad clicks
    ad_stats = {}  # ad_text -> [total_clicks, purchase_clicks]
    
    for click_log in ad_clicks:
        parts = click_log.split(',', 2)
        if len(parts) != 3:
            continue
            
        ip, timestamp, ad_text = parts
        
        # Initialize if new ad
        if ad_text not in ad_stats:
            ad_stats[ad_text] = [0, 0]
        
        # Count total click
        ad_stats[ad_text][0] += 1
        
        # Check if click led to purchase
        user = ip_to_user.get(ip)
        if user and user in purchasers:
            ad_stats[ad_text][1] += 1
    
    return ad_stats

# Test
purchase_user_ids = ["user1", "user2"]
ad_clicks = [
    "122.121.0.1,2016-11-03 11:41:19,Buy wool coats",
    "96.3.199.11,2016-10-15 20:18:31,2900 fish tanks",
    "122.121.0.1,2016-11-03 11:41:35,Buy wool coats",
    "96.3.199.11,2016-10-15 20:18:40,2900 fish tanks"
]
user_ip_map = {
    "user1": "122.121.0.1",
    "user2": "96.3.199.11",
    "user3": "10.0.0.1"
}

result = analyze_ad_clicks(purchase_user_ids, ad_clicks, user_ip_map)
for ad, (clicks, purchases) in result.items():
    print(f"{ad}: {clicks} clicks, {purchases} purchases")
```

## 3. Badge In/Out Analysis

```python
def find_badge_mismatches(records):
    """
    Find employees who forgot to badge in or out.
    Returns: (entered_without_exit, exited_without_enter)
    """
    # Current state: True = inside, False = outside
    employee_state = {}
    
    # Track mismatches
    entered_without_exit = set()
    exited_without_enter = set()
    
    for name, action in records:
        current_inside = employee_state.get(name, False)
        
        if action == "enter":
            if current_inside:
                # Already inside, entering again
                entered_without_exit.add(name)
            employee_state[name] = True
        else:  # exit
            if not current_inside:
                # Not inside, but exiting
                exited_without_enter.add(name)
            employee_state[name] = False
    
    # Check final states
    for name, inside in employee_state.items():
        if inside:
            entered_without_exit.add(name)
    
    return sorted(entered_without_exit), sorted(exited_without_enter)

# Test
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

entered, exited = find_badge_mismatches(records)
print(f"Entered without exit: {entered}")
print(f"Exited without enter: {exited}")
```

## 4. Frequent Access Detection

```python
def find_frequent_access(access_logs):
    """
    Find users who accessed >3 times within any 1-hour window.
    Returns: Dict[user] -> List of 1-hour windows with >3 accesses
    """
    from collections import defaultdict
    
    # Group by user
    user_accesses = defaultdict(list)
    for user, timestamp in access_logs:
        user_accesses[user].append(int(timestamp))
    
    result = {}
    
    for user, times in user_accesses.items():
        times.sort()
        
        # Sliding window approach
        windows = []
        i = 0
        
        for j in range(len(times)):
            # Move window start to maintain 1-hour constraint
            while i < j and times[j] - times[i] >= 60:
                i += 1
            
            # Check if window has >3 accesses
            window_size = j - i + 1
            if window_size > 3:
                window_times = times[i:j+1]
                if not windows or window_times != windows[-1]:
                    windows.append(window_times)
        
        if windows:
            result[user] = windows
    
    return result

# Test
access_logs = [
    ["James", "1300"],
    ["Martha", "1600"],
    ["Martha", "1620"],
    ["Martha", "1530"],
    ["James", "1315"],
    ["Martha", "1615"],
    ["James", "1305"],
    ["Martha", "1545"],
    ["Martha", "1555"]
]

frequent_users = find_frequent_access(access_logs)
for user, windows in frequent_users.items():
    print(f"{user}: {windows}")
```

## 5. Formula Evaluation (Graph-Based)

```python
def evaluate_formulas(formulas, target):
    """
    Evaluate formulas with dependencies using graph traversal.
    """
    import re
    from collections import defaultdict
    
    # Parse formulas
    graph = defaultdict(list)  # variable -> (operator, operands)
    values = {}  # variable -> computed value
    
    for formula in formulas:
        parts = formula.split('=')
        if len(parts) != 2:
            continue
            
        var = parts[0].strip()
        expr = parts[1].strip()
        
        # Check if it's a constant
        try:
            values[var] = float(expr)
        except:
            # Parse expression (simple format: VAR op VAR)
            tokens = expr.split()
            if len(tokens) == 3:
                operand1, op, operand2 = tokens
                graph[var] = (op, [operand1, operand2])
            elif len(tokens) == 1:
                # Direct assignment
                graph[var] = ('=', [tokens[0]])
    
    # DFS to evaluate target
    def evaluate(var):
        if var in values:
            return values[var]
        
        if var not in graph:
            # Try to parse as number
            try:
                return float(var)
            except:
                raise ValueError(f"Unknown variable: {var}")
        
        op, operands = graph[var]
        
        if op == '=':
            values[var] = evaluate(operands[0])
        elif op == '+':
            values[var] = evaluate(operands[0]) + evaluate(operands[1])
        elif op == '-':
            values[var] = evaluate(operands[0]) - evaluate(operands[1])
        elif op == '*':
            values[var] = evaluate(operands[0]) * evaluate(operands[1])
        elif op == '/':
            values[var] = evaluate(operands[0]) / evaluate(operands[1])
        
        return values[var]
    
    return evaluate(target)

# Test
formulas = [
    "T1 = T2 + T3",
    "T2 = 3",
    "T3 = 5",
    "T4 = T1 * 2"
]
print(evaluate_formulas(formulas, "T4"))  # 16
```

## 6. Banking System Design

```python
import heapq
from collections import defaultdict

class BankingSystem:
    def __init__(self):
        self.accounts = {}  # account_id -> balance
        self.transactions = []  # Min heap of (-amount, transaction_details)
        self.transaction_id = 0
    
    def create_account(self, account_id):
        """Create a new account."""
        if account_id in self.accounts:
            return False
        self.accounts[account_id] = 0
        return True
    
    def deposit(self, account_id, amount):
        """Deposit money into an account."""
        if account_id not in self.accounts or amount <= 0:
            return False
        
        self.accounts[account_id] += amount
        self.transaction_id += 1
        
        # Store transaction (negative amount for max heap behavior)
        transaction = {
            'id': self.transaction_id,
            'type': 'deposit',
            'account': account_id,
            'amount': amount
        }
        heapq.heappush(self.transactions, (-amount, self.transaction_id, transaction))
        return True
    
    def transfer(self, from_account, to_account, amount):
        """Transfer money between accounts."""
        if (from_account not in self.accounts or 
            to_account not in self.accounts or 
            from_account == to_account or
            amount <= 0 or
            self.accounts[from_account] < amount):
            return False
        
        self.accounts[from_account] -= amount
        self.accounts[to_account] += amount
        self.transaction_id += 1
        
        transaction = {
            'id': self.transaction_id,
            'type': 'transfer',
            'from': from_account,
            'to': to_account,
            'amount': amount
        }
        heapq.heappush(self.transactions, (-amount, self.transaction_id, transaction))
        return True
    
    def get_top_k_transactions(self, k):
        """Get top K transactions by amount."""
        # Create a copy of transactions heap
        temp_heap = self.transactions.copy()
        result = []
        
        for _ in range(min(k, len(temp_heap))):
            neg_amount, tid, transaction = heapq.heappop(temp_heap)
            result.append(transaction)
        
        return result

# Test
bank = BankingSystem()
bank.create_account("acc1")
bank.create_account("acc2")
bank.deposit("acc1", 1000)
bank.deposit("acc2", 500)
bank.transfer("acc1", "acc2", 200)
print(bank.get_top_k_transactions(2))
```

## 7. Tile Movement Simulation

```python
def generate_tile_moves(board):
    """
    Generate all possible moves for tiles on a 1D board.
    R = Red (moves right), B = Black (moves left), _ = Empty
    """
    moves = []
    n = len(board)
    
    for i in range(n):
        if board[i] == 'R':
            # Red tile moves right
            # Adjacent move
            if i + 1 < n and board[i + 1] == '_':
                new_board = board.copy()
                new_board[i], new_board[i + 1] = '_', 'R'
                moves.append(('R', i, i + 1, new_board))
            
            # Jump move
            if i + 2 < n and board[i + 1] == 'B' and board[i + 2] == '_':
                new_board = board.copy()
                new_board[i], new_board[i + 2] = '_', 'R'
                moves.append(('R', i, i + 2, new_board))
                
        elif board[i] == 'B':
            # Black tile moves left
            # Adjacent move
            if i - 1 >= 0 and board[i - 1] == '_':
                new_board = board.copy()
                new_board[i], new_board[i - 1] = '_', 'B'
                moves.append(('B', i, i - 1, new_board))
            
            # Jump move
            if i - 2 >= 0 and board[i - 1] == 'R' and board[i - 2] == '_':
                new_board = board.copy()
                new_board[i], new_board[i - 2] = '_', 'B'
                moves.append(('B', i, i - 2, new_board))
    
    return moves

# Test
board = ['R', 'B', '_', 'R', 'B']
moves = generate_tile_moves(board)
for color, from_pos, to_pos, new_board in moves:
    print(f"{color} from {from_pos} to {to_pos}: {''.join(new_board)}")
```

## Key Takeaways

1. **Time Complexity Matters**: Always analyze and state the time/space complexity
2. **Edge Cases**: Handle empty inputs, invalid data, boundary conditions
3. **Code Quality**: Write clean, readable code with meaningful variable names
4. **Testing**: Include test cases to demonstrate your solution works
5. **Communication**: Explain your approach before and during coding
6. **Optimization**: Be ready to discuss trade-offs and potential improvements

## Common Patterns in Instacart Problems

1. **Real-world Scenarios**: Problems often simulate actual business use cases
2. **Data Processing**: Many problems involve parsing and analyzing log data
3. **System Design Elements**: Even coding problems may have design aspects
4. **Multiple Data Sources**: Often need to correlate data from different inputs
5. **Time-based Analysis**: Sliding windows, intervals, and timestamp processing