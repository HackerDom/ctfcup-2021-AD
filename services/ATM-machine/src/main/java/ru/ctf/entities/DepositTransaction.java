package ru.ctf.entities;

public record DepositTransaction(long id,
                                 String from,
                                 String to,
                                 double value,
                                 String comment) implements ClearTransaction {
    private static final TransactionType TYPE = TransactionType.DEPOSIT;

    @Override
    public TransactionType type() {
        return TYPE;
    }

    @Override
    public String toString() {
        return constructString();
    }
}
