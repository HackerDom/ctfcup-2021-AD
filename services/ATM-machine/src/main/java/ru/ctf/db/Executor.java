package ru.ctf.db;

import ru.ctf.entities.TransactionType;

import java.io.IOException;
import java.io.InputStream;
import java.sql.*;
import java.util.Arrays;
import java.util.Map;
import java.util.Properties;
import java.util.stream.Collectors;

public class Executor {
    // TODO: поправить вызов функций посредством prepared statement (по-другому аргументы вставлять)
    private static final String FUNC_CALL_PATTERN = "SELECT prod.%s (%s);";
    private static final String PROC_CALL_PATTERN = "CALL prod.%s (%s);";

    private final ConnectionFactory connectionFactory;
    private final Validator validator;


    public Executor() {
        connectionFactory = new ConnectionFactory();
        validator = new Validator();
    }

    public ResultSet executeFunction(String funcName, Object... args) throws SQLException {
        if (!validator.validate(funcName, args)) return null;

        try (
                Connection conn = connectionFactory.createConnection();
                CallableStatement st = conn.prepareCall(
                        FUNC_CALL_PATTERN.formatted(funcName, Arrays.stream(args)
                                .map(Object::toString)
                                .collect(Collectors.joining(", ")))
                );
        ) {
            return st.executeQuery();
        }
    }

    public boolean callProcedure(String procName, Object... args) throws SQLException {
        if (!validator.validate(procName, args)) return false;

        try (
                Connection conn = connectionFactory.createConnection();
                CallableStatement st = conn.prepareCall(
                        FUNC_CALL_PATTERN.formatted(procName, Arrays.stream(args)
                                .map(Object::toString)
                                .collect(Collectors.joining(", ")))
                );
        ) {
            return st.execute();
        }
    }

    private static class ConnectionFactory {
        private static final String DB_PROPS = "database.properties";
        private final Properties properties;


        ConnectionFactory() {
            properties = readProperties();
        }

        Connection createConnection() throws SQLException {
            String url = properties.getProperty("url");
            if (url == null) throw new RuntimeException("Property 'url' isn't fount");

            return DriverManager.getConnection(url, properties);
        }

        private Properties readProperties() {
            Properties props = new Properties();
            try (InputStream is = Executor.class.getClassLoader().getResourceAsStream(DB_PROPS)) {
                props.load(is);
            } catch (IOException e) {
                e.printStackTrace();
            }

            return props;
        }
    }

    private static class Validator {
        @SuppressWarnings("rawtypes")
        private final Map<String, Class[]> funcAndArgs;

        Validator() {
            funcAndArgs = Map.of(
                    "getById", new Class[]{Long.class},
                    "save", new Class[] {Long.class, TransactionType.class, Byte[].class},
                    "getAll", new Class[] {Integer.class}
            );
        }

        boolean validate(String name, Object... args) {
            Class<?>[] validArgTypes = funcAndArgs.get(name);

            if (validArgTypes == null || validArgTypes.length != args.length)
                return false;

            for (short i = 0; i < validArgTypes.length; i++) {
                if (!(args[i].getClass() == validArgTypes[i]))
                    return false;
            }

            return true;
        }
    }
}
