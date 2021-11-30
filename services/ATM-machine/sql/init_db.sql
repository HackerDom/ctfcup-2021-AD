CREATE SCHEMA IF NOT EXISTS prod;

DROP TYPE IF EXISTS prod.transaction_type CASCADE;
CREATE TYPE prod.transaction_type AS ENUM('withdraw', 'deposit', 'transfer');

DROP TABLE IF EXISTS prod.tbl_transactions;
CREATE TABLE IF NOT EXISTS prod.tbl_transactions(
    id bigint PRIMARY KEY,
    type prod.transaction_type,
    data bytea
);

DROP FUNCTION IF EXISTS prod.getById;
CREATE FUNCTION prod.getById (bigint) RETURNS table(id bigint, type prod.transaction_type, data bytea)
as 'SELECT * FROM prod.tbl_transactions WHERE id=$1;'
    LANGUAGE sql
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;

DROP PROCEDURE IF EXISTS prod.save;
CREATE PROCEDURE prod.save (bigint, prod.transaction_type, bytea)
LANGUAGE sql
as 'INSERT INTO prod.tbl_transactions (id, type, data) VALUES ($1, $2, $3);';

DROP FUNCTION IF EXISTS prod.getAll;
CREATE FUNCTION prod.getAll (integer) RETURNS table(id bigint, type prod.transaction_type, data bytea)
as 'SELECT * FROM prod.tbl_transactions LIMIT $1;'
    LANGUAGE sql
    IMMUTABLE
    RETURNS NULL ON NULL INPUT;
