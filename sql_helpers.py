from app import mysql, session
from blockchain import Block, Blockchain

class InvalidTransactionException(Exception): pass
class InsufficientFundsException(Exception): pass

class Table:
    def __init__(self, table_name, *args):
        self.table = table_name
        self.columnsList = args
        self.columns = "(%s)" % ",".join([col.split()[0] for col in args])

        if isnewtable(table_name):
            self.create_table()

    def getall(self):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM %s" % self.table)
        data = cur.fetchall()
        cur.close()
        return data

    def getone(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM %s WHERE %s = \"%s\"" % (self.table, search, value))
        data = cur.fetchone()
        cur.close()
        return data

    def deleteone(self, search, value):
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM %s WHERE %s = \"%s\"" % (self.table, search, value))
        mysql.connection.commit()
        cur.close()

    def deleteall(self):
        self.drop()
        self.create_table()
        blockchain = Blockchain()
        self.sync_blockchain(blockchain)

    def drop(self):
        cur = mysql.connection.cursor()
        cur.execute("DROP TABLE IF EXISTS %s" % self.table)
        mysql.connection.commit()
        cur.close()

    def create_table(self):
        cur = mysql.connection.cursor()
        create_query = f"CREATE TABLE {self.table} (id INT AUTO_INCREMENT PRIMARY KEY, {', '.join(self.columnsList)})"
        cur.execute(create_query)
        mysql.connection.commit()
        cur.close()

    def insert(self, *args):
        column_names = ",".join([col.split()[0] for col in self.columnsList])
        placeholders = ",".join(["%s"] * len(args))
        cur = mysql.connection.cursor()
        insert_query = f"INSERT INTO {self.table} ({column_names}) VALUES ({placeholders})"
        cur.execute(insert_query, args)
        mysql.connection.commit()
        cur.close()

    def sync_blockchain(self, blockchain):
        for block in blockchain.chain:
            self.insert(block.number, block.hash(), block.previous_hash, block.data, block.nonce)

def sql_raw(execution):
    cur = mysql.connection.cursor()
    cur.execute(execution)
    mysql.connection.commit()
    cur.close()

def isnewtable(tableName):
    cur = mysql.connection.cursor()
    try:
        cur.execute("SELECT 1 FROM %s LIMIT 1" % tableName)
    except:
        cur.close()
        return True
    cur.close()
    return False

def isnewuser(username):
    users = Table("users", "name VARCHAR(255)", "username VARCHAR(255)", "email VARCHAR(255)", "password VARCHAR(255)")
    data = users.getall()
    usernames = [user.get('username') for user in data]
    return False if username in usernames else True

def send_money(sender, recipient, amount):
    try:
        amount = float(amount)
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
    data = "%s-->%s-->%s" % (sender, recipient, amount)
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
    blockchain_sql = Table("blockchain", "number INT", "hash VARCHAR(64)", "previous VARCHAR(64)", "data TEXT", "nonce INT")
    for b in blockchain_sql.getall():
        blockchain.add(Block(int(b['number']), b['previous'], b['data'], int(b['nonce'])))
    return blockchain

def sync_blockchain(blockchain):
    blockchain_sql = Table("blockchain", "number INT", "hash VARCHAR(64)", "previous VARCHAR(64)", "data TEXT", "nonce INT")
    blockchain_sql.deleteall()
    for block in blockchain.chain:
        blockchain_sql.insert(block.number, block.hash(), block.previous_hash, block.data, block.nonce)

def test_blockchain():
    blockchain = Blockchain()
    database = ["hello", "gday", "howzit", "seeya"]

    num = 0
    for data in database:
        num += 1
        blockchain.mine(Block(number=num, data=data))

    sync_blockchain(blockchain)

