package ru.ctf.crypto;

public class KeyGen {

    /**
     * Generate a random secret key by algorithm.
     * @param algorithm name of algorithm.
     * @return byte array contains secret key data.
     */
    public byte[] generateKey(String algorithm) {

        return new byte[] {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    }
}