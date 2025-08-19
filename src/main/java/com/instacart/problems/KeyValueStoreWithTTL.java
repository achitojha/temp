package com.instacart.problems;

import java.util.*;

public class KeyValueStoreWithTTL<K, V> {

    private static class Entry<V> {
        V value;
        long expireAtMillis; // Long.MAX for no expiry
    }

    private final Map<K, Entry<V>> map = new HashMap<>();
    private final PriorityQueue<Map.Entry<K, Long>> expiryMinHeap = new PriorityQueue<>(Comparator.comparingLong(Map.Entry::getValue));

    public void set(K key, V value, long ttlMillis) {
        long now = System.currentTimeMillis();
        long expireAt = ttlMillis <= 0 ? Long.MAX_VALUE : now + ttlMillis;
        Entry<V> e = new Entry<>();
        e.value = value;
        e.expireAtMillis = expireAt;
        map.put(key, e);
        if (expireAt != Long.MAX_VALUE) {
            expiryMinHeap.add(new AbstractMap.SimpleEntry<>(key, expireAt));
        }
        cleanup(now);
    }

    public V get(K key) {
        long now = System.currentTimeMillis();
        cleanup(now);
        Entry<V> e = map.get(key);
        if (e == null) return null;
        if (e.expireAtMillis < now) {
            map.remove(key);
            return null;
        }
        return e.value;
    }

    public boolean delete(K key) {
        long now = System.currentTimeMillis();
        cleanup(now);
        return map.remove(key) != null;
    }

    public int sizeActive() {
        long now = System.currentTimeMillis();
        cleanup(now);
        return map.size();
    }

    private void cleanup(long now) {
        while (!expiryMinHeap.isEmpty()) {
            Map.Entry<K, Long> top = expiryMinHeap.peek();
            if (top.getValue() > now) break;
            expiryMinHeap.poll();
            Entry<V> e = map.get(top.getKey());
            if (e != null && e.expireAtMillis <= now) {
                map.remove(top.getKey());
            }
        }
    }
}

