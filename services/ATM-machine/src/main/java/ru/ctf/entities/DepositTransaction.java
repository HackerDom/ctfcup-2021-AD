package ru.ctf.entities;

public record DepositTransaction(long id) implements Transaction {
    private static final TransactionType TYPE = TransactionType.DEPOSIT;

    @Override
    public TransactionType type() {
        return TYPE;
    }
}
