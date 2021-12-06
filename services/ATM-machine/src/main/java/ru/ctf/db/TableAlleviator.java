package ru.ctf.db;

import java.sql.*;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.logging.Logger;

public class TableAlleviator {
    private static final Logger LOG = Logger.getLogger(TableAlleviator.class.getName());

    private final String schemaName = "bank";
    private final long diffInMinutes;

    public TableAlleviator(long differenceInMinutes) {
        diffInMinutes = differenceInMinutes;
    }
    
    public void alleviate() {
        final Timestamp deleteBeforeThis = Timestamp
                .valueOf(LocalDateTime.now().minus(Duration.ofMinutes(diffInMinutes)));
        LOG.info("Wingardium leviosa %s".formatted(deleteBeforeThis));
        try (Connection conn = ConnectionFactory.createConnection();
             PreparedStatement st = conn.prepareStatement("CALL %s.deleteoldtransactions (?);".formatted(schemaName))) {
            st.setTimestamp(1, deleteBeforeThis);
            st.execute();
        } catch (SQLException sqlEx) {
            LOG.warning(sqlEx.getMessage());
        }
    }
}
