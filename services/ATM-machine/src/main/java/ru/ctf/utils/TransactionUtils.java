package ru.ctf.utils;

import ru.ctf.crypto.CryptoService;
import ru.ctf.crypto.CryptoServiceImpl;
import ru.ctf.entities.EncryptedTransaction;
import ru.ctf.entities.TransferTransaction;

import javax.crypto.Cipher;
import java.util.UUID;

public class TransactionUtils {
    private final static CryptoService cryptoService = new CryptoServiceImpl();
    public static long generateUniqueId() {
        return UUID.randomUUID().getMostSignificantBits() & Long.MAX_VALUE;
    }

    public static EncryptedTransaction encryptTransaction(TransferTransaction transaction) {
        String stringBody = transaction.from() + transaction.to() + transaction.value() + transaction.comment();
        byte[] encryptBody = cryptoService.makeAes(stringBody.getBytes(), Cipher.ENCRYPT_MODE);
        return new EncryptedTransaction(transaction.id(), transaction.type(), encryptBody);
    }

    public static boolean checkTransaction(String massage) {
        byte[] decryptBody = cryptoService.makeAes(massage.getBytes(), Cipher.DECRYPT_MODE);
        return decryptBody != null;
    }
}
