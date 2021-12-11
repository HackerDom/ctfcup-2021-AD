package ru.ctf.entities;

public interface Transaction {
    TransactionType getType();

    Long getId();
}
