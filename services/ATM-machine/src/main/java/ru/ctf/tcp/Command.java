package ru.ctf.tcp;

public enum Command {
    TRANSFER("transfer"),
    CHECK("check"),
    SHOW("show"),
    CHECKID("checkid"),
    ClOSE("");
    private final String text;

    Command(String text) {
        this.text = text.toLowerCase();
    }

    public static Command getCommandFromString(String strCommand) {
        for (Command value : values()) {
            if (value.text.equals(strCommand))
                return value;
        }

        throw new RuntimeException("Cannot get transaction type from string");
    }
}
