# ADaPT - Development Environment

Instructions on how to create a local development environtment using [Docker](https://docs.docker.com/get-started/overview/), [MySQL 8.0](https://dev.mysql.com/doc/refman/8.0/en/), [OLTPBench](https://github.com/oltpbenchmark/oltpbench) and [Python 3](https://hub.docker.com/_/python).

Examples using a local desktop, macOS Catalina 10.15.7.


## Pre-requistes

### Docker and Docker Compose
```
docker --version
docker-compose --version
```
Example:
```
$ docker --version
Docker version 20.10.5, build 55c4c88
$ docker-compose --version
docker-compose version 1.28.5, build c4eb3a1f
```
If not installed, [Docker Desktop](https://www.docker.com/products/docker-desktop) is recommended.

### Git
```
$ git --version
git version 2.31.1
```
If not installed, get instructions from [git-scm.com](https://git-scm.com/downloads).


### User-defined Docker Network
Example to create a user-defined network called `dev-net`.
```
$ docker network create dev-net
286ae1f1dd52d88307044bcc4db93b29a35daf92f21798d59b58209193b4a955

$ docker network ls
NETWORK ID     NAME      DRIVER    SCOPE
286ae1f1dd52   dev-net   bridge    local
```
Check network:
```
$ docker network inspect dev-net
[
    {
        "Name": "dev-net",
        "Id": "286ae1f1dd52d88307044bcc4db93b29a35daf92f21798d59b58209193b4a955",
        "Created": "2021-04-01T20:24:39.4410999Z",
        "Scope": "local",
        "Driver": "bridge",
        "EnableIPv6": false,
        "IPAM": {
            "Driver": "default",
            "Options": {},
            "Config": [
                {
                    "Subnet": "172.21.0.0/16",
                    "Gateway": "172.21.0.1"
                }
            ]
        },
        "Internal": false,
        "Attachable": false,
        "Ingress": false,
        "ConfigFrom": {
            "Network": ""
        },
        "ConfigOnly": false,
        "Containers": {},
        "Options": {},
        "Labels": {}
    }
]
```


## MySQL on Docker

### Get latest MySQL image available at Docker Hub 
Example using the [Docker community image](https://hub.docker.com/_/mysql/). Not [MySQL Server image](https://hub.docker.com/r/mysql/mysql-server) by Oracle team.
```
docker pull mysql:latest
docker images
```
Example:
```
$ docker pull mysql:latest
latest: Pulling from library/mysql
6f28985ad184: Already exists 
e7cd18945cf6: Pull complete 
ee91068b9313: Pull complete 
b4efa1a4f93b: Pull complete 
f220edfa5893: Pull complete 
74a27d3460f8: Pull complete 
2e11e23b7542: Pull complete 
fbce32c99761: Pull complete 
08545fb3966f: Pull complete 
5b9c076841dc: Pull complete 
ef8b369352ae: Pull complete 
ebd210f0917d: Pull complete 
Digest: sha256:5d1d733f32c28d47061e9d5c2b1fb49b4628c4432901632a70019ec950eda491
Status: Downloaded newer image for mysql:latest
docker.io/library/mysql:latest

$ docker images
REPOSITORY                   TAG            IMAGE ID       CREATED         SIZE
mysql                        latest         26d0ac143221   6 days ago      546MB
```

### Create a local MySQL configuration file
- Create a local directory for the additional MySQL configuration files
- Create a valid MySQL configuration file in the new directory

Example for `~/mysql-dev/conf.d/my-bench.cnf`:
```
mkdir -p ~/mysql-dev/conf.d
cd ~/mysql-dev/conf.d
echo "# MySQL config to be placed in /etc/mysql/conf.d" > my-bench.cnf
echo "[mysqld]" >> my-bench.cnf
echo "autocommit=0    # Default is 1 (ON)" >> my-bench.cnf
```
Check:
```
$ cat ~/mysql-dev/conf.d/my-bench.cnf
# MySQL config to be placed in /etc/mysql/conf.d
[mysqld]
autocommit=0    # Default is 1 (ON)
```

### Create an empty data directory
Create a local empty directory for the MySQL data files. MySQL will store data in this directory, then the data files can be persisted accessed outside the container.
```
mkdir -p ${HOME}/mysql-dev/data
```

### Create and run a container with MySQL named as `mysql8` 
The MySQL container will be using the Docker network `dev-net`, the local custom MySQL configuration file in `mysql-dev/conf.d` and will store the data outside the container in the directory `mysql-dev/data`.
```
docker run --name=mysql8 --network=dev-net \
  -p 3306:3306 -p 33060:33060 \
  -v "${HOME}/mysql-dev/conf.d":/etc/mysql/conf.d \
  -v "${HOME}/mysql-dev/data":/var/lib/mysql \
  -e MYSQL_ROOT_PASSWORD=Root123! \
  -d mysql:latest
```
Note the `-p` (port) parameters aren't mandatory, but they allow access from the host desktop to the database. For example, to use MySQL Workbench.


Check if the constainer `mysql8` is running:
```
docker ps
docker port mysql8
docker logs mysql8
```
Example:
```
$ docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED          STATUS          PORTS                                              NAMES
24320d6c1970   mysql:latest   "docker-entrypoint.s…"   51 seconds ago   Up 50 seconds   0.0.0.0:3306->3306/tcp, 0.0.0.0:33060->33060/tcp   mysql8

$ docker port mysql8
3306/tcp -> 0.0.0.0:3306
33060/tcp -> 0.0.0.0:33060

$ docker logs mysql8
...
2021-04-02T20:27:09.973693Z 0 [System] [MY-010931] [Server] /usr/sbin/mysqld: ready for connections. Version: '8.0.23'  socket: '/var/run/mysqld/mysqld.sock'  port: 3306  MySQL Community Server - GPL.
```

### Connect to MySQL Server from another container
Start another temporary container and use `mysql` client to connect to the MySQL Server running in `mysql8`
```
docker run -it --network=dev-net --rm mysql \
  mysql -hmysql8 -uroot -p'Root123!'
```

Example:
```
$ docker run -it --network=dev-net --rm mysql \
>   mysql -hmysql8 -uroot -p'Root123!'
mysql: [Warning] Using a password on the command line interface can be insecure.
Welcome to the MySQL monitor.  Commands end with ; or \g.
Your MySQL connection id is 1
Server version: 8.0.23 MySQL Community Server - GPL

Copyright (c) 2000, 2021, Oracle and/or its affiliates.

Oracle is a registered trademark of Oracle Corporation and/or its
affiliates. Other names may be trademarks of their respective
owners.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

mysql> SHOW GLOBAL VARIABLES LIKE 'autocommit';
+---------------+-------+
| Variable_name | Value |
+---------------+-------+
| autocommit    | OFF   |
+---------------+-------+
1 row in set (0.00 sec)

mysql> quit
Bye
```

Note the autocommit should be OFF (0) because we used the custom config to override the MySQL default value ON (1).

Additionally, MySQL must create the data files in the local data directory:
```
$ ls /Users/alastori/mysql-dev/data
#ib_16384_0.dblwr	client-cert.pem		performance_schema
#ib_16384_1.dblwr	client-key.pem		private_key.pem
#innodb_temp		ib_buffer_pool		public_key.pem
auto.cnf		ib_logfile0		server-cert.pem
binlog.000001		ib_logfile1		server-key.pem
binlog.000002		ibdata1			sys
binlog.index		ibtmp1			undo_001
ca-key.pem		mysql			undo_002
ca.pem			mysql.ibd
```


### Useful MySQL procedures

#### Connect to MySQL Server using the IP address
You can optionally use the IP address to connect to MySQL instead of the hostname `mysql8` (same as container name). 

1. Discover the IP address with:
```
docker inspect mysql8 | grep IPAddress
```
Example:
```
$ docker inspect mysql8 | grep IPAddress
            "SecondaryIPAddresses": null,
            "IPAddress": "",
                    "IPAddress": "172.21.0.2",
```

2. Connect using the IP address with:
```
$ docker run -it --network=dev-net --rm mysql \
  mysql -h172.21.0.2 -uroot -p'Root123!'
```

#### Connect to MySQL Server direct from the host
You can connect from clients in the host (ex. MySQL Workbench installed in the desktop) to the MySQL Server running in the container. 
With the Docker option `-p`, the ports `3306` and `33060` are mapped to the host. 
In Workbench or other client, just use `localhost` and the mapped port `3306` (MySQL classic protocol) or `33060` (MySQL Xprotocol).

#### Create a MySQL user with permissions to connect remotely
1. Connect to MySQL and run the following SQL commands:
```
mysql> CREATE USER 'remote'@'%' IDENTIFIED BY 'Remote123!';
Query OK, 0 rows affected (0.04 sec)

mysql> GRANT ALL PRIVILEGES ON *.* TO 'remote'@'%';
Query OK, 0 rows affected (0.03 sec)
```

2. Check the MySQL users that can connect remotely:
```
mysql> SELECT user, host FROM mysql.user WHERE host = '%';
+--------+------+
| user   | host |
+--------+------+
| remote | %    |
| root   | %    |
+--------+------+
2 rows in set (0.00 sec)
```


## Useful Docker commands

- Stop the container 
```
docker stop mysql8
docker ps
```

- List all containers, including stopped
```
docker ps -a
```

- Start container
```
docker start mysql8
```

- Container terminal
```
docker exec -it mysql8 /bin/bash
```

- Remove the container
```
docker rm mysql8
docker ps -a
```

- Remove the image
```
docker images
docker rmi mysql
```

- Remove unused networks
```
docker network prune
```

- Remove everything unused
```
docker system prune -a
```


## OLTPBench
[OLTPBench](https://github.com/oltpbenchmark/oltpbench) is a database benchmark suite that can generate multi-threaded synthetic workloads. 

### Clone OLTPBench repository 
```
git clone https://github.com/oltpbenchmark/oltpbench.git
```
Example:
```
$ git clone https://github.com/oltpbenchmark/oltpbench.git
Cloning into 'oltpbench'...
remote: Enumerating objects: 132, done.
remote: Counting objects: 100% (132/132), done.
remote: Compressing objects: 100% (85/85), done.
remote: Total 15070 (delta 43), reused 83 (delta 32), pack-reused 14938
Receiving objects: 100% (15070/15070), 119.51 MiB | 38.95 MiB/s, done.
Resolving deltas: 100% (9370/9370), done.
```

### OLTPBench Docker image bug fix 
On March 31, 2021 the [most recent OLTPBench version](https://github.com/oltpbenchmark/oltpbench/commit/6e8c04f3a2e672fb8ffe54a1acc6bcb9a59acf38) has a [known issue](https://github.com/oltpbenchmark/oltpbench/issues/344) causing `ExceptionInInitializerError` in `com.oltpbenchmark.DBWorkload.main(DBWorkload.java:87)` when running from Docker.
To workarond the issue, downgrade the OpenJDK base image from version 16 to version 15. 

Edit the `oltpbench/Dockerfile`:
```
FROM openjdk:15-slim-buster
```


### Build OLTPBench Docker image with tag `oltpbench`
```
cd oltpbench
docker build -t oltpbench .
docker images | grep oltpbench
```
Example:
```
$ cd oltpbench
$ docker build -t oltpbench .
[+] Building 66.1s (10/10) FINISHED                                             
 => [internal] load build definition from Dockerfile                       0.1s
 => => transferring dockerfile: 233B                                       0.0s
 => [internal] load .dockerignore                                          0.0s
 => => transferring context: 2B                                            0.0s
 => [internal] load metadata for docker.io/library/openjdk:15-slim-buster  2.3s
 => [auth] library/openjdk:pull token for registry-1.docker.io             0.0s
 => CACHED [1/4] FROM docker.io/library/openjdk:15-slim-buster@sha256:7ba  0.0s
 => [internal] load build context                                         11.6s
 => => transferring context: 191.03MB                                     11.5s
 => [2/4] COPY . /usr/src/oltpbench                                        0.6s
 => [3/4] WORKDIR /usr/src/oltpbench                                       0.0s
 => [4/4] RUN .deploy/install.sh                                          50.0s
 => exporting to image                                                     1.4s 
 => => exporting layers                                                    1.4s 
 => => writing image sha256:dadf8000ee55bbda73affb1bea9e769638b8419b0a97b  0.0s 
 => => naming to docker.io/library/oltpbench                               0.0s 

$ docker images | grep oltpbench
oltpbench    latest    dadf8000ee55   1 minute ago   737MB 
```

### Create MySQL user and database to run OLTPBench
Connect to MySQL and run the following SQL commands:
```
CREATE USER IF NOT EXISTS 'oltpbench'@'%' IDENTIFIED BY 'Oltpbench123!';
CREATE DATABASE tpcc;
GRANT ALL PRIVILEGES ON tpcc.* TO 'oltpbench'@'%';
```

### Create a local working directory for OLTPBench files
In this example, the OLTPBench configuration files will be placed in `~/oltpbench-dev/config` and the result files `~/oltpbench-dev/result`.
```
mkdir -p ~/oltpbench-dev/config
mkdir -p ~/oltpbench-dev/results
```

### Create an OLTPBench config XML file
Crete the OLTPBench configuration file in the working directory. 
Make sure you use the correct MySQL hostname in `DBUrl`, `username` and `password`.
Example for `~/oltpbench-dev/config/mysql_tpcc_config.xml`:
```
<?xml version="1.0"?>
<!-- config/mysql_tpcc_config.xml -->
<parameters>
	<!-- Connection details -->
	<dbtype>mysql</dbtype>
	<driver>com.mysql.jdbc.Driver</driver>
	<DBUrl>jdbc:mysql://mysql8:3306/tpcc?useSSL=false</DBUrl>
	<username>oltpbench</username>
	<password>Oltpbench123!</password>
	<isolation>TRANSACTION_SERIALIZABLE</isolation>
	<uploadCode></uploadCode>
	<uploadUrl></uploadUrl>
	
	<!-- Scale factor is the number of warehouses in TPCC -->
	<scalefactor>2</scalefactor>
	
	<!-- The workload -->
	<terminals>2</terminals>
	<works>
		<work>
			<time>60</time>
			<rate>10000</rate>
			<weights>45,43,4,4,4</weights>
		</work>
	</works>

	<!-- TPCC specific -->  
	<transactiontypes>
		<transactiontype>
			<name>NewOrder</name>
		</transactiontype>
		<transactiontype>
			<name>Payment</name>
		</transactiontype>
		<transactiontype>
			<name>OrderStatus</name>
		</transactiontype>
		<transactiontype>
			<name>Delivery</name>
		</transactiontype>
		<transactiontype>
			<name>StockLevel</name>
		</transactiontype>
	</transactiontypes>	
</parameters>
```

Note `useSSL=false` is added to the `DBUrl` to avoid warning messages like:
```
WARN: Establishing SSL connection without server's identity verification is not recommended. According to MySQL 5.5.45+, 5.6.26+ and 5.7.6+ requirements SSL connection must be established by default if explicit option isn't set. For compliance with existing applications not using SSL the verifyServerCertificate property is set to 'false'. You need either to explicitly disable SSL by setting useSSL=false, or set useSSL=true and provide truststore for server certificate verification.
```

### Run OLTPBench with MySQL

#### Option 1 - run and remove the container after finished, saving results in `/oltpbench-dev/results`:
```
cd ~/oltpbench-dev
cat config/mysql_tpcc_config.xml | \
  docker run -i --rm --name=oltpbench --network=dev-net \
    -v ${HOME}/oltpbench-dev/results:/usr/src/oltpbench/results \
    oltpbench -b tpcc --create=true --load=true --execute=true -s 5 -o result
```

Example:
```
$ cat config/mysql_tpcc_config.xml |   docker run -i --rm --name=oltpbench --network=dev-net     -v ${HOME}/oltpbench-dev/results:/usr/src/oltpbench/results     oltpbench -b tpcc --create=true --load=true --execute=true -s 5 -o result
02:09:59,192 (DBWorkload.java:270) INFO  - ======================================================================

Benchmark:     TPCC {com.oltpbenchmark.benchmarks.tpcc.TPCCBenchmark}
Configuration: config/docker_workload.xml
Type:          MYSQL
Driver:        com.mysql.jdbc.Driver
URL:           jdbc:mysql://mysql8:3306/tpcc?useSSL=false
Isolation:     TRANSACTION_SERIALIZABLE
Scale Factor:  2.0

02:09:59,199 (DBWorkload.java:271) INFO  - ======================================================================
02:09:59,243 (DBWorkload.java:533) INFO  - Creating new TPCC database...
02:10:01,361 (DBWorkload.java:535) INFO  - Finished!
02:10:01,361 (DBWorkload.java:536) INFO  - ======================================================================
02:10:01,364 (DBWorkload.java:559) INFO  - Loading data into TPCC database with 2 threads...
02:24:40,058 (DBWorkload.java:563) INFO  - Finished!
02:24:40,060 (DBWorkload.java:564) INFO  - ======================================================================
02:24:40,072 (DBWorkload.java:849) INFO  - Creating 2 virtual terminals...
02:24:40,131 (DBWorkload.java:854) INFO  - Launching the TPCC Benchmark with 1 Phase...
02:24:40,148 (ThreadBench.java:341) INFO  - PHASE START :: [Workload=TPCC] [Serial=false] [Time=60] [WarmupTime=0] [Rate=10000] [Arrival=REGULAR] [Ratios=[45.0, 43.0, 4.0, 4.0, 4.0]] [ActiveWorkers=2]
02:24:40,150 (ThreadBench.java:492) INFO  - MEASURE :: Warmup complete, starting measurements.
02:25:40,088 (ThreadBench.java:447) INFO  - TERMINATE :: Waiting for all terminals to finish ..
02:25:40,148 (ThreadBench.java:508) INFO  - Attempting to stop worker threads and collect measurements
02:25:40,152 (ThreadBench.java:247) INFO  - Starting WatchDogThread
02:25:40,160 (DBWorkload.java:860) INFO  - ======================================================================
02:25:40,167 (DBWorkload.java:861) INFO  - Rate limited reqs/s: Results(nanoSeconds=60000641400, measuredRequests=1235) = 20.583113299852158 requests/sec
02:25:40,191 (DBWorkload.java:667) INFO  - Upload Results URL: com.oltpbenchmark.util.ResultUploader@645aa696
02:25:40,206 (DBWorkload.java:700) INFO  - Output Raw data into file: results/result.1.csv
02:25:42,348 (DBWorkload.java:719) INFO  - Output summary data into file: results/result.1.summary
02:25:42,407 (DBWorkload.java:726) INFO  - Output DBMS parameters into file: results/result.1.params
02:25:42,454 (DBWorkload.java:733) INFO  - Output DBMS metrics into file: results/result.1.metrics
02:25:42,483 (DBWorkload.java:740) INFO  - Output experiment config into file: results/result.1.expconfig
02:25:42,837 (DBWorkload.java:757) INFO  - Output throughput samples into file: results/result.1.res
02:25:42,839 (DBWorkload.java:760) INFO  - Grouped into Buckets of 5 seconds
```

#### Option 2 - debug OLTPBench container:
```
docker run --rm --name=oltpbench-debug --network=dev-net \
  -it --entrypoint /bin/bash \
  -v ${HOME}/oltpbench-dev/config:/usr/src/oltpbench/my-config
  -v ${HOME}/oltpbench-dev/results:/usr/src/oltpbench/results

PATH="/usr/local/bin/apache-ant-1.9.15/bin:$PATH"

./oltpbenchmark -c my-config/mysql_tpcc_config.xml -b tpcc --create=true --load=true --execute=true -s 5 -o result-debug
```
