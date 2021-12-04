package ru.ctf.entities;

public interface Transaction {
    TransactionType type();

    long id();
}
