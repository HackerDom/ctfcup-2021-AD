package ru.ctf.db;

import ru.ctf.entities.*;

import javax.naming.OperationNotSupportedException;
import java.sql.*;
import java.time.LocalDateTime;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;
import java.util.logging.Logger;

public class TransactionPairDAO implements DAO<Long, TransactionPair> {
    private static final Logger LOG = Logger.getLogger(TransactionPairDAO.class.getName());

    private final String schemaName = "bank";
    private final Map<String, String> CALL_PATTERNS = Map.of(
            "save", "CALL %s.save (?, ?, ?, ?, ?, ?, ?);".formatted(schemaName),
            "saveEncrypted", "CALL %s.saveencrypted (?, ?, ?, ?);".formatted(schemaName),
            "getAll", "SELECT * FROM %s.getall (?, ?);".formatted(schemaName),
            "getById", "SELECT * FROM %s.getbyid (?);".formatted(schemaName)
    );


    @Override
    public boolean save(TransactionPair transactionPair) {
        final ClearTransaction transaction = transactionPair.transaction();
        LOG.info("Saving transaction (id: %s, type: %s)".formatted(transaction.id(), transaction.type()));
        Timestamp creationTime = Timestamp.valueOf(LocalDateTime.now());
        try (Connection conn = ConnectionFactory.createConnection();
             PreparedStatement stSave = conn.prepareStatement(CALL_PATTERNS.get("save"));
             PreparedStatement stEncSave = conn.prepareStatement(CALL_PATTERNS.get("saveEncrypted"))) {
            setEncryptedSaveArgs(
                    stEncSave,
                    transaction.id(), transaction.type(),
                    transactionPair.encryptedTransaction().encryptedBody(), creationTime
            );
            setSaveProcedureArgs(
                    stSave,
                    transaction.id(), transaction.type(),
                    transaction.from(), transaction.to(), transaction.value(),
                    transaction.comment(), creationTime
            );
            stEncSave.execute();
            stSave.execute();
        } catch (SQLException sqlEx) { // TODO: я бы сказал, что нужна более детальная обработка, но пока непонятно
            LOG.warning(sqlEx.getMessage());
        }

        return true;
    }

    @Override
    public boolean delete(TransactionPair transactionPair) {
        return false;
    }

    @Override
    public TransactionPair update(TransactionPair transactionPair) throws OperationNotSupportedException {
        final Transaction transaction = transactionPair.transaction();
        LOG.info("Updating transaction (id: %s, type: %s)".formatted(transaction.id(), transaction.type()));
        throw new OperationNotSupportedException();
    }

    @Override
    public List<TransactionPair> getAll(Integer offset, Integer limit) {
        LOG.info("Getting transaction list");
        List<TransactionPair> pairs = new LinkedList<>();
        try (Connection conn = ConnectionFactory.createConnection();
             PreparedStatement st = conn.prepareStatement(CALL_PATTERNS.get("getAll"))) {
            st.setInt(1, offset);
            st.setInt(2, limit);
            try (ResultSet queryRes = st.executeQuery()) {
                while (queryRes.next()) {
                    pairs.add(constructTransactionPair(queryRes));
                }
            }
        } catch (SQLException sqlEx) {
            LOG.warning(sqlEx.getMessage());
        }

        return pairs;
    }

    @Override
    public TransactionPair get(Long id) {
        LOG.info("Getting transaction by id=%s".formatted(id));
        try (Connection conn = ConnectionFactory.createConnection();
             PreparedStatement st = conn.prepareStatement(CALL_PATTERNS.get("getById"))) {
            st.setLong(1, id);
            try (ResultSet queryRes = st.executeQuery()) {
                if (!queryRes.next())
                    return null;

                return constructTransactionPair(queryRes);
            }
        } catch (SQLException sqlEx) {
            LOG.warning(sqlEx.getMessage());
        }

        return null;
    }

    private TransactionPair constructTransactionPair(ResultSet queryRes) throws SQLException {
        long id = queryRes.getLong("id");
        TransactionType type = TransactionType.getFromString(queryRes.getString("type"));
        String from = queryRes.getString("fromAcc");
        String to = queryRes.getString("toAcc");
        double value = queryRes.getDouble("value");
        String comment = queryRes.getString("comment");
        ClearTransaction transaction = switch (type) {
            case TRANSFER -> new TransferTransaction(id, from, to, value, comment);
            case WITHDRAW -> new WithdrawTransaction(id, from, to, value, comment);
            case DEPOSIT -> new DepositTransaction(id, from, to, value, comment);
        };

        return new TransactionPair(
                transaction,
                new EncryptedTransaction(id, type, queryRes.getBytes("encryptedData"))
        );
    }

    private void setSaveProcedureArgs(PreparedStatement st,
                                      long id,
                                      TransactionType type,
                                      String from,
                                      String to,
                                      double value,
                                      String comment,
                                      Timestamp creationTime)
            throws SQLException {
        st.setLong(1, id);
        st.setString(2, type.getText());
        st.setString(3, from);
        st.setString(4, to);
        st.setDouble(5, value);
        st.setString(6, comment);
        st.setTimestamp(7, creationTime);
    }

    private void setEncryptedSaveArgs(PreparedStatement st,
                                      long id,
                                      TransactionType type,
                                      byte[] rawData,
                                      Timestamp creationTime) throws SQLException {
        st.setLong(1, id);
        st.setString(2, type.getText());
        st.setBytes(3, rawData);
        st.setTimestamp(4, creationTime);
    }
}
