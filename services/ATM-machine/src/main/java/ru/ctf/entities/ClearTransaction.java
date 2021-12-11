package ru.ctf.entities;

public interface ClearTransaction extends Transaction {
    String getFromAcc();
    String getToAcc();
    Double getValue();
    String getComment();
    default String constructString() {
        return """
                {"from":"%s","to":"%s","value":"%.02f","comment":"%s"}""".formatted(getFromAcc(), getToAcc(), getValue(), getComment());
    }
}
