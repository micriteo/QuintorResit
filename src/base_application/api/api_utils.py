import json
from bson import ObjectId
from lxml import etree
import os
import jsonschema
from xmlschema import XMLSchema
import xml.etree.ElementTree as ET
from dataBaseConnectionPyMongo import get_collection

xml_schema_path = os.path.join(os.path.dirname(__file__), 'schema-definition.xsd')
json_schema_path = os.path.join(os.path.dirname(__file__), 'mt_json_schema.json')
json_member_path_schema = os.path.join(os.path.dirname(__file__), 'insert_member_schema.json')
json_association_schema_path = os.path.join(os.path.dirname(__file__), 'association_json_schema.json')
json_edit_transaction_schema_path = os.path.join(os.path.dirname(__file__), 'edit_transaction_schema.json')
xml_member_schema_path = os.path.join(os.path.dirname(__file__), 'member_xml.xsd')


def validate_json(json_inp):
    try:
        with open(json_schema_path) as r:
            schema = json.load(r)
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        print(str(error))
        return False


def validate_member_json(json_inp):
    try:
        with open(json_member_path_schema) as r:
            schema = json.load(r)
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        print(error)
        return False


def validate_xml(xml_file):
    with open(xml_schema_path, 'r') as f:
        xsd = etree.parse(f)
    schema = etree.XMLSchema(xsd)
    xml_tree = etree.fromstring(xml_file)
    is_valid = schema.validate(xml_tree)
    return is_valid


def validate_association_json(json_inp):
    try:
        with open(json_association_schema_path) as r:
            schema = json.load(r)
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        print(error)
        return False


def validate_member_xml(xml_file):
    schema = XMLSchema(xml_member_schema_path)
    try:
        schema.validate(xml_file)
    except Exception as e:
        return False
    return True


def validate_edit_transaction_json(json_inp):
    try:
        with open(json_edit_transaction_schema_path) as r:
            schema = json.load(r)
            jsonschema.validate(json_inp, schema)
        return True
    except (Exception, jsonschema.ValidationError) as error:
        print(error)
        return False


# XML CRUD

def dict_to_xml(d, root_name='root'):
    root = ET.Element(root_name)
    for key, value in d.items():
        if isinstance(value, dict):
            child = dict_to_xml(value, key)
            root.append(child)
        elif isinstance(value, list):
            for item in value:
                child = ET.Element(key)
                root.append(child)
                dict_to_xml(item, key)
        else:
            child = ET.Element(key)
            child.text = str(value)
            root.append(child)
    return root


def json_file_to_xml(file_path, root_name='root'):
    with open(file_path, 'r') as f:
        json_data = f.read()
    data_dict = json.loads(json_data)
    xml_root = dict_to_xml(data_dict, root_name)
    return ET.tostring(xml_root, encoding='unicode')


# creates a xml entry from json
def xml_create():
    collection = get_collection()

    # json import link to file
    json_imp = open("mt940Example.json")
    json_dict = json.load(json_imp)

    # json validation
    if validate_json(json_dict):
        print("JSON FILE VALIDATED AND CORRECT")
        print(json_dict)
    else:
        print("JSON FILE NOT CORRECT")
        return False

    # xml file to add the convert the entered JSON file into
    xml_mt940 = json_file_to_xml("mt940Example.json", root_name='MT940')
    print(xml_mt940)

    # xml validation
    if validate_xml(xml_mt940):
        print("XML FILE VALIDATED AND CORRECT")
    else:
        print("XML FILE NOT CORRECT")
        print(xml_mt940)
        return False

    collection.insert_one(xml_mt940)


# reads all transactions & returns them as xml entries
def xml_read():
    collection = get_collection()
    documents = collection.find({})

    root = ET.Element("Transactions")
    for document in documents:
        document['_id'] = str(document['_id'])
        xml_root = dict_to_xml(document, "Transaction")
        root.append(xml_root)

    return root


# reads a transaction based on its id
def xml_read_by_object_id(object_id: str):
    collection = get_collection()
    document = collection.find_one({"_id": ObjectId(object_id)})

    if document:
        document['_id'] = str(document['_id'])
        xml_root = dict_to_xml(document, "Transaction")
        return xml_root
    else:
        return None


# updates the xml entry
def xml_update(object_id: str, update: dict):
    object_id = {'_id': ObjectId(object_id)}
    collection = get_collection()
    collection.update_one(object_id, update)


# removes an entry based on its id
def xml_delete(object_id: str):
    collection = get_collection()
    document = collection.delete_one({"_id": ObjectId(object_id)})

    if document.deleted_count > 0:
        print(f"Transaction with _id {object_id} deleted successfully.")
        return True
    else:
        print(f"No transaction found with _id {object_id}.")
        return False
