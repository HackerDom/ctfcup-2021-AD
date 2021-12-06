CREATE SCHEMA IF NOT EXISTS bank;

DROP FUNCTION IF EXISTS bank.getById;
DROP FUNCTION IF EXISTS bank.getAll;
DROP PROCEDURE IF EXISTS bank.save;


DROP TABLE IF EXISTS bank.tbl_encrypted_transactions CASCADE;
CREATE TABLE IF NOT EXISTS bank.tbl_encrypted_transactions
(
    id           bigint PRIMARY KEY,
    type         varchar(16),
    data         bytea,
    creationTime timestamp
);

DROP TABLE IF EXISTS bank.tbl_transactions CASCADE;
CREATE TABLE IF NOT EXISTS bank.tbl_transactions
(
    id           bigint REFERENCES bank.tbl_encrypted_transactions (id)
            ON DELETE CASCADE,
    type         varchar(16),
    fromAcc      varchar(16),
    toAcc        varchar(16),
    value        numeric,
    comment      text,
    creationTime timestamp
);

CREATE OR REPLACE FUNCTION bank.getAll(_offset integer, _limit integer)
    RETURNS table
            (
                id            bigint,
                type          varchar(16),
                fromAcc       varchar(16),
                toAcc         varchar(16),
                value         numeric,
                comment       text,
                encryptedData bytea
            )
as
'SELECT t.id      as id,
        t.type    as type,
        t.fromAcc as fromAcc,
        t.toAcc   as toAcc,
        t.value   as value,
        t.comment as comment,
        et.data   as encryptedData
 FROM bank.tbl_encrypted_transactions et
          LEFT JOIN bank.tbl_transactions t ON et.id = t.id
ORDER BY t.creationtime desc
OFFSET _offset LIMIT _limit;'
    LANGUAGE sql
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;


CREATE OR REPLACE FUNCTION bank.getById(bigint)
    RETURNS table
            (
                id            bigint,
                type          varchar(16),
                fromAcc       varchar(16),
                toAcc         varchar(16),
                value         numeric,
                comment       text,
                encryptedData bytea
            )
as
'SELECT et.id     as id,
        et.type   as type,
        t.fromAcc as fromAcc,
        t.toAcc   as toAcc,
        t.value   as value,
        t.comment as comment,
        et.data   as encryptedData
 FROM (SELECT *
       FROM bank.tbl_encrypted_transactions
       WHERE id = $1) et
          LEFT JOIN bank.tbl_transactions t ON et.id = t.id;'
    LANGUAGE sql
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;


CREATE OR REPLACE PROCEDURE bank.saveEncrypted(bigint, varchar(16), bytea, timestamp)
    LANGUAGE sql
as
$$
INSERT INTO bank.tbl_encrypted_transactions (id, type, data, creationTime)
VALUES ($1, $2, $3, $4);
$$;

CREATE OR REPLACE PROCEDURE bank.save(
    _id bigint,
    _type varchar(16),
    _fromAcc varchar(16),
    _toAcc varchar(16),
    _value double precision,
    _comment text,
    _creationTime timestamp
)
    LANGUAGE sql
as
$$
INSERT INTO bank.tbl_transactions (id, type, fromAcc, toAcc, value, comment, creationTime)
VALUES (_id, _type, _fromAcc, _toAcc, _value, _comment, _creationTime);
$$;

CREATE OR REPLACE PROCEDURE bank.deleteOldTransactions(timestamp)
    LANGUAGE sql
as
'DELETE
 FROM bank.tbl_encrypted_transactions
 WHERE creationTime <= $1;';
