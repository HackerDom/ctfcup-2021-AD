package ru.ctf.crypto;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import java.security.NoSuchAlgorithmException;
import java.util.Arrays;
import java.util.stream.IntStream;

public class CryptoServiceImpl implements CryptoService {
    private SecretKey secretKey;

    public CryptoServiceImpl() {
//            Byte[] key = Arrays.copyOf(IntStream.range(1, 17).boxed().toArray(), 16, Byte[].class);
        byte[] key = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
        SecretKeySpec secretKeySpec = new SecretKeySpec(key, "AES");
        secretKey = secretKeySpec;
    }

    public byte[] makeAes(byte[] rawMessage, int cipherMode) {
        try {
            Cipher cipher = Cipher.getInstance("AES");
            cipher.init(cipherMode, secretKey);
            byte [] output = cipher.doFinal(rawMessage);
            return output;
        } catch (Exception e){
            return null;
        }
    }
}
