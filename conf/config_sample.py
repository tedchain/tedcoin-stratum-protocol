'''
This is example configuration for Stratum server.
Please rename it to config.py and fill correct values.
'''

# ******************** GENERAL SETTINGS ***************

# Enable some verbose debug (logging requests and responses).
DEBUG = False

# Destination for application logs, files rotated once per day.
LOGDIR = 'log/'

# Main application log file.
LOGFILE = None#'stratum.log'

# Possible values: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOGLEVEL = 'INFO'

# How many threads use for synchronous methods (services).
# 30 is enough for small installation, for real usage
# it should be slightly more, say 100-300.
THREAD_POOL_SIZE = 10

ENABLE_EXAMPLE_SERVICE = True

# ******************** TRANSPORTS *********************

# Hostname or external IP to expose
HOSTNAME = 'localhost'

# Port used for Socket transport. Use 'None' for disabling the transport.
LISTEN_SOCKET_TRANSPORT = 3333

# Port used for HTTP Poll transport. Use 'None' for disabling the transport
LISTEN_HTTP_TRANSPORT = None

# Port used for HTTPS Poll transport
LISTEN_HTTPS_TRANSPORT = None

# Port used for WebSocket transport, 'None' for disabling WS
LISTEN_WS_TRANSPORT = None

# Port used for secure WebSocket, 'None' for disabling WSS
LISTEN_WSS_TRANSPORT = None

# Hostname and credentials for one trusted Tedcoin node.
# Stratum uses both P2P port (which is 7777 already) and RPC port
TEDCOIN_TRUSTED_HOST = 'localhost'
TEDCOIN_TRUSTED_PORT = 8344
TEDCOIN_TRUSTED_USER = 'user'
TEDCOIN_TRUSTED_PASSWORD = 'password'

# Use "echo -n '<yourpassword>' | sha256sum | cut -f1 -d' ' "
# for calculating SHA256 of your preferred password
ADMIN_PASSWORD_SHA256 = None
#ADMIN_PASSWORD_SHA256 = '9e6c0c1db1e0dfb3fa5159deb4ecd9715b3c8cd6b06bd4a3ad77e9a8c5694219' # SHA256 of the password

IRC_NICK = None


DATABASE_DRIVER = 'mysql'
DATABASE_EXTEND = False         # False = pushpool db layout, True = pushpool + extra columns
DB_MYSQL_HOST = 'localhost'
DB_MYSQL_DBNAME = 'pooldb'
DB_MYSQL_USER = 'pooldb'
DB_MYSQL_PASS = '**empty**'


# Pool related settings
INSTANCE_ID = 31
CENTRAL_WALLET = '4WpFe4iTc8zC3UHAzdQX6w9BcRuXFxvPqm' # local Tedcoin address where money goes
PREVHASH_REFRESH_INTERVAL = 5 # in sec
MERKLE_REFRESH_INTERVAL = 60 # How often check memorypool
COINBASE_EXTRAS = ''

# ******************** Pool Difficulty Settings *********************
#  Again, Don't change unless you know what this is for.

# Pool Target (Base Difficulty)
POOL_TARGET = 32                # Pool-wide difficulty target int >= 1

# Variable Difficulty Enable
VARIABLE_DIFF = False           # Master variable difficulty enable

# Variable diff tuning variables
VDIFF_TARGET = 15               # Target time per share (i.e. try to get 1 share per this many seconds)
VDIFF_RETARGET = 120            # Check to see if we should retarget this often
VDIFF_VARIANCE_PERCENT = 50     # Allow average time to very this % from target without retarget

# ******************** Adv. DB Settings *********************
#  Don't change these unless you know what you are doing

DB_LOADER_CHECKTIME = 15        # How often we check to see if we should run the loader
DB_LOADER_REC_MIN = 10          # Min Records before the bulk loader fires
DB_LOADER_REC_MAX = 20          # Max Records the bulk loader will commit at a time

DB_STATS_AVG_TIME = 30          # When using the DATABASE_EXTEND option, average speed over X sec
                                #       Note: this is also how often it updates
DB_USERCACHE_TIME = 600         # How long the usercache is good for before we refresh

USERS_AUTOADD = False
