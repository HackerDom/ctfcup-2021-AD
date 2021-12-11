CREATE SCHEMA IF NOT EXISTS bank;

DROP FUNCTION IF EXISTS bank.getById;
DROP FUNCTION IF EXISTS bank.getAll;
DROP PROCEDURE IF EXISTS bank.save;


DROP TABLE IF EXISTS bank.tbl_encrypted_transactions CASCADE;

DROP TABLE IF EXISTS bank.tbl_transactions CASCADE;
CREATE TABLE IF NOT EXISTS bank.tbl_transactions
(
    id            bigint PRIMARY KEY,
    encryptedData bytea,
    fromAcc       varchar(16),
    toAcc         varchar(16),
    value         numeric,
    comment       text,
    creationTime  timestamp
);
