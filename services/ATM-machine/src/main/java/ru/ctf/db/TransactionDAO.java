package ru.ctf.db;

import org.hibernate.HibernateException;
import org.hibernate.Session;
import org.hibernate.SessionFactory;
import org.hibernate.Transaction;
import org.hibernate.query.Query;
import ru.ctf.entities.TransferTransaction;
import ru.ctf.utils.HibernateSessionFactoryUtil;

import javax.naming.OperationNotSupportedException;
import java.util.Collections;
import java.util.List;
import java.util.logging.Logger;

public class TransactionDAO implements DAO<Long, TransferTransaction> {
    private static final Logger LOG = Logger.getLogger(TransactionDAO.class.getName());

    private final SessionFactory sessionFactory;

    public TransactionDAO() {
        sessionFactory = HibernateSessionFactoryUtil.getSessionFactory();
    }

    @Override
    public boolean save(TransferTransaction transferTransaction) {
        LOG.info("Saving transaction " + transferTransaction.getId());
        try (Session session = sessionFactory.openSession()) {
            Transaction transaction = session.beginTransaction();
            session.save(transferTransaction);
            transaction.commit();
            return true;
        } catch (HibernateException he) {
            LOG.warning(he.getMessage());
            return false;
        }
    }

    @Override
    public boolean delete(TransferTransaction transferTransaction) {
        return false;
    }

    @Override
    public TransferTransaction update(TransferTransaction transferTransaction) throws OperationNotSupportedException {
        LOG.info("Updating transaction " + transferTransaction.getId());
        throw new OperationNotSupportedException();
    }

    @Override
    public List<TransferTransaction> getAll(Integer offset, Integer limit) {
        LOG.info("Getting transactions with offset %s and limit %s".formatted(offset, limit));
        try (Session session = sessionFactory.openSession()) {
            Query<TransferTransaction> query = session
                    .createQuery("SELECT tt FROM TransferTransaction tt ORDER BY tt.creationTime DESC",
                            TransferTransaction.class)
                    .setFirstResult(offset)
                    .setMaxResults(limit);

            return query.list();
        } catch (HibernateException he) {
            LOG.warning(he.getMessage());
        }

        return Collections.emptyList();
    }

    @Override
    public TransferTransaction get(Long id) {
        LOG.info("Getting transaction by id " + id);
        try (Session session = sessionFactory.openSession()) {
            return session.get(TransferTransaction.class, id);
        } catch (HibernateException he) {
            LOG.warning(he.getMessage());
            return null;
        }
    }
}
