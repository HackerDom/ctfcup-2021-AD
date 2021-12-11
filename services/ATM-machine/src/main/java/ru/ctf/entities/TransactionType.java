package ru.ctf.entities;

public enum TransactionType {
    WITHDRAW("withdraw"),
    DEPOSIT("deposit"),
    TRANSFER("transfer");
    private final String text;

    TransactionType(String text) {
        this.text = text.toLowerCase();
    }

    public String getText() {
        return text;
    }

    public static TransactionType getFromString(String text) {
        for (TransactionType value : values()) {
            if (value.text.equals(text))
                return value;
        }

        throw new RuntimeException("Cannot get transaction type from string");
    }
}
