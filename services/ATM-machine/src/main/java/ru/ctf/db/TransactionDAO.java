package ru.ctf.db;

import ru.ctf.entities.*;

import javax.naming.OperationNotSupportedException;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.LinkedList;
import java.util.List;

public class TransactionDAO implements DAO<Long, EncryptedTransaction> {

    private final Executor executor;

    public TransactionDAO() {
        executor = new Executor();
    }

    @Override
    public boolean save(EncryptedTransaction transaction) {
        try {
            return executor.callProcedure(
                    "save",
                    transaction.id(),
                    transaction.type(),
                    transaction.encryptedBody()
            );
        } catch (SQLException e) { // я бы сказал, что нужна более детальная обработка, но пока непонятно
            e.printStackTrace();
        }

        return false;
    }

    @Override
    public boolean delete(EncryptedTransaction transaction) {
        return false;
    }

    @Override
    public EncryptedTransaction update(EncryptedTransaction transaction) throws OperationNotSupportedException {
        throw new OperationNotSupportedException();
    }

    @Override
    public List<EncryptedTransaction> getAll() {
        List<EncryptedTransaction> transactions = new LinkedList<>();
        try {
            ResultSet queryRes = executor.executeFunction("getAll", 10);
            while (queryRes.next()) {
                transactions.add(
                        constructTransaction(queryRes)
                );
            }
        } catch (SQLException sqlEx) {
            sqlEx.printStackTrace();
        }

        return transactions;
    }

    @Override
    public EncryptedTransaction get(Long id) {
        try (ResultSet queryRes = executor.executeFunction("getById", id)) {
            if (!queryRes.first())
                return null;

            return constructTransaction(queryRes);
//            final long transactionId = queryRes.getLong("id");
//            return switch ((TransactionType) queryRes.getObject("type")) {
//                case TRANSFER -> new TransferTransaction(transactionId);
//                case DEPOSIT -> new DepositTransaction(transactionId);
//                case WITHDRAW -> new WithdrawTransaction(transactionId);
//            };

        } catch (SQLException sqlEx) {
            sqlEx.printStackTrace();
        } catch (ClassCastException cce) {
            throw new RuntimeException("Something went wrong with database settings");
        }

        return null;
    }

    private EncryptedTransaction constructTransaction(ResultSet queryRes) throws SQLException {
        return new EncryptedTransaction(
                queryRes.getLong("id"),
                (TransactionType) queryRes.getObject("type"),
                queryRes.getBytes("data")
        );
    }
}
