from fpdf import FPDF
import os


OUTPUT_DIR = "/workspace/instacart-cheatsheets"
os.makedirs(OUTPUT_DIR, exist_ok=True)


# Keep content ASCII-only for core PDF fonts
PROBLEMS = [
    {
        "title": "Password Decryption",
        "statement": (
            "Given an encrypted string and a list of indices indicating the sequence "
            "to read characters, reconstruct the original password."
        ),
        "variants": [
            "Multiple records: decrypt a batch of strings with corresponding index lists.",
            "File-based: input file contains alternating lines of cipher and indices.",
            "Index format variations: spaces/commas; out-of-range indices; duplicates.",
        ],
        "leverage": (
            "Normalize and parse indices once, then apply the same O(n) indexing to build the result."
        ),
        "java": r'''import java.util.*;
import java.io.*;
import java.nio.file.*;

public final class PasswordDecryptor {
	public static String decryptByIndices(String cipher, List<Integer> indices) {
		if (cipher == null || indices == null) return "";
		StringBuilder builder = new StringBuilder(indices.size());
		for (int index : indices) {
			if (index < 0 || index >= cipher.length()) {
				throw new IllegalArgumentException("Index out of bounds: " + index);
			}
			builder.append(cipher.charAt(index));
		}
		return builder.toString();
	}

	public static List<String> decryptBatch(List<String> ciphers, List<List<Integer>> indicesLists) {
		if (ciphers.size() != indicesLists.size()) {
			throw new IllegalArgumentException("Mismatched batch sizes");
		}
		List<String> results = new ArrayList<>(ciphers.size());
		for (int i = 0; i < ciphers.size(); i++) {
			results.add(decryptByIndices(ciphers.get(i), indicesLists.get(i)));
		}
		return results;
	}

	public static List<String> decryptFromFile(Path file) throws IOException {
		List<String> decrypted = new ArrayList<>();
		try (BufferedReader reader = Files.newBufferedReader(file)) {
			String cipherLine;
			while ((cipherLine = reader.readLine()) != null) {
				String indicesLine = reader.readLine();
				if (indicesLine == null) break;
				String cipher = parseAfterColon(cipherLine);
				List<Integer> indices = parseIndices(parseAfterColon(indicesLine));
				decrypted.add(decryptByIndices(cipher, indices));
			}
		}
		return decrypted;
	}

	private static String parseAfterColon(String line) {
		int idx = line.indexOf(':');
		return idx >= 0 ? line.substring(idx + 1).trim() : line.trim();
	}

	private static List<Integer> parseIndices(String s) {
		if (s.isEmpty()) return Collections.emptyList();
		String[] parts = s.split("[,\\s]+");
		List<Integer> result = new ArrayList<>(parts.length);
		for (String p : parts) {
			if (p.isEmpty()) continue;
			result.add(Integer.parseInt(p));
		}
		return result;
	}
}
'''
    },
    {
        "title": "Expression Evaluation (Dependency Graph)",
        "statement": (
            "Given equations like T1=2, T3=T1+T2, and a target variable, evaluate the "
            "target by resolving dependencies."
        ),
        "variants": [
            "Operators: + - * /",
            "Aliases: T2 = T3",
            "Mix constants and variables; detect cycles/undefined variables.",
        ],
        "leverage": (
            "Build a graph and use DFS with memoization; add cycle/undefined checks once."
        ),
        "java": r'''import java.util.*;

public final class ExpressionGraph {
	private final Map<String, Node> variableToNode = new HashMap<>();

	public static ExpressionGraph fromEquations(List<String> equations) {
		ExpressionGraph graph = new ExpressionGraph();
		for (String eq : equations) {
			graph.addEquation(eq);
		}
		return graph;
	}

	public double evaluate(String target) {
		Map<String, Double> memo = new HashMap<>();
		Set<String> visiting = new HashSet<>();
		return evaluateVar(target, memo, visiting);
	}

	private void addEquation(String equation) {
		String[] parts = equation.split("=");
		if (parts.length != 2) throw new IllegalArgumentException("Bad equation: " + equation);
		String lhs = parts[0].trim();
		String rhs = parts[1].trim();
		Node node = parseRhs(rhs);
		variableToNode.put(lhs, node);
	}

	private static Node parseRhs(String rhs) {
		String[] tokens = rhs.split("\\s+");
		if (tokens.length == 1) {
			Term term = parseTerm(tokens[0]);
			if (term.isConst) return Node.constant(term.value);
			else return Node.identity(term.variableName);
		} else if (tokens.length == 3) {
			Term left = parseTerm(tokens[0]);
			char op = tokens[1].charAt(0);
			Term right = parseTerm(tokens[2]);
			return Node.binary(left, op, right);
		}
		throw new IllegalArgumentException("Unsupported RHS: " + rhs);
	}

	private static Term parseTerm(String token) {
		if (isNumber(token)) return Term.constant(Double.parseDouble(token));
		return Term.variable(token);
	}

	private static boolean isNumber(String s) {
		try { Double.parseDouble(s); return true; }
		catch (NumberFormatException e) { return false; }
	}

	private double evaluateVar(String name, Map<String, Double> memo, Set<String> visiting) {
		if (memo.containsKey(name)) return memo.get(name);
		if (visiting.contains(name)) throw new IllegalStateException("Cycle detected at " + name);
		Node node = variableToNode.get(name);
		if (node == null) throw new IllegalArgumentException("Undefined variable: " + name);

		visiting.add(name);
		double result;
		if (node.kind == NodeKind.CONST) result = node.constantValue;
		else if (node.kind == NodeKind.IDENTITY) result = resolveTerm(node.left, memo, visiting);
		else {
			double leftVal = resolveTerm(node.left, memo, visiting);
			double rightVal = resolveTerm(node.right, memo, visiting);
			switch (node.op) {
				case '+': result = leftVal + rightVal; break;
				case '-': result = leftVal - rightVal; break;
				case '*': result = leftVal * rightVal; break;
				case '/': result = leftVal / rightVal; break;
				default: throw new IllegalArgumentException("Unknown op: " + node.op);
			}
		}
		visiting.remove(name);
		memo.put(name, result);
		return result;
	}

	private double resolveTerm(Term term, Map<String, Double> memo, Set<String> visiting) {
		if (term.isConst) return term.value;
		return evaluateVar(term.variableName, memo, visiting);
	}

	private enum NodeKind { CONST, IDENTITY, BINARY }

	private static final class Node {
		final NodeKind kind;
		final double constantValue;
		final char op;
		final Term left, right;
		private Node(NodeKind kind, double constantValue, char op, Term left, Term right) {
			this.kind = kind; this.constantValue = constantValue; this.op = op; this.left = left; this.right = right;
		}
		static Node constant(double v) { return new Node(NodeKind.CONST, v, 0, null, null); }
		static Node identity(String var) { return new Node(NodeKind.IDENTITY, 0, 0, Term.variable(var), null); }
		static Node binary(Term l, char op, Term r) { return new Node(NodeKind.BINARY, 0, op, l, r); }
	}

	private static final class Term {
		final boolean isConst;
		final double value; final String variableName;
		private Term(boolean isConst, double value, String variableName) {
			this.isConst = isConst; this.value = value; this.variableName = variableName;
		}
		static Term constant(double v) { return new Term(true, v, null); }
		static Term variable(String n) { return new Term(false, 0, n); }
	}
}
'''
    },
    {
        "title": "Ad Click Analysis",
        "statement": (
            "Given purchased user IDs, ad click logs (IP, ad text), and a mapping userId->IP, "
            "return each ad's total clicks and clicks that led to purchases."
        ),
        "variants": [
            "Multiple IPs per user; deduplicate repeated clicks",
            "Only count first purchase; inconsistent casing/whitespace",
        ],
        "leverage": (
            "Convert user->IP to IP->user. One pass to count totals and purchase-clicks; add optional (ip,ad) dedup set."
        ),
        "java": r'''import java.util.*;

public final class AdClickAnalytics {
	public static final class AdClick {
		public final String ip; public final String adText;
		public AdClick(String ip, String adText) { this.ip = ip; this.adText = adText; }
	}

	public static Map<String, int[]> analyze(Set<String> purchasedUserIds,
	                                         List<AdClick> clicks,
	                                         Map<String, String> userIdToIp) {
		Map<String, String> ipToUser = new HashMap<>();
		for (Map.Entry<String, String> e : userIdToIp.entrySet()) {
			if (e.getValue() != null) ipToUser.put(e.getValue(), e.getKey());
		}
		Map<String, int[]> result = new HashMap<>();
		for (AdClick c : clicks) {
			String ad = c.adText == null ? "" : c.adText.trim();
			int[] counters = result.computeIfAbsent(ad, k -> new int[2]);
			counters[0]++;
			String user = ipToUser.get(c.ip);
			if (user != null && purchasedUserIds.contains(user)) counters[1]++;
		}
		return result;
	}

	public static Map<String, int[]> analyzeDedup(Set<String> purchasedUserIds,
	                                              List<AdClick> clicks,
	                                              Map<String, String> userIdToIp) {
		Map<String, String> ipToUser = new HashMap<>();
		for (Map.Entry<String, String> e : userIdToIp.entrySet()) {
			if (e.getValue() != null) ipToUser.put(e.getValue(), e.getKey());
		}
		Map<String, int[]> result = new HashMap<>();
		Set<String> seenIpAd = new HashSet<>();
		for (AdClick c : clicks) {
			String ad = c.adText == null ? "" : c.adText.trim();
			String key = c.ip + "\u0000" + ad;
			if (!seenIpAd.add(key)) continue;
			int[] counters = result.computeIfAbsent(ad, k -> new int[2]);
			counters[0]++;
			String user = ipToUser.get(c.ip);
			if (user != null && purchasedUserIds.contains(user)) counters[1]++;
		}
		return result;
	}
}
'''
    },
    {
        "title": "Badge Access: Forgot IN/OUT",
        "statement": (
            "Given logs (name, time, IN/OUT), determine employees who missed an IN or OUT."
        ),
        "variants": [
            "Out-of-order logs; multiple days",
            "Mixed casing; multiple consecutive INs/OUTs",
        ],
        "leverage": (
            "Group per user, sort by time, and scan with a simple state machine."
        ),
        "java": r'''import java.util.*;

public final class BadgeAnomalyDetector {
	public static final class Event {
		public final String employee; public final int minutes; public final boolean isIn;
		public Event(String employee, int minutes, boolean isIn) { this.employee = employee; this.minutes = minutes; this.isIn = isIn; }
	}
	public static final class Result { public final Set<String> forgotIn = new HashSet<>(); public final Set<String> forgotOut = new HashSet<>(); }

	public static Result findForgotInOut(List<Event> events) {
		Map<String, List<Event>> byEmployee = new HashMap<>();
		for (Event e : events) byEmployee.computeIfAbsent(e.employee, k -> new ArrayList<>()).add(e);
		Result result = new Result();
		for (Map.Entry<String, List<Event>> entry : byEmployee.entrySet()) {
			String name = entry.getKey();
			List<Event> list = entry.getValue();
			list.sort(Comparator.comparingInt(ev -> ev.minutes));
			boolean inside = false;
			for (Event e : list) {
				if (e.isIn) {
					if (inside) result.forgotOut.add(name);
					inside = true;
				} else {
					if (!inside) result.forgotIn.add(name);
					inside = false;
				}
			}
			if (inside) result.forgotOut.add(name);
		}
		return result;
	}

	public static int parseTimeToMinutes(String hhmm) {
		String[] p = hhmm.split(":");
		return Integer.parseInt(p[0]) * 60 + Integer.parseInt(p[1]);
	}
}
'''
    },
    {
        "title": "Badge Access: >=3 in 1 Hour",
        "statement": (
            "For each employee, if there exist >=3 badge-ins within any rolling 60-minute window, report the window times."
        ),
        "variants": [
            "Return earliest window only vs all windows",
            "Inclusive boundaries; dedup timestamps",
        ],
        "leverage": (
            "Sort times and use a sliding window; toggle output mode via early-break."
        ),
        "java": r'''import java.util.*;

public final class BadgeFrequencyDetector {
	public static Map<String, List<List<String>>> findAllWindows(Map<String, List<String>> logs) {
		Map<String, List<List<String>>> result = new HashMap<>();
		for (Map.Entry<String, List<String>> e : logs.entrySet()) {
			String name = e.getKey();
			List<Integer> times = new ArrayList<>();
			for (String t : e.getValue()) times.add(parse(t));
			Collections.sort(times);
			int left = 0; List<List<String>> windows = new ArrayList<>();
			for (int right = 0; right < times.size(); right++) {
				while (times.get(right) - times.get(left) > 60) left++;
				if (right - left + 1 >= 3) {
					List<String> win = new ArrayList<>();
					for (int k = left; k <= right; k++) win.add(format(times.get(k)));
					windows.add(win);
				}
			}
			if (!windows.isEmpty()) result.put(name, windows);
		}
		return result;
	}
	private static int parse(String hhmm) { String[] p = hhmm.split(":"); return Integer.parseInt(p[0])*60 + Integer.parseInt(p[1]); }
	private static String format(int minutes) { int h = minutes/60, m = minutes%60; return String.format("%02d:%02d", h, m); }
}
'''
    },
    {
        "title": "Longest Common Subarray",
        "statement": (
            "Given two arrays, find the longest common contiguous subarray."
        ),
        "variants": [
            "Return length only vs subarray",
            "Memory-optimized DP",
        ],
        "leverage": (
            "Use rolling DP; track end index to rebuild the subarray if needed."
        ),
        "java": r'''import java.util.*;

public final class LongestCommonSubarray {
	public static int length(int[] a, int[] b) {
		int n = a.length, m = b.length; int[] dp = new int[m + 1]; int best = 0;
		for (int i = 1; i <= n; i++) {
			int prev = 0;
			for (int j = 1; j <= m; j++) {
				int temp = dp[j];
				if (a[i - 1] == b[j - 1]) { dp[j] = prev + 1; if (dp[j] > best) best = dp[j]; }
				else dp[j] = 0;
				prev = temp;
			}
		}
		return best;
	}
	public static int[] subarray(int[] a, int[] b) {
		int n = a.length, m = b.length; int[] dp = new int[m + 1]; int best = 0, endA = -1;
		for (int i = 1; i <= n; i++) {
			int prev = 0;
			for (int j = 1; j <= m; j++) {
				int temp = dp[j];
				if (a[i - 1] == b[j - 1]) { dp[j] = prev + 1; if (dp[j] > best) { best = dp[j]; endA = i - 1; } }
				else dp[j] = 0;
				prev = temp;
			}
		}
		if (best == 0) return new int[0];
		return Arrays.copyOfRange(a, endA - best + 1, endA + 1);
	}
}
'''
    },
    {
        "title": "Sudoku Validation",
        "statement": (
            "Validate an N x N Sudoku board ensuring no duplicates in rows, columns, and sub-boxes."
        ),
        "variants": [
            "Different board sizes and box dimensions",
            "Partial boards ('.' as empty)",
        ],
        "leverage": (
            "Parameterize box dimensions; same row/col/box set checks."
        ),
        "java": r'''import java.util.*;

public final class SudokuValidator {
	public static boolean isValid(char[][] board) { return isValid(board, 3, 3); }
	public static boolean isValid(char[][] board, int boxRows, int boxCols) {
		int n = board.length; for (char[] row : board) if (row.length != n) throw new IllegalArgumentException("Non-square board");
		Set<Character>[] rows = new Set[n]; Set<Character>[] cols = new Set[n];
		@SuppressWarnings("unchecked") Set<Character>[][] boxes = new Set[n / boxRows][n / boxCols];
		for (int i = 0; i < n; i++) rows[i] = new HashSet<>(); for (int j = 0; j < n; j++) cols[j] = new HashSet<>();
		for (int br = 0; br < n / boxRows; br++) for (int bc = 0; bc < n / boxCols; bc++) boxes[br][bc] = new HashSet<>();
		for (int i = 0; i < n; i++) {
			for (int j = 0; j < n; j++) {
				char c = board[i][j]; if (c == '.') continue;
				if (rows[i].contains(c) || cols[j].contains(c) || boxes[i / boxRows][j / boxCols].contains(c)) return false;
				rows[i].add(c); cols[j].add(c); boxes[i / boxRows][j / boxCols].add(c);
			}
		}
		return true;
	}
}
'''
    },
    {
        "title": "Tile Movement Simulation (1-D)",
        "statement": (
            "Given start and target board strings (e.g., 'BBB_RRR' -> 'RRR_BBB'), move tiles under rules: "
            "B moves right, R moves left, into '_' or jump over one tile into '_' to reach target in min moves."
        ),
        "variants": [
            "Return the sequence of boards",
            "Multiple blanks; altered movement rules",
        ],
        "leverage": (
            "Use BFS on board states; adapt the neighbor generator for rule changes."
        ),
        "java": r'''import java.util.*;

public final class TileSwapSolver {
	public static int minMoves(String start, String target) {
		if (start.equals(target)) return 0;
		Queue<String> queue = new ArrayDeque<>(); Map<String, Integer> dist = new HashMap<>();
		queue.add(start); dist.put(start, 0);
		while (!queue.isEmpty()) {
			String cur = queue.poll(); int d = dist.get(cur);
			for (String nxt : nextStates(cur)) {
				if (dist.containsKey(nxt)) continue; if (nxt.equals(target)) return d + 1;
				dist.put(nxt, d + 1); queue.add(nxt);
			}
		}
		return -1;
	}
	private static List<String> nextStates(String s) {
		List<String> states = new ArrayList<>(); char[] arr = s.toCharArray(); int n = arr.length; int blank = s.indexOf('_');
		if (blank + 1 < n && arr[blank + 1] == 'R') states.add(swap(arr, blank, blank + 1));
		if (blank + 2 < n && arr[blank + 2] == 'R') states.add(swap(arr, blank, blank + 2));
		if (blank - 1 >= 0 && arr[blank - 1] == 'B') states.add(swap(arr, blank, blank - 1));
		if (blank - 2 >= 0 && arr[blank - 2] == 'B') states.add(swap(arr, blank, blank - 2));
		return states;
	}
	private static String swap(char[] arr, int i, int j) { char[] copy = arr.clone(); char t = copy[i]; copy[i] = copy[j]; copy[j] = t; return new String(copy); }
}
'''
    },
    {
        "title": "Banking System (OO)",
        "statement": (
            "Implement accounts with create, deposit, withdraw, transfer, and top-K transactions."
        ),
        "variants": [
            "Overdraft rules; multi-currency",
            "Per-account top-K; idempotency",
        ],
        "leverage": (
            "Centralize validation in Bank; extend Transaction indexing for richer queries."
        ),
        "java": r'''import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

public final class Bank {
	private final Map<Long, Account> accounts = new HashMap<>();
	private final List<Transaction> allTransactions = new ArrayList<>();
	private final AtomicLong nextId = new AtomicLong(1L);
	public synchronized long createAccount(String owner, long initialCents) {
		if (initialCents < 0) throw new IllegalArgumentException("Negative initial balance");
		long id = nextId.getAndIncrement();
		accounts.put(id, new Account(id, owner, initialCents));
		if (initialCents > 0) allTransactions.add(Transaction.deposit(id, initialCents));
		return id;
	}
	public synchronized void deposit(long accountId, long cents) {
		requirePositive(cents); Account acc = get(accountId); acc.balanceCents += cents; allTransactions.add(Transaction.deposit(accountId, cents));
	}
	public synchronized void withdraw(long accountId, long cents) {
		requirePositive(cents); Account acc = get(accountId); if (acc.balanceCents < cents) throw new IllegalStateException("Insufficient funds");
		acc.balanceCents -= cents; allTransactions.add(Transaction.withdraw(accountId, cents));
	}
	public synchronized void transfer(long fromId, long toId, long cents) {
		requirePositive(cents); Account from = get(fromId); Account to = get(toId); if (from.balanceCents < cents) throw new IllegalStateException("Insufficient funds");
		from.balanceCents -= cents; to.balanceCents += cents; allTransactions.add(Transaction.transfer(fromId, toId, cents));
	}
	public synchronized long balance(long accountId) { return get(accountId).balanceCents; }
	public synchronized List<Transaction> topKByAmount(int k) {
		PriorityQueue<Transaction> pq = new PriorityQueue<>(Comparator.comparingLong(t -> t.amountCents));
		for (Transaction t : allTransactions) {
			if (pq.size() < k) pq.offer(t);
			else if (t.amountCents > pq.peek().amountCents) { pq.poll(); pq.offer(t); }
		}
		List<Transaction> result = new ArrayList<>(pq); result.sort((a, b) -> Long.compare(b.amountCents, a.amountCents)); return result;
	}
	private Account get(long id) { Account acc = accounts.get(id); if (acc == null) throw new NoSuchElementException("No account " + id); return acc; }
	private static void requirePositive(long cents) { if (cents <= 0) throw new IllegalArgumentException("Non-positive amount"); }
	public static final class Account { public final long id; public final String owner; private long balanceCents; Account(long id, String owner, long balanceCents) { this.id = id; this.owner = owner; this.balanceCents = balanceCents; } }
	public static final class Transaction {
		public enum Type { DEPOSIT, WITHDRAW, TRANSFER }
		public final Type type; public final long fromAccountId; public final long toAccountId; public final long amountCents; public final long timestampMs;
		private Transaction(Type type, long fromAccountId, long toAccountId, long amountCents) { this.type = type; this.fromAccountId = fromAccountId; this.toAccountId = toAccountId; this.amountCents = amountCents; this.timestampMs = System.currentTimeMillis(); }
		public static Transaction deposit(long toId, long amount) { return new Transaction(Type.DEPOSIT, -1, toId, amount); }
		public static Transaction withdraw(long fromId, long amount) { return new Transaction(Type.WITHDRAW, fromId, -1, amount); }
		public static Transaction transfer(long fromId, long toId, long amount) { return new Transaction(Type.TRANSFER, fromId, toId, amount); }
	}
}
'''
    },
    {
        "title": "Key-Value Store (with transactions)",
        "statement": (
            "Implement SET/GET/DELETE/COUNT with optional BEGIN/ROLLBACK/COMMIT transactions."
        ),
        "variants": [
            "Versioned GET; TTL",
            "Nested transactions",
        ],
        "leverage": (
            "Use maps for values and value-counts; transaction stack holds undo ops for rollback/commit."
        ),
        "java": r'''import java.util.*;

public final class KeyValueStore {
	private final Map<String, String> store = new HashMap<>();
	private final Map<String, Integer> valueCounts = new HashMap<>();
	private final Deque<List<Runnable>> txStack = new ArrayDeque<>();
	public void set(String key, String value) {
		String old = store.put(key, value); if (old != null) decrement(old); increment(value);
		recordUndo(() -> { String prev = old; String cur = store.put(key, prev); if (cur != null) decrement(cur); if (prev != null) increment(prev); });
	}
	public String get(String key) { return store.get(key); }
	public void delete(String key) { String old = store.remove(key); if (old == null) return; decrement(old); recordUndo(() -> { String cur = store.put(key, old); if (cur != null) decrement(cur); increment(old); }); }
	public int count(String value) { return valueCounts.getOrDefault(value, 0); }
	public void begin() { txStack.push(new ArrayList<>()); }
	public boolean rollback() { if (txStack.isEmpty()) return false; List<Runnable> undos = txStack.pop(); for (int i = undos.size() - 1; i >= 0; i--) undos.get(i).run(); return true; }
	public boolean commit() { if (txStack.isEmpty()) return false; List<Runnable> changes = txStack.pop(); if (!txStack.isEmpty()) txStack.peek().addAll(changes); return true; }
	private void increment(String value) { valueCounts.put(value, valueCounts.getOrDefault(value, 0) + 1); }
	private void decrement(String value) { valueCounts.compute(value, (k, v) -> v == null || v <= 1 ? null : v - 1); }
	private void recordUndo(Runnable undo) { if (!txStack.isEmpty()) txStack.peek().add(undo); }
}
'''
    },
]


class CheatSheetPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, self.title, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(1)
        self.set_draw_color(180, 180, 180)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def add_section_header(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")


def add_paragraph(pdf: FPDF, text: str, line_height: float = 6.0):
    pdf.set_font("Helvetica", size=11)
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    for para in text.splitlines():
        if not para:
            pdf.ln(2)
            continue
        # Multi-cell with explicit width to avoid line-break exceptions
        pdf.multi_cell(effective_width, line_height, para)
    pdf.ln(1)


def add_bullets(pdf: FPDF, items):
    pdf.set_font("Helvetica", size=11)
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    for it in items:
        pdf.multi_cell(effective_width, 6.0, f"- {it}")
    pdf.ln(1)


def add_code_block(pdf: FPDF, code: str):
    pdf.set_font("Courier", size=9)
    effective_width = pdf.w - pdf.l_margin - pdf.r_margin
    # Render code by slicing long lines to fit
    for raw in code.splitlines():
        line = raw.rstrip("\n")
        if line == "":
            pdf.ln(4)
            continue
        remaining = line
        while remaining:
            # Binary search longest prefix that fits the width
            lo, hi = 1, len(remaining)
            best = 1
            while lo <= hi:
                mid = (lo + hi) // 2
                if pdf.get_string_width(remaining[:mid]) <= effective_width:
                    best = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            chunk = remaining[:best]
            pdf.cell(0, 4.5, chunk, new_x="LMARGIN", new_y="NEXT")
            remaining = remaining[best:]
    pdf.ln(1)


def main():
    for prob in PROBLEMS:
        pdf = CheatSheetPDF(orientation="P", unit="mm", format="A4")
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.title = prob["title"]
        pdf.add_page()

        add_section_header(pdf, "Problem Statement")
        add_paragraph(pdf, prob["statement"]) 

        add_section_header(pdf, "Variants")
        add_bullets(pdf, prob["variants"])

        add_section_header(pdf, "How to Leverage the Solution")
        add_paragraph(pdf, prob["leverage"]) 

        add_section_header(pdf, "Java Solution")
        add_paragraph(pdf, "Below is a concise reference implementation.")
        add_code_block(pdf, prob["java"].strip())

        filename = prob["title"].lower().replace(" ", "-").replace("/", "-") + ".pdf"
        out_path = os.path.join(OUTPUT_DIR, filename)
        pdf.output(out_path)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()

from fpdf import FPDF
import os

OUT_DIR = "/workspace/instacart-cheatsheets"
os.makedirs(OUT_DIR, exist_ok=True)

# Use ASCII-only text to avoid Unicode issues with core fonts
problems = [
  {
    "title": "Password Decryption",
    "statement": "Given an encrypted string and a list of indices indicating the sequence to read characters, reconstruct the original password.",
    "variants": [
      "Multiple records: decrypt a batch of strings with corresponding index lists.",
      "File-based: input file contains alternating lines of cipher and indices.",
      "Index format variations: spaces/commas; out-of-range indices; duplicates."
    ],
    "leverage": "Normalize/parsing once for indices, then apply the same O(n) indexing to build the result.",
    "java": r'''import java.util.*;
import java.io.*;
import java.nio.file.*;

public final class PasswordDecryptor {
	public static String decryptByIndices(String cipher, List<Integer> indices) {
		if (cipher == null || indices == null) return "";
		StringBuilder builder = new StringBuilder(indices.size());
		for (int index : indices) {
			if (index < 0 || index >= cipher.length()) {
				throw new IllegalArgumentException("Index out of bounds: " + index);
			}
			builder.append(cipher.charAt(index));
		}
		return builder.toString();
	}

	public static List<String> decryptBatch(List<String> ciphers, List<List<Integer>> indicesLists) {
		if (ciphers.size() != indicesLists.size()) {
			throw new IllegalArgumentException("Mismatched batch sizes");
		}
		List<String> results = new ArrayList<>(ciphers.size());
		for (int i = 0; i < ciphers.size(); i++) {
			results.add(decryptByIndices(ciphers.get(i), indicesLists.get(i)));
		}
		return results;
	}

	public static List<String> decryptFromFile(Path file) throws IOException {
		List<String> decrypted = new ArrayList<>();
		try (BufferedReader reader = Files.newBufferedReader(file)) {
			String cipherLine;
			while ((cipherLine = reader.readLine()) != null) {
				String indicesLine = reader.readLine();
				if (indicesLine == null) break;
				String cipher = parseAfterColon(cipherLine);
				List<Integer> indices = parseIndices(parseAfterColon(indicesLine));
				decrypted.add(decryptByIndices(cipher, indices));
			}
		}
		return decrypted;
	}

	private static String parseAfterColon(String line) {
		int idx = line.indexOf(':');
		return idx >= 0 ? line.substring(idx + 1).trim() : line.trim();
	}

	private static List<Integer> parseIndices(String s) {
		if (s.isEmpty()) return Collections.emptyList();
		String[] parts = s.split("[,\\s]+");
		List<Integer> result = new ArrayList<>(parts.length);
		for (String p : parts) {
			if (p.isEmpty()) continue;
			result.add(Integer.parseInt(p));
		}
		return result;
	}
}
'''
  },
  {
    "title": "Expression Evaluation (Dependency Graph)",
    "statement": "Given equations like T1=2, T3=T1+T2, and a target variable, evaluate the target by resolving dependencies.",
    "variants": [
      "Operators: + - * /",
      "Aliases: T2 = T3",
      "Mix constants and variables; detect cycles/undefined variables."
    ],
    "leverage": "Build a graph and use DFS + memoization for all variants; add cycle/undefined checks once.",
    "java": r'''import java.util.*;

public final class ExpressionGraph {
	private final Map<String, Node> variableToNode = new HashMap<>();

	public static ExpressionGraph fromEquations(List<String> equations) {
		ExpressionGraph graph = new ExpressionGraph();
		for (String eq : equations) {
			graph.addEquation(eq);
		}
		return graph;
	}

	public double evaluate(String target) {
		Map<String, Double> memo = new HashMap<>();
		Set<String> visiting = new HashSet<>();
		return evaluateVar(target, memo, visiting);
	}

	private void addEquation(String equation) {
		String[] parts = equation.split("=");
		if (parts.length != 2) throw new IllegalArgumentException("Bad equation: " + equation);
		String lhs = parts[0].trim();
		String rhs = parts[1].trim();
		Node node = parseRhs(rhs);
		variableToNode.put(lhs, node);
	}

	private static Node parseRhs(String rhs) {
		String[] tokens = rhs.split("\\s+");
		if (tokens.length == 1) {
			Term term = parseTerm(tokens[0]);
			if (term.isConst) return Node.constant(term.value);
			else return Node.identity(term.variableName);
		} else if (tokens.length == 3) {
			Term left = parseTerm(tokens[0]);
			char op = tokens[1].charAt(0);
			Term right = parseTerm(tokens[2]);
			return Node.binary(left, op, right);
		}
		throw new IllegalArgumentException("Unsupported RHS: " + rhs);
	}

	private static Term parseTerm(String token) {
		if (isNumber(token)) return Term.constant(Double.parseDouble(token));
		return Term.variable(token);
	}

	private static boolean isNumber(String s) {
		try { Double.parseDouble(s); return true; }
		catch (NumberFormatException e) { return false; }
	}

	private double evaluateVar(String name, Map<String, Double> memo, Set<String> visiting) {
		if (memo.containsKey(name)) return memo.get(name);
		if (visiting.contains(name)) throw new IllegalStateException("Cycle detected at " + name);
		Node node = variableToNode.get(name);
		if (node == null) throw new IllegalArgumentException("Undefined variable: " + name);

		visiting.add(name);
		double result;
		if (node.kind == NodeKind.CONST) result = node.constantValue;
		else if (node.kind == NodeKind.IDENTITY) result = resolveTerm(node.left, memo, visiting);
		else {
			double leftVal = resolveTerm(node.left, memo, visiting);
			double rightVal = resolveTerm(node.right, memo, visiting);
			switch (node.op) {
				case '+': result = leftVal + rightVal; break;
				case '-': result = leftVal - rightVal; break;
				case '*': result = leftVal * rightVal; break;
				case '/': result = leftVal / rightVal; break;
				default: throw new IllegalArgumentException("Unknown op: " + node.op);
			}
		}
		visiting.remove(name);
		memo.put(name, result);
		return result;
	}

	private double resolveTerm(Term term, Map<String, Double> memo, Set<String> visiting) {
		if (term.isConst) return term.value;
		return evaluateVar(term.variableName, memo, visiting);
	}

	private enum NodeKind { CONST, IDENTITY, BINARY }

	private static final class Node {
		final NodeKind kind;
		final double constantValue;
		final char op;
		final Term left, right;
		private Node(NodeKind kind, double constantValue, char op, Term left, Term right) {
			this.kind = kind; this.constantValue = constantValue; this.op = op; this.left = left; this.right = right;
		}
		static Node constant(double v) { return new Node(NodeKind.CONST, v, 0, null, null); }
		static Node identity(String var) { return new Node(NodeKind.IDENTITY, 0, 0, Term.variable(var), null); }
		static Node binary(Term l, char op, Term r) { return new Node(NodeKind.BINARY, 0, op, l, r); }
	}

	private static final class Term {
		final boolean isConst;
		final double value; final String variableName;
		private Term(boolean isConst, double value, String variableName) {
			this.isConst = isConst; this.value = value; this.variableName = variableName;
		}
		static Term constant(double v) { return new Term(true, v, null); }
		static Term variable(String n) { return new Term(false, 0, n); }
	}
}
'''
  },
  {
    "title": "Ad Click Analysis",
    "statement": "Given purchased user IDs, ad click logs (IP, ad text), and a mapping userId->IP, return each ad's total clicks and clicks that led to purchases.",
    "variants": [
      "Multiple IPs per user; deduplicate repeated clicks",
      "Only count first purchase; inconsistent casing/whitespace"
    ],
    "leverage": "Convert user->IP to IP->user. One pass to count totals and purchase-clicks; add optional (ip,ad) dedup set.",
    "java": r'''import java.util.*;

public final class AdClickAnalytics {
	public static final class AdClick {
		public final String ip; public final String adText;
		public AdClick(String ip, String adText) { this.ip = ip; this.adText = adText; }
	}

	public static Map<String, int[]> analyze(Set<String> purchasedUserIds,
	                                         List<AdClick> clicks,
	                                         Map<String, String> userIdToIp) {
		Map<String, String> ipToUser = new HashMap<>();
		for (Map.Entry<String, String> e : userIdToIp.entrySet()) {
			if (e.getValue() != null) ipToUser.put(e.getValue(), e.getKey());
		}
		Map<String, int[]> result = new HashMap<>();
		for (AdClick c : clicks) {
			String ad = c.adText == null ? "" : c.adText.trim();
			int[] counters = result.computeIfAbsent(ad, k -> new int[2]);
			counters[0]++;
			String user = ipToUser.get(c.ip);
			if (user != null && purchasedUserIds.contains(user)) counters[1]++;
		}
		return result;
	}

	public static Map<String, int[]> analyzeDedup(Set<String> purchasedUserIds,
	                                              List<AdClick> clicks,
	                                              Map<String, String> userIdToIp) {
		Map<String, String> ipToUser = new HashMap<>();
		for (Map.Entry<String, String> e : userIdToIp.entrySet()) {
			if (e.getValue() != null) ipToUser.put(e.getValue(), e.getKey());
		}
		Map<String, int[]> result = new HashMap<>();
		Set<String> seenIpAd = new HashSet<>();
		for (AdClick c : clicks) {
			String ad = c.adText == null ? "" : c.adText.trim();
			String key = c.ip + "\u0000" + ad;
			if (!seenIpAd.add(key)) continue;
			int[] counters = result.computeIfAbsent(ad, k -> new int[2]);
			counters[0]++;
			String user = ipToUser.get(c.ip);
			if (user != null && purchasedUserIds.contains(user)) counters[1]++;
		}
		return result;
	}
}
'''
  },
  {
    "title": "Badge Access: Forgot IN/OUT",
    "statement": "Given logs (name, time, IN/OUT), determine employees who missed an IN or OUT.",
    "variants": [
      "Out-of-order logs; multiple days",
      "Mixed casing; multiple consecutive INs/OUTs"
    ],
    "leverage": "Group per user, sort by time, and scan with a simple state machine.",
    "java": r'''import java.util.*;

public final class BadgeAnomalyDetector {
	public static final class Event {
		public final String employee; public final int minutes; public final boolean isIn;
		public Event(String employee, int minutes, boolean isIn) { this.employee = employee; this.minutes = minutes; this.isIn = isIn; }
	}
	public static final class Result { public final Set<String> forgotIn = new HashSet<>(); public final Set<String> forgotOut = new HashSet<>(); }

	public static Result findForgotInOut(List<Event> events) {
		Map<String, List<Event>> byEmployee = new HashMap<>();
		for (Event e : events) byEmployee.computeIfAbsent(e.employee, k -> new ArrayList<>()).add(e);
		Result result = new Result();
		for (Map.Entry<String, List<Event>> entry : byEmployee.entrySet()) {
			String name = entry.getKey();
			List<Event> list = entry.getValue();
			list.sort(Comparator.comparingInt(ev -> ev.minutes));
			boolean inside = false;
			for (Event e : list) {
				if (e.isIn) {
					if (inside) result.forgotOut.add(name);
					inside = true;
				} else {
					if (!inside) result.forgotIn.add(name);
					inside = false;
				}
			}
			if (inside) result.forgotOut.add(name);
		}
		return result;
	}

	public static int parseTimeToMinutes(String hhmm) {
		String[] p = hhmm.split(":");
		return Integer.parseInt(p[0]) * 60 + Integer.parseInt(p[1]);
	}
}
'''
  },
  {
    "title": "Badge Access: >=3 in 1 Hour",
    "statement": "For each employee, if there exist >=3 badge-ins within any rolling 60-minute window, report the window times.",
    "variants": [
      "Return earliest window only vs all windows",
      "Inclusive boundaries; dedup timestamps"
    ],
    "leverage": "Sort times and use a sliding window; toggle output mode via early-break.",
    "java": r'''import java.util.*;

public final class BadgeFrequencyDetector {
	public static Map<String, List<List<String>>> findAllWindows(Map<String, List<String>> logs) {
		Map<String, List<List<String>>> result = new HashMap<>();
		for (Map.Entry<String, List<String>> e : logs.entrySet()) {
			String name = e.getKey();
			List<Integer> times = new ArrayList<>();
			for (String t : e.getValue()) times.add(parse(t));
			Collections.sort(times);
			int left = 0; List<List<String>> windows = new ArrayList<>();
			for (int right = 0; right < times.size(); right++) {
				while (times.get(right) - times.get(left) > 60) left++;
				if (right - left + 1 >= 3) {
					List<String> win = new ArrayList<>();
					for (int k = left; k <= right; k++) win.add(format(times.get(k)));
					windows.add(win);
				}
			}
			if (!windows.isEmpty()) result.put(name, windows);
		}
		return result;
	}
	private static int parse(String hhmm) { String[] p = hhmm.split(":"); return Integer.parseInt(p[0])*60 + Integer.parseInt(p[1]); }
	private static String format(int minutes) { int h = minutes/60, m = minutes%60; return String.format("%02d:%02d", h, m); }
}
'''
  },
  {
    "title": "Longest Common Subarray",
    "statement": "Given two arrays, find the longest common contiguous subarray.",
    "variants": [
      "Return length only vs subarray",
      "Memory-optimized DP"
    ],
    "leverage": "Use rolling DP; track end index to rebuild the subarray if needed.",
    "java": r'''import java.util.*;

public final class LongestCommonSubarray {
	public static int length(int[] a, int[] b) {
		int n = a.length, m = b.length; int[] dp = new int[m + 1]; int best = 0;
		for (int i = 1; i <= n; i++) {
			int prev = 0;
			for (int j = 1; j <= m; j++) {
				int temp = dp[j];
				if (a[i - 1] == b[j - 1]) { dp[j] = prev + 1; if (dp[j] > best) best = dp[j]; }
				else dp[j] = 0;
				prev = temp;
			}
		}
		return best;
	}
	public static int[] subarray(int[] a, int[] b) {
		int n = a.length, m = b.length; int[] dp = new int[m + 1]; int best = 0, endA = -1;
		for (int i = 1; i <= n; i++) {
			int prev = 0;
			for (int j = 1; j <= m; j++) {
				int temp = dp[j];
				if (a[i - 1] == b[j - 1]) { dp[j] = prev + 1; if (dp[j] > best) { best = dp[j]; endA = i - 1; } }
				else dp[j] = 0;
				prev = temp;
			}
		}
		if (best == 0) return new int[0];
		return Arrays.copyOfRange(a, endA - best + 1, endA + 1);
	}
}
'''
  },
  {
    "title": "Sudoku Validation",
    "statement": "Validate an N x N Sudoku board ensuring no duplicates in rows, columns, and sub-boxes.",
    "variants": [
      "Different board sizes and box dimensions",
      "Partial boards ('.' as empty)"
    ],
    "leverage": "Parameterize box dims; same row/col/box sets.",
    "java": r'''import java.util.*;

public final class SudokuValidator {
	public static boolean isValid(char[][] board) { return isValid(board, 3, 3); }
	public static boolean isValid(char[][] board, int boxRows, int boxCols) {
		int n = board.length; for (char[] row : board) if (row.length != n) throw new IllegalArgumentException("Non-square board");
		Set<Character>[] rows = new Set[n]; Set<Character>[] cols = new Set[n];
		@SuppressWarnings("unchecked") Set<Character>[][] boxes = new Set[n / boxRows][n / boxCols];
		for (int i = 0; i < n; i++) rows[i] = new HashSet<>(); for (int j = 0; j < n; j++) cols[j] = new HashSet<>();
		for (int br = 0; br < n / boxRows; br++) for (int bc = 0; bc < n / boxCols; bc++) boxes[br][bc] = new HashSet<>();
		for (int i = 0; i < n; i++) {
			for (int j = 0; j < n; j++) {
				char c = board[i][j]; if (c == '.') continue;
				if (rows[i].contains(c) || cols[j].contains(c) || boxes[i / boxRows][j / boxCols].contains(c)) return false;
				rows[i].add(c); cols[j].add(c); boxes[i / boxRows][j / boxCols].add(c);
			}
		}
		return true;
	}
}
'''
  },
  {
    "title": "Tile Movement Simulation (1-D)",
    "statement": "Given start and target board strings (e.g., 'BBB_RRR' -> 'RRR_BBB'), move tiles under rules: B moves right, R moves left, into '_' or jump over one tile into '_' to reach target in min moves.",
    "variants": [
      "Return the sequence of boards",
      "Multiple blanks; altered movement rules"
    ],
    "leverage": "Use BFS on board states; adapt the neighbor generator for rule changes.",
    "java": r'''import java.util.*;

public final class TileSwapSolver {
	public static int minMoves(String start, String target) {
		if (start.equals(target)) return 0;
		Queue<String> queue = new ArrayDeque<>(); Map<String, Integer> dist = new HashMap<>();
		queue.add(start); dist.put(start, 0);
		while (!queue.isEmpty()) {
			String cur = queue.poll(); int d = dist.get(cur);
			for (String nxt : nextStates(cur)) {
				if (dist.containsKey(nxt)) continue; if (nxt.equals(target)) return d + 1;
				dist.put(nxt, d + 1); queue.add(nxt);
			}
		}
		return -1;
	}
	private static List<String> nextStates(String s) {
		List<String> states = new ArrayList<>(); char[] arr = s.toCharArray(); int n = arr.length; int blank = s.indexOf('_');
		if (blank + 1 < n && arr[blank + 1] == 'R') states.add(swap(arr, blank, blank + 1));
		if (blank + 2 < n && arr[blank + 2] == 'R') states.add(swap(arr, blank, blank + 2));
		if (blank - 1 >= 0 && arr[blank - 1] == 'B') states.add(swap(arr, blank, blank - 1));
		if (blank - 2 >= 0 && arr[blank - 2] == 'B') states.add(swap(arr, blank, blank - 2));
		return states;
	}
	private static String swap(char[] arr, int i, int j) { char[] copy = arr.clone(); char t = copy[i]; copy[i] = copy[j]; copy[j] = t; return new String(copy); }
}
'''
  },
  {
    "title": "Banking System (OO)",
    "statement": "Implement accounts with create, deposit, withdraw, transfer, and top-K transactions.",
    "variants": [
      "Overdraft rules; multi-currency",
      "Per-account top-K; idempotency"
    ],
    "leverage": "Centralize validation in Bank; extend Transaction indexing for richer queries.",
    "java": r'''import java.util.*;
import java.util.concurrent.atomic.AtomicLong;

public final class Bank {
	private final Map<Long, Account> accounts = new HashMap<>();
	private final List<Transaction> allTransactions = new ArrayList<>();
	private final AtomicLong nextId = new AtomicLong(1L);
	public synchronized long createAccount(String owner, long initialCents) {
		if (initialCents < 0) throw new IllegalArgumentException("Negative initial balance");
		long id = nextId.getAndIncrement();
		accounts.put(id, new Account(id, owner, initialCents));
		if (initialCents > 0) allTransactions.add(Transaction.deposit(id, initialCents));
		return id;
	}
	public synchronized void deposit(long accountId, long cents) {
		requirePositive(cents); Account acc = get(accountId); acc.balanceCents += cents; allTransactions.add(Transaction.deposit(accountId, cents));
	}
	public synchronized void withdraw(long accountId, long cents) {
		requirePositive(cents); Account acc = get(accountId); if (acc.balanceCents < cents) throw new IllegalStateException("Insufficient funds");
		acc.balanceCents -= cents; allTransactions.add(Transaction.withdraw(accountId, cents));
	}
	public synchronized void transfer(long fromId, long toId, long cents) {
		requirePositive(cents); Account from = get(fromId); Account to = get(toId); if (from.balanceCents < cents) throw new IllegalStateException("Insufficient funds");
		from.balanceCents -= cents; to.balanceCents += cents; allTransactions.add(Transaction.transfer(fromId, toId, cents));
	}
	public synchronized long balance(long accountId) { return get(accountId).balanceCents; }
	public synchronized List<Transaction> topKByAmount(int k) {
		PriorityQueue<Transaction> pq = new PriorityQueue<>(Comparator.comparingLong(t -> t.amountCents));
		for (Transaction t : allTransactions) {
			if (pq.size() < k) pq.offer(t);
			else if (t.amountCents > pq.peek().amountCents) { pq.poll(); pq.offer(t); }
		}
		List<Transaction> result = new ArrayList<>(pq); result.sort((a, b) -> Long.compare(b.amountCents, a.amountCents)); return result;
	}
	private Account get(long id) { Account acc = accounts.get(id); if (acc == null) throw new NoSuchElementException("No account " + id); return acc; }
	private static void requirePositive(long cents) { if (cents <= 0) throw new IllegalArgumentException("Non-positive amount"); }
	public static final class Account { public final long id; public final String owner; private long balanceCents; Account(long id, String owner, long balanceCents) { this.id = id; this.owner = owner; this.balanceCents = balanceCents; } }
	public static final class Transaction {
		public enum Type { DEPOSIT, WITHDRAW, TRANSFER }
		public final Type type; public final long fromAccountId; public final long toAccountId; public final long amountCents; public final long timestampMs;
		private Transaction(Type type, long fromAccountId, long toAccountId, long amountCents) { this.type = type; this.fromAccountId = fromAccountId; this.toAccountId = toAccountId; this.amountCents = amountCents; this.timestampMs = System.currentTimeMillis(); }
		public static Transaction deposit(long toId, long amount) { return new Transaction(Type.DEPOSIT, -1, toId, amount); }
		public static Transaction withdraw(long fromId, long amount) { return new Transaction(Type.WITHDRAW, fromId, -1, amount); }
		public static Transaction transfer(long fromId, long toId, long amount) { return new Transaction(Type.TRANSFER, fromId, toId, amount); }
	}
}
'''
  },
  {
    "title": "Key-Value Store (with transactions)",
    "statement": "Implement SET/GET/DELETE/COUNT with optional BEGIN/ROLLBACK/COMMIT transactions.",
    "variants": [
      "Versioned GET; TTL",
      "Nested transactions"
    ],
    "leverage": "Use maps for values and value-counts; transaction stack holds undo ops for rollback/commit.",
    "java": r'''import java.util.*;

public final class KeyValueStore {
	private final Map<String, String> store = new HashMap<>();
	private final Map<String, Integer> valueCounts = new HashMap<>();
	private final Deque<List<Runnable>> txStack = new ArrayDeque<>();
	public void set(String key, String value) {
		String old = store.put(key, value); if (old != null) decrement(old); increment(value);
		recordUndo(() -> { String prev = old; String cur = store.put(key, prev); if (cur != null) decrement(cur); if (prev != null) increment(prev); });
	}
	public String get(String key) { return store.get(key); }
	public void delete(String key) { String old = store.remove(key); if (old == null) return; decrement(old); recordUndo(() -> { String cur = store.put(key, old); if (cur != null) decrement(cur); increment(old); }); }
	public int count(String value) { return valueCounts.getOrDefault(value, 0); }
	public void begin() { txStack.push(new ArrayList<>()); }
	public boolean rollback() { if (txStack.isEmpty()) return false; List<Runnable> undos = txStack.pop(); for (int i = undos.size() - 1; i >= 0; i--) undos.get(i).run(); return true; }
	public boolean commit() { if (txStack.isEmpty()) return false; List<Runnable> changes = txStack.pop(); if (!txStack.isEmpty()) txStack.peek().addAll(changes); return true; }
	private void increment(String value) { valueCounts.put(value, valueCounts.getOrDefault(value, 0) + 1); }
	private void decrement(String value) { valueCounts.compute(value, (k, v) -> v == null or v <= 1 ? null : v - 1); }
	private void recordUndo(Runnable undo) { if (!txStack.isEmpty()) txStack.peek().add(undo); }
}
'''
  }
]

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        # Full-width title cell, then newline
        self.cell(0, 10, self.title, new_x="LMARGIN", new_y="NEXT", align="C")
        self.ln(2)
        self.set_draw_color(180, 180, 180)
        # horizontal rule
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=9)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

EFFECTIVE_WIDTH = None

def add_paragraph(pdf: FPDF, label: str, text: str):
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, label, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", size=11)
    # Split by explicit newlines; render each with wrapping to effective width
    for para in text.splitlines():
        if not para:
            pdf.ln(2)
            continue
        pdf.multi_cell(EFFECTIVE_WIDTH, 6, para)
    pdf.ln(2)

def add_bullets(pdf: FPDF, items):
    pdf.set_font("Helvetica", size=11)
    for it in items:
        pdf.multi_cell(EFFECTIVE_WIDTH, 6, f"- {it}")
    pdf.ln(2)

def add_code(pdf: FPDF, code: str):
    pdf.set_font("Courier", size=9)
    # Wrap code lines by measuring string width and splitting long tokens
    for raw in code.splitlines():
        line = raw.rstrip("\n")
        if not line:
            pdf.ln(4)
            continue
        remaining = line
        while remaining:
            # find the longest prefix that fits EFFECTIVE_WIDTH
            lo, hi = 1, len(remaining)
            best = 1
            while lo <= hi:
                mid = (lo + hi) // 2
                w = pdf.get_string_width(remaining[:mid])
                if w <= EFFECTIVE_WIDTH:
                    best = mid
                    lo = mid + 1
                else:
                    hi = mid - 1
            chunk = remaining[:best]
            pdf.cell(0, 4.5, chunk, new_x="LMARGIN", new_y="NEXT")
            remaining = remaining[best:]
    pdf.ln(2)

for p in problems:
    pdf = PDF(orientation='P', unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.title = p["title"]
    pdf.add_page()

    # Effective width between margins
    EFFECTIVE_WIDTH = pdf.w - pdf.l_margin - pdf.r_margin

    add_paragraph(pdf, "Problem Statement", p["statement"])
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Variants", new_x="LMARGIN", new_y="NEXT")
    add_bullets(pdf, p["variants"])
    add_paragraph(pdf, "How to Leverage the Solution", p["leverage"]) 
    add_paragraph(pdf, "Java Solution", "Below is a concise reference implementation. Full comments omitted for brevity.")
    add_code(pdf, p["java"].strip())

    out_path = os.path.join(OUT_DIR, p["title"].lower().replace(' ', '-').replace('/', '-') + ".pdf")
    pdf.output(out_path)
    print("Wrote", out_path)
