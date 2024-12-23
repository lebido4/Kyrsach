CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);


CREATE TABLE virtual_machines (
    id SERIAL PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    cpu INT NOT NULL,
    ram INT NOT NULL,
    disk INT NOT NULL,
    user_id INT REFERENCES users(id) ON DELETE CASCADE
);

INSERT INTO users (username, password) VALUES ('admin', '123');
INSERT INTO users (username, password) VALUES ('person_1', '456');
INSERT INTO users (username, password) VALUES ('person_2', 'admin');
INSERT INTO virtual_machines (name, cpu, ram, disk) VALUES ('Ubuntu', 4, 6, 122);
