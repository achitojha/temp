package com.instacart.problems;

public class SudokuValidator {

    public static boolean isValid(char[][] board) {
        if (board == null || board.length != 9 || board[0].length != 9) {
            return false;
        }
        boolean[][] rows = new boolean[9][9];
        boolean[][] cols = new boolean[9][9];
        boolean[][] boxes = new boolean[9][9];
        for (int r = 0; r < 9; r++) {
            for (int c = 0; c < 9; c++) {
                char ch = board[r][c];
                if (ch == '.') continue;
                if (ch < '1' || ch > '9') return false;
                int idx = ch - '1';
                int b = (r / 3) * 3 + (c / 3);
                if (rows[r][idx] || cols[c][idx] || boxes[b][idx]) return false;
                rows[r][idx] = cols[c][idx] = boxes[b][idx] = true;
            }
        }
        return true;
    }
}

