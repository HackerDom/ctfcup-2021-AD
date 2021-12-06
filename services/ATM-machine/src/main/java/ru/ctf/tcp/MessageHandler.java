package ru.ctf.tcp;

import ru.ctf.db.DAO;
import ru.ctf.db.TransactionPairDAO;
import ru.ctf.entities.EncryptedTransaction;
import ru.ctf.entities.TransactionPair;
import ru.ctf.entities.TransferTransaction;
import ru.ctf.utils.TransactionUtils;

import java.util.Arrays;
import java.util.List;

public class MessageHandler {
    private final DAO<Long, TransactionPair> dao = new TransactionPairDAO();
    private final MessageValidator messageValidator = new MessageValidator();


    public byte[] handleMessage(String message, byte[] byteMsg) {
        String[] messageParts = message.split(" ");
        String strCommand = messageValidator.getValidCommand(messageParts);
        switch (Command.getCommandFromString(strCommand)) {
            case TRANSFER -> {
                if (messageValidator.validateTransfer(messageParts)) {
                    return getEncryptAndId(messageParts);
                }
                throw new RuntimeException();
            }
            case SHOW -> {
                if (messageValidator.validateShow(messageParts)) {
                    return getTransactionsBytes(
                            Integer.parseInt(messageParts[1]),
                            Integer.parseInt(messageParts[2])
                    );
                }
                throw new RuntimeException();
            }
            case CHECKID -> {
                if (messageValidator.validateCheckId(messageParts)) {
                    return getOriginTransaction(messageParts);
                }
                throw new RuntimeException();
            }
            case CHECK -> { return getCheckBytes(byteMsg); }
            case ClOSE -> { return new byte[1488]; }
            default -> throw new RuntimeException();
        }
    }

    private byte[] getCheckBytes(byte[] byteMsg) {
        int commandLen = "check ".getBytes().length;
        if (TransactionUtils.checkTransaction(Arrays.copyOfRange(byteMsg, commandLen, byteMsg.length))) {
            return "ok".getBytes();
        }
        return "error".getBytes();
    }

    private byte[] getOriginTransaction(String[] messageParts) {
        long id = Long.parseLong(messageParts[1]);
        TransactionPair transactionPair = dao.get(id);
        if (transactionPair == null) {
            return "not found".getBytes();
        }
        return transactionPair.transaction().toString().getBytes();
    }

    private byte[] getEncryptAndId(String[] messageParts) {
        TransferTransaction transaction = getTransaction(messageParts);
        EncryptedTransaction encryptedTransaction = TransactionUtils.encryptTransaction(transaction);
        dao.save(new TransactionPair(transaction, encryptedTransaction));
        byte[] idBytes = Long.toString(encryptedTransaction.id()).getBytes();
        byte[] resBytes = new byte[idBytes.length + encryptedTransaction.encryptedBody().length + 1];
        System.arraycopy(idBytes, 0, resBytes, 0, idBytes.length);
        resBytes[idBytes.length] = (byte) '\n';
        System.arraycopy(encryptedTransaction.encryptedBody(), 0, resBytes,
                idBytes.length + 1,
                resBytes.length - (idBytes.length + 1));
        return resBytes;
    }

    private byte[] getTransactionsBytes(Integer offset, Integer limit) {
        List<EncryptedTransaction> encryptedTransactions = dao.getAll(offset, limit).stream()
                .map(TransactionPair::encryptedTransaction)
                .toList();

        return concatWithDelimiter((byte) '\n', encryptedTransactions);
    }

    private TransferTransaction getTransaction(String[] messageParts) {
        long id = TransactionUtils.generateUniqueId();
        String from = messageParts[1];
        String to = messageParts[2];
        double value;
        try {
            value = Double.parseDouble(messageParts[3]);
        } catch (NumberFormatException exception) {
            throw new RuntimeException();
        }
        String comment = messageParts[4];
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

    private static class MessageValidator {
        private String getValidCommand(String[] messageParts) {
            if (messageParts.length >= 1) {
                return messageParts[0];
            }
            return "unknown";
        }

        private boolean validateTransfer(String[] messageParts) {
            if (messageParts.length == 5) {
                try {
                    Double.parseDouble(messageParts[3]);
                    return true;
                } catch (NumberFormatException e) {
                    return false;
                }
            }
            return false;
        }

        private boolean validateCheckId(String[] messageParts) {
            if (messageParts.length == 2) {
                try {
                    Long.parseLong(messageParts[1]);
                    return true;
                } catch (NumberFormatException e) {
                    return false;
                }
            }
            return false;
        }

        private boolean validateShow(String[] messageParts) {
            if (messageParts.length == 3) {
                try {
                    Integer.parseInt(messageParts[1]);
                    Integer.parseInt(messageParts[2]);

                    return true;
                } catch (NumberFormatException nfe) {
                    return false;
                }
            }

            return false;
        }
    }
}
