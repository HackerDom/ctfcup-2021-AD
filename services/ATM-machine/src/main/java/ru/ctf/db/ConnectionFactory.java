package ru.ctf.db;

import java.io.IOException;
import java.io.InputStream;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.Properties;

public class ConnectionFactory {
    private static final String DB_PROPS = "database.properties";
    private static final Properties properties = readProperties();

    public static Connection createConnection() throws SQLException {
        String url = properties.getProperty("url");
        if (url == null) throw new RuntimeException("Property 'url' isn't fount");

        return DriverManager.getConnection(url, properties);
    }

    private static Properties readProperties() {
        Properties props = new Properties();
        try (InputStream is = ConnectionFactory.class.getClassLoader().getResourceAsStream(DB_PROPS)) {
            props.load(is);
        } catch (IOException e) {
            e.printStackTrace();
        }

        return props;
    }
}
