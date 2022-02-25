DROP DATABASE IF EXISTS bot_db;
SHOW WARNINGS;
CREATE DATABASE bot_db;

USE bot_db;
CREATE TABLE userdata(
    id INT AUTO_INCREMENT NOT NULL,
	uid VARCHAR(100),
	d_id VARCHAR(100),
	lvl	INT,
	warns INT,
	msg INT,
	join_date VARCHAR(100),
	money INT,
	xp INT,
   growth FLOAT,
   description VARCHAR(100) DEFAULT 'Nothing to describe',
   robbed_success INT DEFAULT 0,
   robbed_fail INT DEFAULT 0,
   worked_hours INT DEFAULT 0,
   inventory_slot_one VARCHAR(255) DEFAULT "Leer",
   inventory_slot_two VARCHAR(255) DEFAULT "Leer",
   inventory_slot_three VARCHAR(255) DEFAULT "Leer",
   PRIMARY KEY(uid)
);


CREATE TABLE homework(
	h_id INT AUTO_INCREMENT,
	task VARCHAR(255),
	task_date VARCHAR(255),
	PRIMARY KEY(h_id)
);

CREATE TABLE classtest(
	c_id INT AUTO_INCREMENT,
	test VARCHAR(255),
	test_date VARCHAR(255),
	PRIMARY KEY(c_id)
);

CREATE TABLE news(
	n_id INT AUTO_INCREMENT,
	news VARCHAR(255),
	news_date VARCHAR(255),
	PRIMARY KEY(n_id)
);

CREATE TABLE warns(
    warn_id INT PRIMARY KEY AUTO_INCREMENT,
    warn_info TEXT,
    user_id INT,
    warn_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY user_id(user_id) REFERENCES userdata(id)
);

CREATE TABLE economy_variables(
    lottery_pot INT
);

CREATE TABLE case_items(
	item_id INT PRIMARY KEY AUTO_INCREMENT,
	item_name VARCHAR(255),
	item_description VARCHAR(255),
	item_price INT,
	item_type VARCHAR(255),
	item_rarity INT
);

INSERT INTO case_items(
	item_name,
	item_description,
	item_price,
	item_type,
	item_rarity
) VALUES (
	"Random Money Drop - Solo",
	"Entweder der Schlüssel ist wieder drin oder nicht.",
	"100",
	"Money Drop",
	"1"
),
(
	"Messer",
	"Dieses Messer erhöht die Wahrscheinlichkeit jemanden auszurauben."
	"100",
	"Weapon",
	"2"
),
(
	"Taser",
	"Dieser Taser schützt dich davor ausgeraubt zu werden.",
	"100",
	"Weapon",
	"2"
),
(
	"Random Money Drop - Everyone",
	"Jeder kriegt Geld!",
	"100",
	"Money Drop",
	"5"
);
	
DROP USER IF EXISTS 'bot_db_admin'@'%';
FLUSH PRIVILEGES;

CREATE USER 'bot_db_admin'@'%' IDENTIFIED BY 'adminSimplistic';
FLUSH PRIVILEGES;

GRANT ALL PRIVILEGES ON bot_db.* TO 'bot_db_admin'@'%' IDENTIFIED BY 'adminSimplistic';
FLUSH PRIVILEGES;

DROP USER IF EXISTS 'ita19b'@'%';
FLUSH PRIVILEGES;

CREATE USER 'ita19b'@'%' IDENTIFIED BY 'admin';
FLUSH PRIVILEGES;

GRANT SELECT ON bot_db.* TO 'ita19b'@'%' IDENTIFIED BY 'admin';
FLUSH PRIVILEGES;