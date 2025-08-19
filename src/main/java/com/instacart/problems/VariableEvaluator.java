package com.instacart.problems;

import java.util.*;

public class VariableEvaluator {

    public static Integer evaluate(List<String> equations, String target) {
        Map<String, String> equalTo = new HashMap<>();
        Map<String, Integer> values = new HashMap<>();
        Set<String> symbols = new HashSet<>();

        for (String eq : equations) {
            String[] parts = eq.split("=");
            if (parts.length != 2) continue;
            String left = parts[0].trim();
            String right = parts[1].trim();
            symbols.add(left);
            if (isInteger(right)) {
                values.put(left, Integer.parseInt(right));
            } else {
                equalTo.put(left, right);
                symbols.add(right);
            }
        }

        Map<String, Integer> memo = new HashMap<>();
        Set<String> visiting = new HashSet<>();

        return dfs(target, equalTo, values, memo, visiting);
    }

    private static Integer dfs(String var,
                               Map<String, String> equalTo,
                               Map<String, Integer> values,
                               Map<String, Integer> memo,
                               Set<String> visiting) {
        if (memo.containsKey(var)) return memo.get(var);
        if (values.containsKey(var)) {
            int v = values.get(var);
            memo.put(var, v);
            return v;
        }
        if (visiting.contains(var)) return null; // cycle
        visiting.add(var);
        String other = equalTo.get(var);
        if (other == null) return null; // undefined
        Integer val = dfs(other, equalTo, values, memo, visiting);
        visiting.remove(var);
        if (val != null) memo.put(var, val);
        return val;
    }

    private static boolean isInteger(String s) {
        try { Integer.parseInt(s); return true; } catch (Exception ignored) { return false; }
    }
}

