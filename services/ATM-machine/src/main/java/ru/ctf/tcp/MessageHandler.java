package ru.ctf.tcp;

import ru.ctf.db.DAO;
import ru.ctf.db.TransactionDAO;
import ru.ctf.entities.EncryptedTransaction;
import ru.ctf.entities.TransferTransaction;
import ru.ctf.utils.TransactionUtils;

import java.util.List;

public class MessageHandler {
    private final DAO<Long, EncryptedTransaction> dao = new TransactionDAO();


    public byte[] handleMessage(String message) {
        String[] massageParts = message.split(" ");
        try {
            return switch (Command.valueOf(massageParts[0])) {
                case TRANSFER -> getEncryptedBytes(massageParts);
                case SHOW -> getTransactionsBytes();
                case CHECK -> getCheckBytes(massageParts);
            };
        } catch (IllegalArgumentException iae) {
            throw new RuntimeException(iae);
        }
    }

    private byte[] getCheckBytes(String[] massageParts) {
        // todo: как-то завуалировано говорить, что можно расшифровать
        if (TransactionUtils.checkTransaction(massageParts[1])) {
            return "ok".getBytes();
        }
        return "not ok".getBytes();
    }

    private byte[] getEncryptedBytes(String[] massageParts) {
        // todo: допилить валидацию
        TransferTransaction transaction = getTransaction(massageParts);
        EncryptedTransaction encryptedTransaction = TransactionUtils.encryptTransaction(transaction);
        dao.save(encryptedTransaction);
        return encryptedTransaction.encryptedBody();
    }

    private byte[] getTransactionsBytes() {
        List<EncryptedTransaction> encryptedTransactions = dao.getAll();

        return concatWithDelimiter((byte)'\n', encryptedTransactions);
    }

    private boolean validate(String[] messageParts) {
        return true;
    }

    private TransferTransaction getTransaction(String[] massageParts) {
        long id = TransactionUtils.generateUniqueId();
        String from = massageParts[1];
        String to = massageParts[2];
        double value;
        try {
            value = Double.parseDouble(massageParts[3]);
        } catch (NumberFormatException exception) {
            throw new RuntimeException();
        }
        String comment = massageParts[4];
        return new TransferTransaction(id, from, to, value, comment);
    }

    public static byte[] concatWithDelimiter(byte delimiter, List<EncryptedTransaction> transactions) {
        byte[] concatenated = new byte[calculateConcatenationLength(transactions)];
        int currentIndex = 0;
        for (int i = 0; i < transactions.size(); i++) {
            byte[] arr = transactions.get(i).encryptedBody();
            for (byte b : arr) {
                concatenated[currentIndex++] = b;
            }
            if (i != transactions.size() - 1) {
                concatenated[currentIndex++] = delimiter;
            }
        }

        return concatenated;
    }

    private static int calculateConcatenationLength(List<EncryptedTransaction> transactions) {
        return transactions.stream()
                .map(EncryptedTransaction::encryptedBody)
                .mapToInt(arr -> arr.length + 1).sum() - 1;
    }
}
