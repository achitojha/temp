package com.instacart.problems;

import java.util.*;

public class HighFrequencyAccess {

    public static class AccessRecord {
        public final String name;
        public final String timestampHHmm;

        public AccessRecord(String name, String timestampHHmm) {
            this.name = name;
            this.timestampHHmm = timestampHHmm;
        }
    }

    public static Map<String, List<String>> findAlerts(List<AccessRecord> records, int thresholdCount, int windowMinutes) {
        Map<String, List<Integer>> byUser = new HashMap<>();
        for (AccessRecord r : records) {
            byUser.computeIfAbsent(r.name, k -> new ArrayList<>()).add(toMinutes(r.timestampHHmm));
        }
        for (List<Integer> times : byUser.values()) {
            Collections.sort(times);
        }
        Map<String, List<String>> alerts = new HashMap<>();
        for (Map.Entry<String, List<Integer>> entry : byUser.entrySet()) {
            String name = entry.getKey();
            List<Integer> times = entry.getValue();
            Deque<Integer> window = new ArrayDeque<>();
            for (int t : times) {
                window.addLast(t);
                while (!window.isEmpty() && t - window.peekFirst() > windowMinutes) {
                    window.removeFirst();
                }
                if (window.size() >= thresholdCount) {
                    List<String> formatted = new ArrayList<>();
                    for (int w : window) {
                        formatted.add(formatMinutes(w));
                    }
                    alerts.put(name, formatted);
                    break; // report earliest
                }
            }
        }
        return alerts;
    }

    private static int toMinutes(String hhmm) {
        String[] parts = hhmm.split(":");
        int h = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        return h * 60 + m;
    }

    private static String formatMinutes(int total) {
        int h = total / 60;
        int m = total % 60;
        return String.format("%02d:%02d", h, m);
    }
}

