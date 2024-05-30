import MySQLdb

class BlockchainTableManager:
    def __init__(self, host, user, passwd, dbname, table_name, columns):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.dbname = dbname
        self.table_name = table_name
        self.columns = columns
        self.connection = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname)
        self.cursor = self.connection.cursor()

    def drop_table(self):
        drop_query = f"DROP TABLE IF EXISTS {self.table_name}"
        self.cursor.execute(drop_query)
        self.connection.commit()

    def create_table(self):
        columns_query = ", ".join(self.columns)
        create_query = f"CREATE TABLE {self.table_name} ({columns_query})"
        self.cursor.execute(create_query)
        self.connection.commit()

    def delete_all(self):
        self.drop_table()
        self.create_table()

    def close(self):
        self.cursor.close()
        self.connection.close()

# Example usage
columns = [
    "block_index INT NOT NULL PRIMARY KEY",
    "hash VARCHAR(255) NOT NULL",
    "previous VARCHAR(255)",
    "data TEXT",
    "nonce INT"
]

manager = BlockchainTableManager(
    host="localhost",
    user="your_username",
    passwd="your_password",
    dbname="your_database",
    table_name="blockchain",
    columns=columns
)

# Drop and recreate the table
manager.delete_all()

# Close the connection
manager.close()
