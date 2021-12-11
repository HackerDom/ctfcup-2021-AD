package ru.ctf.entities;


import javax.persistence.*;
import java.sql.Timestamp;

@Entity
@Table(name = "tbl_transactions")
public class TransferTransaction implements ClearTransaction {
    private static final TransactionType TYPE = TransactionType.TRANSFER;

    @Id
    private Long id;

    private String fromAcc;
    private String toAcc;
    private Double value;
    private String comment;
    @Column(name = "encrypteddata")
    private byte[] encryptedData;
    @Column(name = "creationtime")
    private Timestamp creationTime;


    public TransferTransaction(long id,
                               String fromAcc,
                               String toAcc,
                               double value,
                               String comment,
                               byte[] encryptedData,
                               Timestamp creationTime) {
        this.id = id;
        this.fromAcc = fromAcc;
        this.toAcc = toAcc;
        this.value = value;
        this.comment = comment;
        this.encryptedData = encryptedData;
        this.creationTime = creationTime;
    }

    public TransferTransaction() {

    }

    @Override
    public String getFromAcc() {
        return fromAcc;
    }

    @Override
    public String getToAcc() {
        return toAcc;
    }

    @Override
    public Double getValue() {
        return value;
    }

    @Override
    public String getComment() {
        return comment;
    }

    @Override
    public TransactionType getType() {
        return TYPE;
    }

    @Override
    public Long getId() {
        return id;
    }

    public byte[] getEncryptedData() {
        return encryptedData;
    }

    public Timestamp getCreationTime() {
        return creationTime;
    }

    public void setCreationTime(Timestamp creationTime) {
        this.creationTime = creationTime;
    }

    public void setEncryptedData(byte[] encryptedData) {
        this.encryptedData = encryptedData;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public void setFromAcc(String fromAcc) {
        this.fromAcc = fromAcc;
    }

    public void setToAcc(String toAcc) {
        this.toAcc = toAcc;
    }

    public void setValue(Double value) {
        this.value = value;
    }

    public void setComment(String comment) {
        this.comment = comment;
    }

    @Override
    public String toString() {
        return constructString();
    }
}
