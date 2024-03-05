# Project-6.1 Sports Accounting
### By NHL Stenden Student Team IT3I for Quintor

<h3> Description </h3>
A small desktop application that allows sports assocations to keep track and manage their finances. Sports Accounting is capable of reading MT-940 bank files (.sta) to save and manipulate bank trsanction data locally. The application features a NoSQL MongoDB database for archival storage of the files as well as a PostgreSQL database for manipulating the transactions. 
Sport assocation owners can link transactions to a Bar category or to one of the registered assocation Members.
The application was built with Python and TKinter utilizing Flask to create the API responsible for connecting the app to the two databases.


<h3> Prequisites </h3>

* python 3.6 or higher
* pip
* git
* mt-940 4.28.0
* requests 2.28.2 - Kenneth Reitz
* Flask 2.2.2
* json2xml 3.21.0
* psycopg2 2.9.5
* pymongo 4.3.3
* lxml 4.9.2
* jsonschema 4.17.3


<h3> Installation </h3>

1. Clone the repository or downaload the latest release
2. Install the requirements `pip install -r requirements.txt`
3. Make sure to solve one potential conflict by running these commands
`pip uninstall -y mt940 mt-940`
`pip install -U mt-940`
4. Host the postgresql server either locally (Using PGadmin 4) or online. Create a DB called "Quintor" and restore the DB using the `Quintor` file in src - resources directory. DB's password if needed is "password"
5. Files `__init__` `APIConnect` `datBaseConnectionPyMongo` `main`, `api_utils` and all the schemas are parts of the API used by the app. These can be hosted seperatly on a server. Alternatively, run `main` first to start the flask app locally.
6. If needed, adjust connection strings to MongoDB and PostgreSQL in `dataBaseConnectionPyMongo` file and API server ip in `__init__` file of the api package
7. Run the `registerPage` page to start the application 

<h3> Authors </h3>
    
* Dimitri Vastenhout
* Evald Narkevicius
* Teodor Folea
* Stefani Margaritova
* Corvin Wittmaack



