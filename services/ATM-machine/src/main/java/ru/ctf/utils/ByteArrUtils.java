package ru.ctf.utils;

import java.util.Arrays;

public class ByteArrUtils {

    public static int findNonZeroByteIndex(byte[] arr) {
        for (int i = arr.length - 1; i >= 0; i--) {
            if (arr[i] != 0) {
                return i + 1;
            }
        }
        return 0;
    }

    public static byte[] getNonZeroBytes(byte[] arr) {
        return Arrays.copyOfRange(arr, 0, ByteArrUtils.findNonZeroByteIndex(arr));
    }
}
