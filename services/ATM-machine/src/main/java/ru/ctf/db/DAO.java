package ru.ctf.db;

import javax.naming.OperationNotSupportedException;
import java.util.List;

public interface DAO<Key, Entity> {
    boolean save(Entity entity);
    boolean delete(Entity entity);
    Entity update(Entity entity) throws OperationNotSupportedException;
    List<Entity> getAll(Integer offset, Integer limit);
    Entity get(Key key);
}
