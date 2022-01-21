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