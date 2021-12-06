package ru.ctf.entities;

public record TransactionPair(ClearTransaction transaction, EncryptedTransaction encryptedTransaction) {
}
