package com.instacart.problems;

import java.util.*;

public class BankingSystem {
    private final Map<String, Long> accountToBalanceCents = new HashMap<>();

    public boolean createAccount(String accountId) {
        if (accountId == null || accountId.isEmpty()) return false;
        if (accountToBalanceCents.containsKey(accountId)) return false;
        accountToBalanceCents.put(accountId, 0L);
        return true;
    }

    public boolean deposit(String accountId, long amountCents) {
        if (amountCents < 0) return false;
        Long bal = accountToBalanceCents.get(accountId);
        if (bal == null) return false;
        accountToBalanceCents.put(accountId, bal + amountCents);
        return true;
    }

    public boolean withdraw(String accountId, long amountCents) {
        if (amountCents < 0) return false;
        Long bal = accountToBalanceCents.get(accountId);
        if (bal == null) return false;
        if (bal < amountCents) return false;
        accountToBalanceCents.put(accountId, bal - amountCents);
        return true;
    }

    public boolean transfer(String from, String to, long amountCents) {
        if (amountCents < 0) return false;
        Long fromBal = accountToBalanceCents.get(from);
        Long toBal = accountToBalanceCents.get(to);
        if (fromBal == null || toBal == null) return false;
        if (fromBal < amountCents) return false;
        accountToBalanceCents.put(from, fromBal - amountCents);
        accountToBalanceCents.put(to, toBal + amountCents);
        return true;
    }

    public long getBalance(String accountId) {
        return accountToBalanceCents.getOrDefault(accountId, 0L);
    }

    public List<Map.Entry<String, Long>> getTopKBalances(int k) {
        List<Map.Entry<String, Long>> list = new ArrayList<>(accountToBalanceCents.entrySet());
        list.sort((a, b) -> Long.compare(b.getValue(), a.getValue()));
        if (k < list.size()) {
            return new ArrayList<>(list.subList(0, k));
        }
        return list;
    }
}

