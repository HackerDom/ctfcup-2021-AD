package ru.ctf.utils;

import ru.ctf.crypto.CryptoService;
import ru.ctf.crypto.CryptoServiceImpl;
import ru.ctf.entities.EncryptedTransaction;
import ru.ctf.entities.TransferTransaction;

import javax.crypto.BadPaddingException;
import javax.crypto.Cipher;
import java.util.UUID;

public class TransactionUtils {
    private final static CryptoService cryptoService = new CryptoServiceImpl();
    public static long generateUniqueId() {
        return UUID.randomUUID().getMostSignificantBits() & Long.MAX_VALUE;
    }

    public static EncryptedTransaction encryptTransaction(TransferTransaction transaction) {
        try {
            String stringBody = transaction.id() + ":" + transaction.from() + ":" + transaction.to() +
                    ":" + transaction.value() + ":" + transaction.comment();
            byte[] encryptBody = cryptoService.makeAes(stringBody.getBytes(), Cipher.ENCRYPT_MODE);
            return new EncryptedTransaction(transaction.id(), transaction.type(), encryptBody);
        } catch (Exception e) {
            throw new RuntimeException(e.getMessage());
        }
    }

    public static long getId(byte[] byteMsg) throws BadPaddingException {
        return Long.parseLong(new String(cryptoService.makeAes(byteMsg, Cipher.DECRYPT_MODE)).split(":")[0]);
    }
}
