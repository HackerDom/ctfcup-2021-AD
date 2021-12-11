package ru.ctf.tcp;

import ru.ctf.db.DAO;
import ru.ctf.db.TransactionDAO;
import ru.ctf.entities.TransferTransaction;
import ru.ctf.utils.TransactionUtils;

import javax.crypto.BadPaddingException;
import java.sql.Timestamp;
import java.time.Instant;
import java.util.Arrays;
import java.util.List;

public class MessageHandler {
    private final DAO<Long, TransferTransaction> dao = new TransactionDAO();
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
                    byte[] transactions = getTransactionsBytes(
                            Integer.parseInt(messageParts[1]),
                            Math.min(Integer.parseInt(messageParts[2]), 20)
                    );
                    return transactions.length > 0 ? transactions : "empty".getBytes();
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
            case ClOSE -> { return new byte[1000]; }
            default -> throw new RuntimeException();
        }
    }

    private byte[] getCheckBytes(byte[] byteMsg) {
        try {
            int commandLen = "check ".getBytes().length;
            long id = TransactionUtils.getId(Arrays.copyOfRange(byteMsg, commandLen, byteMsg.length));
            TransferTransaction transaction = dao.get(id);
            if (transaction == null) {
                return "not found".getBytes();
            } else {
                return "ok".getBytes();
            }
        } catch (BadPaddingException badPaddingException) {
            return "error".getBytes();
        }
    }

    private byte[] getOriginTransaction(String[] messageParts) {
        long id = Long.parseLong(messageParts[1]);
        TransferTransaction transaction = dao.get(id);
        if (transaction == null) {
            return "not found".getBytes();
        }
        return transaction.toString().getBytes();
    }

    private byte[] getEncryptAndId(String[] messageParts) {
        TransferTransaction transaction = getTransaction(messageParts);
        byte[] encryptedBody = TransactionUtils.encryptTransaction(transaction);
        transaction.setEncryptedData(encryptedBody);
        dao.save(transaction);
        byte[] idBytes = Long.toString(transaction.getId()).getBytes();
        byte[] resBytes = new byte[idBytes.length + encryptedBody.length + 1];
        System.arraycopy(idBytes, 0, resBytes, 0, idBytes.length);
        resBytes[idBytes.length] = (byte) '\n';
        System.arraycopy(encryptedBody, 0, resBytes,
                idBytes.length + 1,
                resBytes.length - (idBytes.length + 1));
        return resBytes;
    }

    private byte[] getTransactionsBytes(Integer offset, Integer limit) {
        List<byte[]> encryptedTransactions = dao.getAll(offset, limit).stream()
                .map(TransferTransaction::getEncryptedData)
                .toList();
        return concatWithDelimiter("separator".getBytes(), encryptedTransactions);
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
        return new TransferTransaction(id, from, to, value, comment, new byte[0], Timestamp.from(Instant.now()));
    }

    public static byte[] concatWithDelimiter(byte[] delimiter, List<byte[]> encryptedBodies) {
        byte[] concatenated = new byte[calculateConcatenationLength(encryptedBodies)];
        int currentIndex = 0;
        for (int i = 0; i < encryptedBodies.size(); i++) {
            byte[] arr = encryptedBodies.get(i);
            for (byte b : arr) {
                concatenated[currentIndex++] = b;
            }
            if (i != encryptedBodies.size() - 1) {
                for (byte byt : delimiter) {
                    concatenated[currentIndex++] = byt;
                }
            }
        }

        return concatenated;
    }

    private static int calculateConcatenationLength(List<byte[]> encryptedBodies) {
        return encryptedBodies.isEmpty() ? 0 : encryptedBodies.stream()
                .mapToInt(arr -> arr.length + 9).sum() - 9;
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
                    return Integer.parseInt(messageParts[1]) >= 0 && Integer.parseInt(messageParts[2]) >= 0;
                } catch (NumberFormatException nfe) {
                    return false;
                }
            }

            return false;
        }
    }
}
