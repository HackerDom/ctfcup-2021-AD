package ru.ctf.utils;

import ru.ctf.crypto.CryptoService;
import ru.ctf.crypto.CryptoServiceImpl;
import ru.ctf.entities.TransferTransaction;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import java.util.UUID;

public class TransactionUtils {
    private final static CryptoService cryptoService = new CryptoServiceImpl();
    public static long generateUniqueId() {
        return UUID.randomUUID().getMostSignificantBits() & Long.MAX_VALUE;
    }

    public static byte[] encryptTransaction(TransferTransaction transaction) {
        try {
            String stringBody = transaction.getId() + ":" + transaction.getFromAcc() + ":" + transaction.getToAcc() +
                    ":" + transaction.getValue() + ":" + transaction.getComment();
            return cryptoService.makeAes(stringBody.getBytes(), Cipher.ENCRYPT_MODE);
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        }
    }

    public static long getId(byte[] byteMsg) throws BadPaddingException {
        return Long.parseLong(new String(cryptoService.makeAes(byteMsg, Cipher.DECRYPT_MODE)).split(":")[0]);
    }
}
