package ru.ctf.crypto;

import com.cryptojava.elephantass.keygen.DateBasedKeyGen;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.SecretKeySpec;
import javax.crypto.spec.IvParameterSpec;

public class CryptoServiceImpl implements CryptoService {
    private final SecretKey secretKey;
    private final IvParameterSpec iv; 

    public CryptoServiceImpl() {
        String algorithm = "AES";
        byte[] key = new DateBasedKeyGen().generateKey(16);
        secretKey = new SecretKeySpec(key, algorithm);
        iv = new IvParameterSpec("0102030405060708".getBytes());
    }

    public byte[] makeAes(byte[] rawMessage, int cipherMode) throws BadPaddingException {
        try {
            Cipher cipher = Cipher.getInstance("AES/CBC/PKCS5Padding");
            cipher.init(cipherMode, secretKey, iv);
            return cipher.doFinal(rawMessage);
        } catch (BadPaddingException badPaddingException) {
            throw badPaddingException;
        } catch (Exception e){
            throw new RuntimeException();
        }
    }
}
