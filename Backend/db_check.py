import pyodbc
from urllib.parse import quote_plus
from sqlalchemy import create_engine

# """Constants"""
# # DATABASE_HOST = '10.0.219.92'
# DB_PORT = '2433'
# DATABASE_HOST = 'VBINBRSUTDB01'
# DATABASE_NAME = "BRSUAT"
# DB_USERNAME = 'BRS'
# DB_PASSWORD = 'Axis@1234'
# DB_TRUSTED_CONNECTION='yes'
# DB_TIMEOUT= 60
# DB_DRIVER= 'SQL Server'


# connection_str = (
#     f"DRIVER={{{.DB_DRIVER}}};"
#     f"SERVER={.DB_HOST},{.DB_PORT};"
#     f"DATABASE={.DB_NAME};"
#     f"UID={.DB_USER};"
#     f"PWD={.DB_PASSWORD};"
#     f"TrustServerCertificate={.DB_TRUSTED_CONNECTION};"
#     f"Connection Timeout={.DB_TIMEOUT};"
# )


# DB_URL = f"mssql+pyodbc:///?odbc_connect={quote_plus(connection_str)}"


# conn_str = (
#     f"DRIVER = {{SQL Server}}"
#     f"SERVER = {DATABASE_HOST},{DB_PORT};"
#     f"DATABASE = {DATABASE_NAME};"
#     f"UID = {DB_USERNAME};"
#     f"PWD = {DB_PASSWORD};"

# )


# """Constants"""
# # DATABASE_HOST = '10.0.219.92'
# DATABASE_HOST = 'VBINBRSUTDB01'
# DB_PORT = '2433'
# DATABASE_NAME = "BRSUAT"
# DB_USERNAME = 'BRS'
# DB_PASSWORD = 'Axis@1234'

# connection_VARCHAR = (f"mssql+pyodbc:///?odbc_connect={quote_plus(f'DRIVER={{SQL Server}};SERVER={DATABASE_HOST},{DB_PORT};DATABASE={DATABASE_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD};TrustServerCertificate=yes;Connection Timeout=60;')}")


# # conn_str = (f"mssql+pyodbc:///?odbc_connect={quote_plus(f'DRIVER={{SQL Server}};SERVER={DATABASE_HOST},{DB_PORT};DATABASE={DATABASE_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD};TrustServerCertificate=yes;Connection Timeout=60;')}")
# # # conn_str = (
#             # f"mssql+pyodbc://{DB_USERNAME}:{quote_plus(DB_PASSWORD)}@{DATABASE_HOST}/{DATABASE_NAME}"
#             # f"?driver={DB_DRIVER}&TrustServerCertificate=yes&Trusted_Connection={DB_TRUSTED_CONNECTION}&Connection Timeout={DB_TIMEOUT}"
#         # )

# try:

#     conn = pyodbc.connect(connection_VARCHAR)
#     print("Connection Successful")

# except Exception as e:
#     print("Connection Failed:", e)

# drivers = pyodbc.drivers()
# print(drivers)



# DATABASE_HOST = '10.0.219.92'
DATABASE_HOST = 'VBINBRSUTDB01'
DB_PORT = '2433'
DATABASE_NAME = "BRSUAT"
DB_USERNAME = 'BRS'
DB_PASSWORD = 'Axis@1234'


def get_db_engine(db_type="mssql"):
    if db_type == "mssql":
        connection_VARCHAR = (f"mssql+pyodbc:///?odbc_connect={quote_plus(f'DRIVER={{SQL Server}};SERVER={DATABASE_HOST},{DB_PORT};DATABASE={DATABASE_NAME};UID={DB_USERNAME};PWD={DB_PASSWORD};TrustServerCertificate=yes;Connection Timeout=60;')}")
        # connection_VARCHAR=""
        print("we are working with this connection",connection_VARCHAR)

        return create_engine(connection_VARCHAR, echo=False, fast_executemany=True)
    else:
        return create_engine(db_url, echo=False)
print(get_db_engine())