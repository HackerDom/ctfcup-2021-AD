package ru.ctf.crypto;

import javax.crypto.BadPaddingException;

public interface CryptoService {
    byte[] makeAes(byte[] rawMessage, int cipherMode) throws BadPaddingException;
}
