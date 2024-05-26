import data_base
import config

db = data_base.UsersDatabaseManager(config.DB_NAME)
print(db.get_data(213))
del db