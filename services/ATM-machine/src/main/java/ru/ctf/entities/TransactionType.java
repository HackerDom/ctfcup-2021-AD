package ru.ctf.entities;

public enum TransactionType {
    WITHDRAW("withdraw"),
    DEPOSIT("deposit"),
    TRANSFER("transfer");
    private final String text;

    TransactionType(String text) {
        // must be validated
        this.text = text.toLowerCase();
    }
}
