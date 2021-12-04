package ru.ctf.crypto;

public interface CryptoService {
    byte[] makeAes(byte[] rawMessage, int cipherMode);
}
