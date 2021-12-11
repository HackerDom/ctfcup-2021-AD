package ru.ctf.db;

import org.hibernate.HibernateException;
import org.hibernate.Session;
import org.hibernate.Transaction;
import ru.ctf.entities.TransferTransaction;
import ru.ctf.utils.HibernateSessionFactoryUtil;

import javax.persistence.criteria.CriteriaBuilder;
import javax.persistence.criteria.CriteriaDelete;
import javax.persistence.criteria.Root;
import java.sql.*;
import java.time.Duration;
import java.time.LocalDateTime;
import java.util.logging.Logger;

public class TableAlleviator {
    private static final Logger LOG = Logger.getLogger(TableAlleviator.class.getName());

    private final long diffInMinutes;

    public TableAlleviator(long differenceInMinutes) {
        diffInMinutes = differenceInMinutes;
    }
    
    public void alleviate() {
        final Timestamp deleteBeforeThis = Timestamp
                .valueOf(LocalDateTime.now().minus(Duration.ofMinutes(diffInMinutes)));
        LOG.info("Wingardium leviosa %s".formatted(deleteBeforeThis));

        try (Session session = HibernateSessionFactoryUtil.getSessionFactory().openSession()) {
            Transaction transaction = session.beginTransaction();
            session.createQuery(createTimeCriteriaDelete(deleteBeforeThis, session)).executeUpdate();

            transaction.commit();
        } catch (HibernateException he) {
            LOG.warning(he.getMessage());
        }
        LOG.info("Table is alleviated");
    }

    private CriteriaDelete<TransferTransaction> createTimeCriteriaDelete(Timestamp deleteBeforeThis, Session session) {
        CriteriaBuilder cb = session.getCriteriaBuilder();
        CriteriaDelete<TransferTransaction> delete = cb.createCriteriaDelete(TransferTransaction.class);
        Root<TransferTransaction> root = delete.from(TransferTransaction.class);
        delete.where(cb.lessThanOrEqualTo(root.get("creationTime"), deleteBeforeThis));
        return delete;
    }
}
