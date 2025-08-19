package com.instacart.problems;

import java.util.*;

public class TileMovementSimulation {

    // State uses 'R' for red, 'B' for black, '_' for empty
    public static List<String> generateNextStates(String state) {
        List<String> result = new ArrayList<>();
        if (state == null || state.isEmpty()) return result;
        char[] s = state.toCharArray();
        int n = s.length;
        for (int i = 0; i < n; i++) {
            if (s[i] == 'R') {
                // move right by 1
                if (i + 1 < n && s[i + 1] == '_') {
                    result.add(swap(s, i, i + 1));
                }
                // jump over one 'B' to empty
                if (i + 2 < n && s[i + 1] == 'B' && s[i + 2] == '_') {
                    result.add(swap(s, i, i + 2));
                }
            } else if (s[i] == 'B') {
                // move left by 1
                if (i - 1 >= 0 && s[i - 1] == '_') {
                    result.add(swap(s, i, i - 1));
                }
                // jump over one 'R' to empty
                if (i - 2 >= 0 && s[i - 1] == 'R' && s[i - 2] == '_') {
                    result.add(swap(s, i, i - 2));
                }
            }
        }
        return dedupPreserveOrder(result);
    }

    private static String swap(char[] s, int i, int j) {
        char[] copy = Arrays.copyOf(s, s.length);
        char tmp = copy[i];
        copy[i] = copy[j];
        copy[j] = tmp;
        return new String(copy);
    }

    private static List<String> dedupPreserveOrder(List<String> arr) {
        LinkedHashSet<String> set = new LinkedHashSet<>(arr);
        return new ArrayList<>(set);
    }
}

