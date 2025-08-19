package com.instacart.problems;

public class LongestCommonSubarray {

    public static int longestCommonSubarrayLength(int[] firstArray, int[] secondArray) {
        if (firstArray == null || secondArray == null || firstArray.length == 0 || secondArray.length == 0) {
            return 0;
        }
        int firstLength = firstArray.length;
        int secondLength = secondArray.length;
        int maxLength = 0;

        int[] previousRow = new int[secondLength + 1];
        int[] currentRow = new int[secondLength + 1];

        for (int i = 1; i <= firstLength; i++) {
            for (int j = 1; j <= secondLength; j++) {
                if (firstArray[i - 1] == secondArray[j - 1]) {
                    currentRow[j] = previousRow[j - 1] + 1;
                    if (currentRow[j] > maxLength) {
                        maxLength = currentRow[j];
                    }
                } else {
                    currentRow[j] = 0;
                }
            }
            int[] temp = previousRow;
            previousRow = currentRow;
            currentRow = temp;
        }
        return maxLength;
    }

    public static int[] longestCommonSubarray(int[] firstArray, int[] secondArray) {
        if (firstArray == null || secondArray == null || firstArray.length == 0 || secondArray.length == 0) {
            return new int[0];
        }
        int firstLength = firstArray.length;
        int secondLength = secondArray.length;
        int maxLength = 0;
        int endIndexInFirst = -1;

        int[] previousRow = new int[secondLength + 1];
        int[] currentRow = new int[secondLength + 1];

        for (int i = 1; i <= firstLength; i++) {
            for (int j = 1; j <= secondLength; j++) {
                if (firstArray[i - 1] == secondArray[j - 1]) {
                    currentRow[j] = previousRow[j - 1] + 1;
                    if (currentRow[j] > maxLength) {
                        maxLength = currentRow[j];
                        endIndexInFirst = i - 1;
                    }
                } else {
                    currentRow[j] = 0;
                }
            }
            int[] temp = previousRow;
            previousRow = currentRow;
            currentRow = temp;
        }

        if (maxLength == 0) {
            return new int[0];
        }
        int start = endIndexInFirst - maxLength + 1;
        int[] result = new int[maxLength];
        for (int k = 0; k < maxLength; k++) {
            result[k] = firstArray[start + k];
        }
        return result;
    }
}
