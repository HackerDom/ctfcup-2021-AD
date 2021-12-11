package ru.ctf.entities;

public class WithdrawTransaction implements ClearTransaction {
    private static final TransactionType TYPE = TransactionType.WITHDRAW;

    private final long id;
    private final String from;
    private final String to;
    private final double value;
    private final String comment;

    public WithdrawTransaction(long id, String from, String to, double value, String comment) {
        this.id = id;
        this.from = from;
        this.to = to;
        this.value = value;
        this.comment = comment;
    }

    public TransactionType getType() {
        return TYPE;
    }

    @Override
    public Long getId() {
        return id;
    }

    @Override
    public String getFromAcc() {
        return from;
    }

    @Override
    public String getToAcc() {
        return to;
    }

    @Override
    public Double getValue() {
        return value;
    }

    @Override
    public String getComment() {
        return comment;
    }
}
