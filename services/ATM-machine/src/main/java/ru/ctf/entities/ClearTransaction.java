package ru.ctf.entities;

public interface ClearTransaction extends Transaction{
    String from();
    String to();
    double value();
    String comment();
    default String constructString() {
        return """
                {"from":"%s","to":"%s","value":"%.02f","comment":"%s"}
                """.formatted(from(), to(), value(), comment());
    }
}
