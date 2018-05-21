Stratum-mining
==============

Demo implementation of Tedcoin mining pool using Stratum mining protocol.

For Stratum mining protocol specification, please visit http://mining.bitcoin.cz/stratum-mining.

Installation Instructions
=========================

Step 0: Install tedcoind
It MUST be a recent version of tedcoind
Set it up and start it!
Downloading the blockchain can take some time!

Step 1: Install the stratum core
	git pull https://github.com/slush0/stratum.git
	sudo easy_install stratum
	(or if using alternate python: sudo /usr/local/bin/easy_install stratum)

Step 2: Pull a copy of the miner
	git pull https://github.com/CryptoManiac/stratum-mining.git

Step 3: Configure the Miner
	cp conf/config_sample.py conf/config.py
	make your changes to conf/config.py 
	Make sure you set the values in BASIC SETTINGS! These are how to connect to tedcoind 
	and where your money goes! Please read comments carefully, this may be helpful.
	
Step 4: Run the pool
	twistd -ny launcher.tac -l -
	OR - using alternate python
	/usr/local/bin/twistd -ny launcher.tac -l -

You can now set the URL on your stratum proxy (or miner that supports stratum) to:
http://YOURHOSTNAME:3333

Tedcoind blocknotify Setup
=========================
Although scary (for me), this is actually pretty easy.

Step 1: Set Admin Password
	Ensure that you have set the ADMIN_PASSWORD_SHA256 parameter in conf/config.py
	To make life easy you can run the generateAdminHash script to make the hash
		./scripts/generateAdminHash.sh <password>

Step 2: Test It
	Restart the pool if it's already running
	run ./scripts/blocknotify.sh --password <password> --host localhost --port 3333
	Ensure everything is ok.

Step 3: Run bitcoind with blocknotify
	Stop bitcoind if it's already running
	bitcoind stop
	Wait till it ends
	tedcoind -blocknotify="/absolute/path/to/scripts/blocknotify.sh --password <password> --host localhost --port 3333"

Step 4: Adjust pool polling
	Now you should be able to watch the pools debug messages for awhile and see the blocknotify come in
	once you are sure it's working edit conf/config.py and set
		PREVHASH_REFRESH_INTERVAL = to the same value as MERKLE_REFRESH_INTERVAL
	restart the pool


Problems????
=========================

Is your firewall off?
Is tedcoind running?

TODO: are there other problems?