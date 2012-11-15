DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TABLE guests (
	id SERIAL PRIMARY KEY,
	name VARCHAR(80) NOT NULL,
	email VARCHAR(80),
	seats_booked INTEGER NOT NULL,
	paid BOOLEAN
);

CREATE TABLE seats (
	id SERIAL PRIMARY KEY,
	number INTEGER NOT NULL,
	table_number INTEGER NOT NULL,
	guest_id INTEGER REFERENCES guests ON DELETE CASCADE ON UPDATE CASCADE
);

INSERT INTO guests (name, email, seats_booked) VALUES ('Matthew Brown', 'mnbbrown@gmail.com', 5);