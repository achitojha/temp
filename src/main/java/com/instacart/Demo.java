package com.instacart;

import com.instacart.problems.*;

import java.util.*;

public class Demo {
    public static void main(String[] args) {
        runLongestCommonSubarrayDemo();
        runAdClickAnalysisDemo();
        runBadgeAccessAnomaliesDemo();
        runHighFrequencyAccessDemo();
        runSudokuValidatorDemo();
        runTileMovementSimulationDemo();
        runVariableEvaluatorDemo();
        runBankingSystemDemo();
        runKeyValueStoreWithTTLDemo();
        System.out.println("All demos ran.");
    }

    private static void runLongestCommonSubarrayDemo() {
        int[] first = {1, 2, 3, 2, 1};
        int[] second = {3, 2, 1, 4, 7};
        int len = LongestCommonSubarray.longestCommonSubarrayLength(first, second);
        System.out.println("LCS length: " + len);
        System.out.println("LCS array: " + Arrays.toString(LongestCommonSubarray.longestCommonSubarray(first, second)));
    }

    private static void runAdClickAnalysisDemo() {
        List<String> adClicks = Arrays.asList(
                "192.168.0.1,Buy Shoes",
                "192.168.0.2,Buy Shoes",
                "192.168.0.3,Fresh Apples",
                "192.168.0.1,Fresh Apples"
        );
        List<String> ipToUser = Arrays.asList(
                "192.168.0.1,u1",
                "192.168.0.2,u2",
                "192.168.0.3,u3"
        );
        List<String> purchases = Arrays.asList("u2", "u3", "u3");
        Map<String, AdClickAnalysis.AdStats> stats = AdClickAnalysis.computeAdStats(adClicks, ipToUser, purchases);
        System.out.println("Ad stats: " + stats);
    }

    private static void runBadgeAccessAnomaliesDemo() {
        List<BadgeAccessAnomalies.BadgeRecord> records = Arrays.asList(
                new BadgeAccessAnomalies.BadgeRecord("Alice", "09:00", "in"),
                new BadgeAccessAnomalies.BadgeRecord("Alice", "12:00", "in"),
                new BadgeAccessAnomalies.BadgeRecord("Alice", "18:00", "out"),
                new BadgeAccessAnomalies.BadgeRecord("Bob", "09:00", "out"),
                new BadgeAccessAnomalies.BadgeRecord("Bob", "10:00", "in")
        );
        BadgeAccessAnomalies.Result result = BadgeAccessAnomalies.findAnomalies(records);
        System.out.println("Forgot IN: " + result.forgotBadgeIn);
        System.out.println("Forgot OUT: " + result.forgotBadgeOut);
    }

    private static void runHighFrequencyAccessDemo() {
        List<HighFrequencyAccess.AccessRecord> records = Arrays.asList(
                new HighFrequencyAccess.AccessRecord("Carol", "09:00"),
                new HighFrequencyAccess.AccessRecord("Carol", "09:30"),
                new HighFrequencyAccess.AccessRecord("Carol", "09:59"),
                new HighFrequencyAccess.AccessRecord("Dave", "12:00"),
                new HighFrequencyAccess.AccessRecord("Dave", "13:01"),
                new HighFrequencyAccess.AccessRecord("Dave", "13:30")
        );
        Map<String, List<String>> alerts = HighFrequencyAccess.findAlerts(records, 3, 60);
        System.out.println("High frequency alerts: " + alerts);
    }

    private static void runSudokuValidatorDemo() {
        char[][] board = new char[][]{
                {'5','3','.', '.', '7','.', '.', '.', '.'},
                {'6','.', '.', '1','9','5', '.', '.', '.'},
                {'.','9','8', '.', '.', '.', '.', '6','.'},
                {'8','.', '.', '.', '6','.', '.', '.', '3'},
                {'4','.', '.', '8','.', '3', '.', '.', '1'},
                {'7','.', '.', '.', '2','.', '.', '.', '6'},
                {'.','6','.', '.', '.', '.', '2','8','.'},
                {'.','.', '.', '4','1','9', '.', '.', '5'},
                {'.','.', '.', '.', '8','.', '.', '7','9'}
        };
        System.out.println("Sudoku valid: " + SudokuValidator.isValid(board));
    }

    private static void runTileMovementSimulationDemo() {
        String state = "R_B_RB_";
        List<String> next = TileMovementSimulation.generateNextStates(state);
        System.out.println("Next states from " + state + ": " + next);
    }

    private static void runVariableEvaluatorDemo() {
        List<String> equations = Arrays.asList("T1=2", "T2=T3", "T3=T1", "T4=T3");
        Integer value = VariableEvaluator.evaluate(equations, "T4");
        System.out.println("T4 value: " + value);
    }

    private static void runBankingSystemDemo() {
        BankingSystem bank = new BankingSystem();
        bank.createAccount("a");
        bank.createAccount("b");
        bank.deposit("a", 100_00);
        bank.deposit("b", 50_00);
        bank.transfer("a", "b", 25_00);
        System.out.println("Balance a: " + bank.getBalance("a") + ", b: " + bank.getBalance("b"));
        System.out.println("Top1: " + bank.getTopKBalances(1));
    }

    private static void runKeyValueStoreWithTTLDemo() {
        KeyValueStoreWithTTL<String, String> store = new KeyValueStoreWithTTL<>();
        store.set("k1", "v1", 100);
        store.set("k2", "v2", 0);
        System.out.println("k1: " + store.get("k1") + ", k2: " + store.get("k2"));
        try { Thread.sleep(120); } catch (InterruptedException ignored) {}
        System.out.println("k1 after ttl: " + store.get("k1"));
        System.out.println("active size: " + store.sizeActive());
    }
}

