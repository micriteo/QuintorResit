import copy
import json
import os
import xml.etree.ElementTree as ET
from xml.dom import minidom

from lxml import etree

import psycopg2
from flask import jsonify, request, make_response, Flask, Response
from json2xml import json2xml
from bson import json_util, ObjectId
from bson.json_util import dumps as json_util_dumps
from array import array

from xmlschema import XMLSchema

# xml_member_schema_path = os.path.join(os.path.dirname(__file__), 'member_xml.xsd')

# Get instance of Flask
# from src.base_application.api.main import app
app = Flask(__name__)

from src.base_application.api.dataBaseConnectionPyMongo import get_connection_postgre, get_connection_postgre_user,\
    get_collection
from src.base_application.api.api_utils import validate_json, validate_association_json, validate_member_xml, \
    validate_xml
# Get connection strings to Postgre and MongoDB
transactions_collection = get_collection()
postgre_connection = get_connection_postgre()
postgre_connection_user = get_connection_postgre_user()
postgre_connection.autocommit = True


@app.route("/")
def index():
    answer = {
        "message": "Welcome to Sports Accounting API",
        "api": {
            "test": "/api/test",
            "getTransactionsAmount": "/api/getTransactionsCount",
            "getTransactions": "/api/getTransactions",
            "uploadMT940File": "/api/uploadFile",
            "downloadJSON": "/api/downloadJSON",
            "downloadXML": "/api/downloadXML",
            "searchKeywordSQL": "/api/searchKeyword/<keyword>",
            "insertAssociationSQL": "/api/insertAssociation",
            "insertFileSQL": "/api/insertFile",
            "insertTransactionSQL": "/api/insertTransaction",
            "insertMemberSQL": "/api/insertMemberSQL/<name>/<email>",
            "updateTransactionSQL": "/api/updateTransactionSQL/<transaction_id>",
            "deleteMemberSQL": "/api/deleteMember",
            "getAssociationSQL": "/api/getAssociation"
        }
    }
    return make_response(jsonify(answer), 200)

# ----------------------- No SQL MongoDB functions of the API ---------------------------------


@app.route("/api/test")
def test():
    return make_response(jsonify("API works fine!"))


@app.route("/api/getTransactionsCount", methods=["GET"])
def get_transactions_count():
    output = {"transactionsCount": transactions_collection.count_documents({})}
    return output


@app.route("/api/downloadJSON", methods=["GET"])
def downloadJSON():
    with app.app_context():
        # Get the Content-Type header from the request
        content_type_header = request.headers.get('Content-Type', 'application/json')

        # Check if the Content-Type header is application/json
        if content_type_header == 'application/json':
            # Get the data from the database
            try:
                data = get_all_transactions()
            except TypeError:
                data = []

            # Create a JSON response object
            json_data = json_util.dumps(data, indent=4)
            response = make_response(json_data)
            response.headers['Content-Type'] = 'application/json'
            response.headers['Content-Disposition'] = 'attachment; filename=data.json'
        else:
            # Return an error message if the Content-Type header is not application/json
            return 'Unsupported media type', 415

    return response


@app.route("/api/downloadXML", methods=["GET"])
def downloadXML():
    # Get the data from the database
    try:
        data = get_all_transactions()
    except TypeError:
        data = []

    # Convert the data to a JSON string
    # json_data = json.dumps(data)
    json_data = json_util.dumps(data, indent=4)
    # Convert the JSON data to an ElementTree
    xml_root = ET.fromstring(json2xml.Json2xml(json.loads(json_data)).to_xml())
    xml_str = ET.tostring(xml_root, encoding='utf-8', method='xml')

    # Validate XML
    if not validate_xml(xml_str):
        print('Validation failed')
        # return jsonify({'Error': 'Error Occured'})

    # Create the Flask response object with XML data
    response = make_response(xml_str)
    response.headers["Content-Type"] = "application/xml"
    response.headers["Content-Disposition"] = "attachment; filename=data.xml"
    return response


@app.route("/api/getTransactions", methods=["GET"])
def get_all_transactions():
    output_transactions = []

    for trans in transactions_collection.find():
        output_transactions.append(trans)

    return output_transactions


# Send a POST request with the file path to this function
@app.route("/api/uploadFile", methods=["POST"])
def file_upload():
    # Get the JSON file from the POST request
    json_data = request.get_json()

    # Validate JSON
    if not validate_json(json_data):
        jsonify({'Error': 'Error Occured'})

    # Insert into No SQL Db
    transactions_collection.insert_one(json_data)

    return make_response(jsonify(status="File uploaded!"), 200)


# -------------------------- SQL PostGreSQL DB functions of the API ---------------------------
@app.route("/api/deleteMember", methods=["DELETE"])
def delete_member():
    try:
        member_id = request.args.get('memberid')
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('CALL delete_member(%s)', (member_id,))

        # commit the procedure
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'Member removed'})
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': str(error)})


# The function receives a hashed password
@app.route("/api/insertAssociation", methods=["POST"])
def insert_association():
    try:
        # Get the JSON file from the POST request
        json_data = json.loads(request.get_json())
        # Validate with schema
        if not validate_association_json(json_data):
            print("Schema failed")
            return jsonify({'Error': 'Error Occured'})

        accountID = str(json_data['accountID'])
        name = str(json_data['name'])
        hashed_password = str(json_data['password'])

        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('CALL insert_into_association(%s,%s,%s)', (accountID, name, hashed_password))

        # commit the transaction
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        print("Schema failed")
        return jsonify({'error': error_message})


@app.route("/api/insertMemberSQL", methods=["POST"])
def insert_member():
    try:
        # Get the XML file from the POST request
        xml_file = request.files['file']
        xml_str = xml_file.read().decode('utf-8')

        # Parse the XML string into a ElementTree(XML) object to validate and access
        root = ET.fromstring(xml_str)
        if not validate_member_xml(root):
            print("Failed Validation")
            return jsonify({'Error': 'Error Occured'}), 500

        # Extract 'Name' and 'Email' fields
        name = str(root.findtext('name'))
        email = str(root.findtext('email'))

        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('CALL insert_into_member(%s,%s)', (name, email))

        # commit the transaction
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'Member saved successfully'})
    except Exception as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getAssociation", methods=["GET"])
def get_association():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_association()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/insertTransaction", methods=["POST"])
def insert_transaction():
    try:
        # Get the JSON file from the POST request
        json_trans = request.get_json()

        # Validate JSON
        if not validate_json(json_trans):
            print("Validation failed")
            return jsonify({'Error': 'Error Occured'})

        bank_reference = str(json_trans["transaction_reference"])

        cursor = postgre_connection.cursor()

        for trans_set in json_trans["transactions"]:
            amount = trans_set["amount"]["amount"]
            currency = trans_set["amount"]["currency"]
            transaction_date = trans_set["date"]
            transaction_details = str(trans_set["transaction_details"])
            transaction_details = transaction_details.replace("/", "-")
            description = None
            typetransaction = trans_set["status"]

            cursor.execute('CALL insert_into_transaction(%s,%s,%s,%s,%s,%s,%s,%s,%s)', (
                bank_reference, transaction_details, description, amount, currency, transaction_date, None, None,
                typetransaction))
            # commit the transaction
            postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/insertmtsql", methods=["POST"])
def insert_mt_file():
    try:
        # Get the JSON file from the POST request & parse it into JSON
        json_transactions = request.get_json()

        # Validate JSON
        if not validate_json(json_transactions):
            print("Validation failed")
            return jsonify({'Error': 'Error Occured'})

        # Get amount of transaction in a JSON
        trans_len = len(json_transactions["transactions"])

        # Extract values from a JSON into variables for the File table
        reference_number = str(json_transactions["transaction_reference"])
        statement_number = str(json_transactions["statement_number"])
        sequence_detail = str(json_transactions["sequence_number"])
        available_balance = float(json_transactions["available_balance"]["amount"]["amount"])
        forward_available_balance = float(json_transactions["forward_available_balance"]["amount"]["amount"])
        account_identification = str(json_transactions["account_identification"])

        # Create lists to pass to a Transaction in PostGre
        amount_list = []
        currency_list = []
        trans_date_list = []
        trans_details_list = []
        description_list = []
        type_trans_list = []

        # Prepare transaction data to insert into DB
        for trans_set in json_transactions["transactions"]:
            amount_list.append(float(trans_set["amount"]["amount"]))
            currency_list.append(str(trans_set["amount"]["currency"]))
            trans_date_list.append(str(trans_set["date"]))
            description_list.append(str("None"))
            type_trans_list.append(str(trans_set["status"]))
            # Replace special symbols if necessary to avoid errors in postgre sql
            transaction_details = str(trans_set["transaction_details"])
            transaction_details = transaction_details.replace("/", "-")
            trans_details_list.append(str(transaction_details))

        cursor = postgre_connection.cursor()

        # Call a stored procedure
        cursor.execute('CALL insert_transaction_5(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)', (
            reference_number, statement_number, sequence_detail, available_balance, forward_available_balance, account_identification,
            trans_details_list, description_list, amount_list, currency_list, trans_date_list, type_trans_list))

        # commit the transaction
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': error})


@app.route("/api/insertFile", methods=["POST"])
def insert_file():
    try:
        # Get the JSON file from the POST request
        json_transactions = request.get_json()


        # Validate JSON
        if not validate_json(json_transactions):
            print("Validation failed")
            return jsonify({'Error': 'Error Occured'})

        # Extract values from a JSON into variables for the File table
        reference_number = str(json_transactions["transaction_reference"])
        statement_number = str(json_transactions["statement_number"])
        sequence_detail = str(json_transactions["sequence_number"])
        available_balance = json_transactions["available_balance"]["amount"]["amount"]
        forward_available_balance = json_transactions["forward_available_balance"]["amount"]["amount"]
        account_identification = str(json_transactions["account_identification"])

        cursor = postgre_connection.cursor()

        # Call a stored procedure
        cursor.execute('CALL insert_into_file(%s,%s,%s,%s,%s,%s)', (
            reference_number, statement_number, sequence_detail, available_balance, forward_available_balance, account_identification))

        # commit the transaction
        postgre_connection.commit()

        # close the cursor
        cursor.close()

        return jsonify({'message': 'File inserted successfully'})
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': error})


@app.route("/api/getTransactionsSQL", methods=["GET"])
def get_transactions_sql():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_transaction()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message}), 500


@app.route("/api/getTransactionsSQLXML", methods=["GET"])
def get_transactions_sql_xml():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_transaction()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Create an XML Tree called Data that contains all DB entries from transactions table
        root = ET.Element("Data")
        for row in data:
            # Create one child transaction that will contain information about one db entry
            entry = ET.SubElement(root, "transaction")
            transactionid = ET.SubElement(entry, "transactionid")  # Create a xml element that corresponds to a DB field
            transactionid.text = str(row[0])  # Give that child a value
            refrencenumber = ET.SubElement(entry, "refrencenumber")
            refrencenumber.text = str(row[1])
            transactiondetail = ET.SubElement(entry, "transactiondetail")
            transactiondetail.text = str(row[2])
            description = ET.SubElement(entry, "description")
            description.text = str(row[3])
            amount = ET.SubElement(entry, "amount")
            amount.text = str(row[4])
            currency = ET.SubElement(entry, "currency")
            currency.text = str(row[5])
            transaction_date = ET.SubElement(entry, "transaction_date")
            transaction_date.text = str(row[6])
            categoryid = ET.SubElement(entry, "categoryid")
            categoryid.text = str(row[7])
            memberid = ET.SubElement(entry, "memberid")
            memberid.text = str(row[8])
            typetransaction = ET.SubElement(entry, "typetransaction")
            typetransaction.text = str(row[9])

        # Convert XML to string
        xml_string = ET.tostring(root, encoding="utf-8").decode('utf-8')
        xml_pretty_string = minidom.parseString(xml_string).toprettyxml(indent="  ")
        print(xml_pretty_string)

        # Set content type to XML and return the response
        return Response(xml_pretty_string, content_type='application/xml')


    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message}), 500



# Balance is [4]
@app.route("/api/getFile", methods=["GET"])
def get_file():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_file()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getMembers", methods=["GET"])
def get_members():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM select_all_member()')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getCategory", methods=["GET"])
def get_category():
    try:
        cursor = postgre_connection.cursor()

        # call a stored procedure
        cursor.execute('SELECT * FROM category')

        # Get all data from the stored procedure
        data = cursor.fetchall()

        # Return data in JSON format
        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getTransactionOnId/<trans_id>", methods=["GET"])
def get_transaction_on_id(trans_id):
    try:
        cursor = postgre_connection.cursor()

        cursor.execute('SELECT * FROM select_transaction_on_id(%s)', (int(trans_id),))

        data = cursor.fetchall()

        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/updateTransaction", methods=["PUT"])
def update_transaction():
    try:
        cursor = postgre_connection.cursor()
        # Get data from a post request
        transactionID = request.form.get('trans_id')
        description = request.form.get('desc')
        categoryID = request.form.get('category')
        memberID = request.form.get('member')
        cursor = postgre_connection.cursor()

        if categoryID == "None":
            categoryID = None
        else:
            categoryID = int(categoryID)

        if memberID == "None":
            memberID = None
        else:
            memberID = int(memberID)

        cursor.execute('CALL update_transaction(%s,%s,%s,%s)', (
            transactionID, description, categoryID, memberID))

        return jsonify({'message': 'Transaction Updated'})
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/getTransactionOnIdJoin/<trans_id>", methods=["GET"])
def get_transaction_on_id_join(trans_id):
    try:
        cursor = postgre_connection.cursor()

        cursor.execute('select * from full_join_view where transactionid = %s', (int(trans_id),))

        data = cursor.fetchall()

        return jsonify(data)
    except psycopg2.InterfaceError as error:
        error_message = str(error)
        return jsonify({'error': error_message})


@app.route("/api/searchKeyword/<keyword>", methods=["GET"])
def search_keyword(keyword):
    try:
        cursor = postgre_connection.cursor()

        # Call the search_table2 function with a search term
        cursor.execute("SELECT * FROM search_table2(%s)", (keyword,))

        # Fetch the results from the function call
        results = cursor.fetchall()
        return jsonify(results)
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({'message': error})


if __name__ == '__main__':
    app.run()








