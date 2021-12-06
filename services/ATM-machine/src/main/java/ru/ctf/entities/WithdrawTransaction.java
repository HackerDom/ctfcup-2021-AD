package ru.ctf.entities;

public record WithdrawTransaction(long id,
                                  String from,
                                  String to,
                                  double value,
                                  String comment) implements ClearTransaction {
    private static final TransactionType TYPE = TransactionType.WITHDRAW;

    @Override
    public TransactionType type() {
        return TYPE;
    }

    @Override
    public String toString() {
        return constructString();
    }
}
