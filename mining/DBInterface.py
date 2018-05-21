from twisted.internet import reactor, defer
import time
from datetime import datetime
import Queue

from stratum import settings

import stratum.logger
log = stratum.logger.get_logger('DBInterface')

class DBInterface():
    def __init__(self):
	self.dbi = self.connectDB()

    def init_main(self):
	self.dbi.check_tables()
 
	self.q = Queue.Queue()
        self.queueclock = None

	self.usercache = {}
        self.clearusercache()

	self.nextStatsUpdate = 0

        self.scheduleImport()

    def set_bitcoinrpc(self,bitcoinrpc):
	self.bitcoinrpc=bitcoinrpc

    def connectDB(self):
	# Choose our database driver and put it in self.dbi
	if settings.DATABASE_DRIVER == "sqlite":
		log.debug('DB_Sqlite INIT')
		import DB_Sqlite
		return DB_Sqlite.DB_Sqlite()
	elif settings.DATABASE_DRIVER == "mysql":
		log.debug('DB_Mysql INIT')
		import DB_Mysql
		return DB_Mysql.DB_Mysql()
	elif settings.DATABASE_DRIVER == "postgresql":
		log.debug('DB_Postgresql INIT')
		import DB_Postgresql
		return DB_Postgresql.DB_Postgresql()
	elif settings.DATABASE_DRIVER == "none":
		log.debug('DB_None INIT')
		import DB_None
		return DB_None.DB_None()
	else:
		log.error('Invalid DATABASE_DRIVER -- using NONE')
		log.debug('DB_None INIT')
		import DB_None
		return DB_None.DB_None()

    def clearusercache(self):
	self.usercache = {}
        self.usercacheclock = reactor.callLater( settings.DB_USERCACHE_TIME , self.clearusercache)

    def scheduleImport(self):
	# This schedule's the Import
	use_thread = True
	if settings.DATABASE_DRIVER == "sqlite":
	    use_thread = False
	
	if use_thread:
            self.queueclock = reactor.callLater( settings.DB_LOADER_CHECKTIME , self.run_import_thread)
	else:
            self.queueclock = reactor.callLater( settings.DB_LOADER_CHECKTIME , self.run_import)
    
    def run_import_thread(self):
	if self.q.qsize() >= settings.DB_LOADER_REC_MIN:	# Don't incur thread overhead if we're not going to run
		reactor.callInThread(self.import_thread)
	self.scheduleImport()

    def run_import(self):
	self.do_import(self.dbi,False)
	if settings.DATABASE_EXTEND and time.time() > self.nextStatsUpdate :
	    self.nextStatsUpdate = time.time() + settings.DB_STATS_AVG_TIME
	    self.dbi.updateStats(settings.DB_STATS_AVG_TIME)
            d = self.bitcoinrpc.getinfo()
            d.addCallback(self._update_pool_info)
	    if settings.ARCHIVE_SHARES :
		self.archive_shares(self.dbi)
	self.scheduleImport()

    def import_thread(self):
	# Here we are in the thread.
	dbi = self.connectDB()	
	self.do_import(dbi,False)
	if settings.DATABASE_EXTEND and time.time() > self.nextStatsUpdate :
	    self.nextStatsUpdate = time.time() + settings.DB_STATS_AVG_TIME
	    dbi.updateStats(settings.DB_STATS_AVG_TIME)
            d = self.bitcoinrpc.getinfo()
            d.addCallback(self._update_pool_info)
	    if settings.ARCHIVE_SHARES :
	    	self.archive_shares(dbi)
	dbi.close()

    def _update_pool_info(self,data):
	self.dbi.update_pool_info({ 'blocks' : data['blocks'], 'balance' : data['balance'], 
		'connections' : data['connections'], 'difficulty' : data['difficulty'] })

    def do_import(self,dbi,force):
	# Only run if we have data
	while force == True or self.q.qsize() >= settings.DB_LOADER_REC_MIN:
	    force = False
	    # Put together the data we want to import
	    sqldata = []
	    datacnt = 0
	    while self.q.empty() == False and datacnt < settings.DB_LOADER_REC_MAX :
		datacnt += 1
		data = self.q.get()
		sqldata.append(data)
		self.q.task_done()
	    # try to do the import, if we fail, log the error and put the data back in the queue
	    try:
		log.info("Inserting %s Share Records",datacnt)
		dbi.import_shares(sqldata)
	    except Exception as e:
		log.error("Insert Share Records Failed: %s", e.args[0])
		for k,v in enumerate(sqldata):
		    self.q.put(v)
		break		# Allows us to sleep a little

    def archive_shares(self,dbi):
	found_time = dbi.archive_check()
	if found_time == 0:
	    return False
	log.info("Archiving shares newer than timestamp %f " % found_time)
	dbi.archive_found(found_time)
	if settings.ARCHIVE_MODE == 'db':
	    dbi.archive_to_db(found_time)
	    dbi.archive_cleanup(found_time)
	elif settings.ARCHIVE_MODE == 'file':
	    shares = dbi.archive_get_shares(found_time)

	    filename = settings.ARCHIVE_FILE
	    if settings.ARCHIVE_FILE_APPEND_TIME :
		filename = filename + "-" + datetime.fromtimestamp(found_time).strftime("%Y-%m-%d-%H-%M-%S")
	    filename = filename + ".csv"

	    if settings.ARCHIVE_FILE_COMPRESS == 'gzip' :
		import gzip
		filename = filename + ".gz"
		filehandle = gzip.open(filename, 'a')	
	    elif settings.ARCHIVE_FILE_COMPRESS == 'bzip2' and settings.ARCHIVE_FILE_APPEND_TIME :
		import bz2
		filename = filename + ".bz2"
		filehandle = bz2.BZFile(filename, mode='wb', buffering=4096 )
	    else:
		filehandle = open(filename, "a")

	    while True:	
		row = shares.fetchone()
		if row == None:
		    break
		str1 = '","'.join([str(x) for x in row])
		filehandle.write('"%s"\n' % str1)
	    filehandle.close()

	    clean = False
	    while not clean:
		try:
		    dbi.archive_cleanup(found_time)
		    clean = True
		except Exception as e:
		    clean = False
		    log.error("Archive Cleanup Failed... will retry to cleanup in 30 seconds")
		    sleep(30)
		
	return True

    def queue_share(self,data):
	self.q.put( data )

    def found_block(self,data):
	try:
	    log.info("Updating Found Block Share Record")
	    self.do_import(self.dbi,True)	# We can't Update if the record is not there.
	    self.dbi.found_block(data)
	except Exception as e:
	    log.error("Update Found Block Share Record Failed: %s", e.args[0])

    def check_password(self,username,password):
	if username == "":
	    log.info("Rejected worker for blank username")
	    return False
	wid = username+":-:"+password
	if wid in self.usercache :
	    return True
	elif self.dbi.check_password(username,password) :
	    self.usercache[wid] = 1
	    return True
	elif settings.USERS_AUTOADD == True :
	    self.insert_user(username,password)
	    self.usercache[wid] = 1
	    return True
	return False

    def insert_user(self,username,password):	
	return self.dbi.insert_user(username,password)

    def delete_user(self,username):
	self.usercache = {}
	return self.dbi.delete_user(username)
	
    def update_user(self,username,password):
	self.usercache = {}
	return self.dbi.update_user(username,password)

    def update_worker_diff(self,username,diff):
	return self.dbi.update_worker_diff(username,diff)

    def get_pool_stats(self):
	return self.dbi.get_pool_stats()
    
    def get_workers_stats(self):
	return self.dbi.get_workers_stats()

    def clear_worker_diff(self):
	return self.dbi.clear_worker_diff()

