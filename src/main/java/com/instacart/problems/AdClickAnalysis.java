package com.instacart.problems;

import java.util.*;

public class AdClickAnalysis {

    public static class AdStats {
        public int totalClicks;
        public int uniquePurchasers;

        public AdStats() {}

        @Override
        public String toString() {
            return "{" +
                    "clicks=" + totalClicks +
                    ", purchasers=" + uniquePurchasers +
                    '}';
        }
    }

    public static Map<String, AdStats> computeAdStats(List<String> adClicks, List<String> ipToUser, List<String> purchases) {
        Map<String, String> ipToUserId = new HashMap<>();
        for (String line : ipToUser) {
            String[] parts = splitOnce(line);
            if (parts.length >= 2) {
                ipToUserId.put(parts[0].trim(), parts[1].trim());
            }
        }

        Map<String, AdStats> adToStats = new HashMap<>();
        Map<String, Set<String>> adToClickUsers = new HashMap<>();
        for (String line : adClicks) {
            String[] parts = splitOnce(line);
            if (parts.length >= 2) {
                String ip = parts[0].trim();
                String adText = parts[1].trim();
                String userId = ipToUserId.get(ip);
                AdStats stats = adToStats.computeIfAbsent(adText, k -> new AdStats());
                stats.totalClicks += 1;
                if (userId != null) {
                    adToClickUsers.computeIfAbsent(adText, k -> new HashSet<>()).add(userId);
                }
            }
        }

        Set<String> purchasingUsers = new HashSet<>();
        for (String line : purchases) {
            String userId = line.trim();
            if (!userId.isEmpty()) {
                purchasingUsers.add(userId);
            }
        }

        for (Map.Entry<String, Set<String>> entry : adToClickUsers.entrySet()) {
            String adText = entry.getKey();
            Set<String> clickedUsers = entry.getValue();
            int purchasers = 0;
            for (String user : clickedUsers) {
                if (purchasingUsers.contains(user)) {
                    purchasers++;
                }
            }
            adToStats.computeIfAbsent(adText, k -> new AdStats()).uniquePurchasers = purchasers;
        }

        return adToStats;
    }

    private static String[] splitOnce(String line) {
        int idx = line.indexOf(',');
        if (idx < 0) return new String[]{line};
        String a = line.substring(0, idx);
        String b = line.substring(idx + 1);
        return new String[]{a, b};
    }
}

