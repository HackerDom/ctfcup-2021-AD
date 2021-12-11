package ru.ctf.utils;

import org.hibernate.SessionFactory;
import org.hibernate.boot.registry.StandardServiceRegistryBuilder;
import org.hibernate.cfg.Configuration;
import ru.ctf.entities.TransferTransaction;
import ru.ctf.tcp.TCPServer;

import java.io.IOException;
import java.util.Properties;

public class HibernateSessionFactoryUtil {
    private static SessionFactory sessionFactory;
    private static final String DB_PROPS = "database.properties";

    public static SessionFactory getSessionFactory() {
        if (sessionFactory == null) {
            Configuration configuration = new Configuration();
            Properties properties = new Properties();
            try {
                properties.load(TCPServer.class.getClassLoader().getResourceAsStream(DB_PROPS));
            } catch (IOException e) {
                throw new IllegalArgumentException("Troubles with '%s' file".formatted(DB_PROPS), e);
            }
            configuration.addProperties(properties);
            configuration.addAnnotatedClass(TransferTransaction.class);
            StandardServiceRegistryBuilder builder = new StandardServiceRegistryBuilder()
                    .applySettings(configuration.getProperties());

            sessionFactory = configuration.buildSessionFactory(builder.build());
        }

        return sessionFactory;
    }
}
