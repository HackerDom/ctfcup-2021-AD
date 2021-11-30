package ru.ctf.entities;

/**
 * The type of transactions stored in the database and transmitted to users
 */
public record EncryptedTransaction(long id, TransactionType type, byte[] encryptedBody) implements Transaction { }
