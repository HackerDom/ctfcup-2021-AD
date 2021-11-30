package ru.ctf.entities;

public record WithdrawTransaction(long id) implements Transaction {
    private static final TransactionType TYPE = TransactionType.WITHDRAW;

    @Override
    public TransactionType type() {
        return TYPE;
    }
}
