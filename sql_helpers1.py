from app import mysql, session
from blockchain import Block, Blockchain

class InvalidTransactionException(Exception): pass
class InsufficientFundsException(Exception): pass

class Table():
    '''
    specify the table name and columns
    EXAMPLE table: blockchain
    number    hash    previous   data    nonce
    -data-   -data-    -data-   -data-  -data-
    EXAMPLE initialization: ...Table("blockchain", "number", "hash", "previous", "data", "nonce")
    '''
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columnsList = args
        self.columns = "(%s)" %",".join(args)
        
        if isnewtable(table_name):
            cur = mysql.connection.cursor()
            cur.execute("CREATE TABLE %s%s" %(self.table, self.columns))
            cur.close()

    #get all the values from the table
    def getall(self):
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s" %self.table)
        data = cur.fetchall() 
        cur.close()
        return data

    #get one value from the table based on a column's data
    #EXAMPLE using blockchain: ...getone("hash","00003f73gh93...")
    def getone(self, search, value):
        data = {}; cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" %(self.table, search, value))
        if result > 0: data = cur.fetchone()
        cur.close() 
        return data

    #delete a value from the table based on column's data
    def deleteone(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("DELETE from %s where %s = \"%s\"" %(self.table, search, value))
        mysql.connection.commit(); cur.close()

    #delete all values from the table.
    # def deleteall(self):
    #     self.drop() #remove table and recreate
    #     self.__init__(self.table, *self.columnsList)

    def deleteall(self):
        self.drop()  # Remove table
        self.create_table()  # Recreate table
        blockchain = Blockchain()  # Reinitialize blockchain with genesis block
        self.sync_blockchain(blockchain)  # Sync the genesis block to the table

    #remove table from mysql
    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE %s" %self.table)
        cur.close()

    def create_table(self):
        cur = mysql.connection.cursor()
        cur.execute("CREATE TABLE %s%s" % (self.table, self.columns))
        mysql.connection.commit()
        cur.close()

    #insert values into the table
    def insert(self, *args):
        data = ""
        for arg in args: #convert data into string mysql format
            data += "\"%s\"," %(arg)
        print(data)

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO %s%s VALUES(%s)" %(self.table, self.columns, data[:len(data)-1]))
        mysql.connection.commit()
        cur.close()

#execute mysql code from python
def sql_raw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()

#check if table already exists
def isnewtable(tableName):
    cur = mysql.connection.cursor()
    
    try:
        result = cur.execute("SELECT * from %s" %tableName)
        cur.close()
    except:
        return True
    else: 
        return False
    
def isnewuser(username):
    users = Table("users", "name", "username", "email", "password")
    data = users.getall()
    usernames = [user.get('username') for user in data]
    
    return False if username in usernames else True

def send_money(sender, recipient, amount):
    try: amount = float(amount)
    except ValueError:
        raise InvalidTransactionException("Invalid Transaction")
    
    if amount > get_balance(sender) and sender != "BANK":
        raise InsufficientFundsException("Insufficient funds")
    elif sender == recipient or amount <= 0.00:
        raise InvalidTransactionException("Invalid transaction")
    elif isnewuser(recipient):
        raise InvalidTransactionException("User does not exist")
    
    blockchain = get_blockchain()
    number = len(blockchain.chain) + 1
    data = "%s-->%s-->%s" %(sender, recipient, amount)
    blockchain.mine(Block(number, data=data))
    sync_blockchain(blockchain)
    
def get_balance(username):
    balance = 0.00
    blockchain = get_blockchain()
    for block in blockchain.chain:
        data = block.data.split("-->")
        if username == data[0]:
            balance -= float(data[2])
        elif username == data[1]:
            balance += float(data[2])
    return balance

def get_blockchain():
    blockchain = Blockchain()
    blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce")
    for b in blockchain_sql.getall():
        blockchain.add(Block(int(b.get('number')), b.get('previous'), b.get('data'), int(b.get('nonce'))))
        
    return blockchain

def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", "number", "hash", "previous", "data", "nonce")
    blockchain_sql.deleteall() 
    
    for block in blockchain.chain:
        blockchain_sql.insert(str(block.number), block.hash(), block.previous_hash, block.data, block.nonce)
        
def test_blockchain():
    blockchain = Blockchain()
    database = ["hello", "gday", "howzit", "seeya"]

    num = 0
    for data in database:
        num += 1
        blockchain.mine(Block(number=num, data=data))
        
    sync_blockchain(blockchain)