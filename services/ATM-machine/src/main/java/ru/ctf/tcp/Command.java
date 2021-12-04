package ru.ctf.tcp;

public enum Command {
    TRANSFER("transfer"),
    CHECK("check"),
    SHOW("show");
    private final String text;

    Command(String text) {
        this.text = text.toLowerCase();
    }
}
