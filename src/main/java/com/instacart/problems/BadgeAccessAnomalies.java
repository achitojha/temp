package com.instacart.problems;

import java.util.*;

public class BadgeAccessAnomalies {

    public static class BadgeRecord {
        public final String name;
        public final String timestampHHmm;
        public final String action; // "in" or "out"

        public BadgeRecord(String name, String timestampHHmm, String action) {
            this.name = name;
            this.timestampHHmm = timestampHHmm;
            this.action = action.toLowerCase(Locale.ROOT);
        }
    }

    public static class Result {
        public final Set<String> forgotBadgeIn;
        public final Set<String> forgotBadgeOut;

        public Result(Set<String> forgotBadgeIn, Set<String> forgotBadgeOut) {
            this.forgotBadgeIn = forgotBadgeIn;
            this.forgotBadgeOut = forgotBadgeOut;
        }
    }

    public static Result findAnomalies(List<BadgeRecord> records) {
        Map<String, List<BadgeRecord>> byUser = new HashMap<>();
        for (BadgeRecord r : records) {
            byUser.computeIfAbsent(r.name, k -> new ArrayList<>()).add(r);
        }
        for (List<BadgeRecord> list : byUser.values()) {
            list.sort(Comparator.comparingInt(BadgeAccessAnomalies::toMinutes));
        }

        Set<String> forgotIn = new HashSet<>();
        Set<String> forgotOut = new HashSet<>();

        for (Map.Entry<String, List<BadgeRecord>> entry : byUser.entrySet()) {
            String name = entry.getKey();
            List<BadgeRecord> list = entry.getValue();
            boolean inside = false;
            for (BadgeRecord r : list) {
                if (r.action.equals("in")) {
                    if (inside) {
                        forgotOut.add(name);
                    }
                    inside = true;
                } else if (r.action.equals("out")) {
                    if (!inside) {
                        forgotIn.add(name);
                    }
                    inside = false;
                }
            }
            if (inside) {
                forgotOut.add(name);
            }
        }
        return new Result(forgotIn, forgotOut);
    }

    private static int toMinutes(BadgeRecord r) {
        return toMinutes(r.timestampHHmm);
    }

    private static int toMinutes(String hhmm) {
        String[] parts = hhmm.split(":");
        int h = Integer.parseInt(parts[0]);
        int m = Integer.parseInt(parts[1]);
        return h * 60 + m;
    }
}

