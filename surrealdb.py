import requests
from requests.auth import HTTPBasicAuth

####################################
# Constant used to define database #
####################################

SURREALDB_URL           = "http://127.0.0.1:8000/sql"
SURREALDB_NAMESPACE     = "cpe314-project"
SURREALDB_DATABASE_NAME = "cpe314-project"
SURREALDB_USER_NAME     = "root"
SURREALDB_USER_PASSWORD = "root"

####################################

# Surreal db database abstraction for querying using web interface
def db(query):
  # Header used by surrealdb to determine what type of content in the header,
  # acceptable type for returning value, namespace for database, and database name
  headers = { 'Content-Type': 'application/json', 
              'Accept':'application/json', 
              'ns': SURREALDB_NAMESPACE, 
              'db': SURREALDB_DATABASE_NAME}
  r = requests.post(  SURREALDB_URL, 
                      data=query, 
                      headers=headers, 
                      auth = HTTPBasicAuth(SURREALDB_USER_NAME, SURREALDB_USER_PASSWORD))
  # raise error if there is some thing error like parse error
  if "code" in r.json(): raise Exception(r.json())
  return r.json()