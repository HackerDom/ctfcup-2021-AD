package ru.ctf.entities;

public record TransferTransaction(
        long id,
        String from,
        String to,
        double value,
        String comment) implements ClearTransaction {
    private static final TransactionType TYPE = TransactionType.TRANSFER;

    @Override
    public TransactionType type() {
        return TYPE;
    }

    @Override
    public String toString() {
        return constructString();
    }
}
