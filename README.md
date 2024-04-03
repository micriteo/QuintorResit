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
4. PostgreSQL is already hosted on azure so you don't have to worry about it
5. Files `__init__` `APIConnect` `datBaseConnectionPyMongo` `api_utils` and all the schemas are parts of the API used by the app. These are separetely hosted on a azure server. Alternatively, on `api` branch you can view the application's api.
6. Run the `registerPage` page to start the application

<h3> Disclaimer </h3> 
For testing purposes, an association is already created and the password for admin is already set - `pass`. However, if a new association is registered, the contents of the Association table must be deleted and, upon registration, a new password will be created along with the IBAN of the association.

<h3> Usage Instructions </h3>
To add files to the program and into the database, you have to put your mt940 file in a folder inside the <strong>base_application</strong> folder called <strong>listener_folder</strong>. Once you place the file in it will be added to the list of transactions as seen in the the table on the right.<br>
You can click on any transaction within the table, and while a transaction is selected the button above the table can be used to edit, update and view the details of the transaction.<br>
Below the table the XML and JSON buttons can be found which switches the table data to their respective data types.<br>
On the left side of the user panel there is a text box where you can search for the transaction containing what you typed in the box, this is done by pressing the <strong>Keyboard Search</strong> Button below.<br>
On the right of the <strong>Keyboard Search</strong> button there is a <strong>Admin Login</strong> button which brings up another page when clicked prompting for an admin password. The password is "pass".
Once on the admin page you can go back using the <strong>Logout</strong> button next to the welcome text.<br>
You can add more members using the "Manage Memberships" button and continuing with the <strong>Add Member</strong> button which will allow you to add the email and username of the new member.<br>
Back in the admin panel, you can search similar to the user panel by typing in the text box and clicking the "Search Keyword" button.<br>
Below the search field, there are two buttons, <strong>Download Transactions in JSON</strong> and <strong>Download Transactions in XML</strong> this will allow the user to get all the contents in the table in the respective file formats.<br>
Everything on the right side of the application is similar to the user panel in functionality.

<h3> Authors </h3>
    
* Dimitri Vastenhout
* Evald Narkevicius
* Teodor Folea
* Stefani Margaritova
* Corvin Wittmaack



