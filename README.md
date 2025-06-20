# Frappe Installation
# Pre-requisites 
Python 3.10+ (v14)
Node.js 16
Redis 6                                       (caching and realtime updates)
MariaDB 10.6.6+ / Postgres v12 to v14         (Database backend)
yarn 1.12+                                    (js dependency manager)
pip 20+                                       (py dependency manager)
wkhtmltopdf (version 0.12.5 with patched qt)  (for pdf generation)
cron                                          (bench's scheduled jobs: automated certificate renewal, scheduled backups)
NGINX                                         (proxying multitenant sites in production)


# Install Yarn
- sudo apt install git python-dev python-pip redis-server

# Install MariaDB
- sudo apt install software-properties-common

# If you are on Ubuntu version older than 20.04, run this before installing MariaDB:
- sudo apt-key adv --recv-keys --keyserver hkp://keyserver.ubuntu.com:80 0xF1656F24C74CD1D8
- sudo add-apt-repository 'deb [arch=amd64,i386,ppc64el] http://ftp.ubuntu-tw.org/mirror/mariadb/repo/10.3/ubuntu xenial main'

# If you are on version Ubuntu 20.04, then MariaDB is available in default repo and you can directly run the below commands to install it:
- sudo apt-get update
- sudo apt-get install mariadb-server

# During this installation you'll be prompted to set the MySQL root password. If you are not prompted, you'll have to initialize the MySQL server setup yourself. You can do that by running the command:
- mysql_secure_installation

# It is really important that you remember this password, since it'll be useful later on. You'll also need the MySQL database development files.
- apt-get install mariadb-client-10.3

# Now, edit the MariaDB configuration file.
- nano /etc/mysql/my.cnf

# And add this configuration
- [mysqld]
- character-set-client-handshake = FALSE
- character-set-server = utf8mb4
- collation-server = utf8mb4_unicode_ci

- [mysql]
- default-character-set = utf8mb4

# Now, just restart the mysql service and you are good to go.
- service mysql restart

# Install Node
- curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.11/install.sh | bash

<!-- After nvm is installed, you may have to close your terminal and open another one. Now run the following command to install node. -->
- nvm install 14
<!-- Verify the installation, by running: -->

- node -v
<!-- output -->
<!-- - v14.17.2 -->

# Finally, install yarn using npm
- apt-get install xvfb libfontconfig wkhtmltopdf

# Install wkhtmltopdf
- apt-get install xvfb libfontconfig wkhtmltopdf

# Install bench via pip3
- pip3 install frappe-bench

<!-- Confirm the bench installation by checking version -->
- bench --version

<!-- output
5.2.1 -->

<!-- Create your first bench folder. -->
- cd ~
- bench init frappe-bench

<!-- After the frappe-bench folder is created, change your directory to it and run this command -->
- bench start
