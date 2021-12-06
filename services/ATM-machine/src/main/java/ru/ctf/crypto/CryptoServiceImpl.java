package ru.ctf.crypto;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;

public class CryptoServiceImpl implements CryptoService {
    private final SecretKey secretKey;

    public CryptoServiceImpl() {
        String algorithm = "AES";
        byte[] key = new KeyGen().generateKey(algorithm);
        secretKey = new SecretKeySpec(key, algorithm);
    }

    public byte[] makeAes(byte[] rawMessage, int cipherMode) {
        try {
            Cipher cipher = Cipher.getInstance("AES");
            cipher.init(cipherMode, secretKey);

            return cipher.doFinal(rawMessage);
        } catch (Exception e){
            return null;
        }
    }
}
