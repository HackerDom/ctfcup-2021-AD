package ru.ctf.utils;

import java.nio.ByteBuffer;
import java.util.Arrays;

public class BufferUtils {
    public static void clearBuffer(ByteBuffer buffer) {
        buffer.clear();
        Arrays.fill(buffer.array(), (byte) 0);
        buffer.clear();
    }

    public static int findNonZeroByteIndex(ByteBuffer buffer) {
        byte[] arr = buffer.array();
        for (int i = arr.length - 1; i >= 0; i--) {
            if (arr[i] != 0) {
                return i + 1;
            }
        }
        return 0;
    }

    public static byte[] getNonZeroBytes(ByteBuffer buffer) {
        return Arrays.copyOfRange(buffer.array(), 0, BufferUtils.findNonZeroByteIndex(buffer));
    }

    public static String getStringFromBuffer(ByteBuffer buffer) {
        return new String(getNonZeroBytes(buffer)).trim();
    }

    public static void fillBuffer(ByteBuffer buffer, byte[] data) {
        clearBuffer(buffer);
        buffer.put(data);
    }
}
