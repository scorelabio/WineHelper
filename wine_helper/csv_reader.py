import os
import csv
import requests as re
import api_tools as api
import json

API_BASE_URL = "http://wine-helper-fake-api.herokuapp.com/api/wines"

def read_csv_file(file_name):
    """
    Read the file with file_name name, except if it is not a csv file.
    """
    csv_file = open(file_name, 'rb')
    rd = csv.reader(csv_file, delimiter=';',quoting=csv.QUOTE_ALL)

    nb_rd_rows = 0
    current_wine = {}
    columns_name = ["name","vintage","appellation","color","wine_id","item_id","price","degustation","food_pairing","food_pairing_french","gws"]
    for row in rd:
        current_object = {}
        nb_column = 0
        nb_rd_rows = nb_rd_rows + 1
        if nb_rd_rows != 1:
            for current_element in row:
                current_element = current_element.replace("é","e")
                current_element = current_element.replace("à","a")
                current_element = current_element.lower()
                to_add = []
                # Case of float
                if current_element[0] >= "0" and current_element[0] <= "9":
                    to_add.append(adapt_type_number(current_element))
                else:
                    to_add = current_element.split(',')
                    for nb in range(len(to_add)):
                        if '(' in to_add[nb]:
                            if nb >= 1:
                                special_values = to_add[nb].split("(")
                                to_add[nb] = special_values[0]
                                to_add[nb].append(special_values[1])
                            else:
                                to_add[nb] = to_add[nb].replace("(","")
                        elif ')' in to_add[nb]:
                            to_add[nb] = to_add[nb].replace(")","")
                        add[nb] = add[nb].strip()
                if len(to_add) > 1:
                    current_object[columns_name[nb_column]] = to_add
                elif len(to_add) == 1:
                    current_object[columns_name[nb_column]] = to_add[0]
                nb_column = nb_column + 1
            if nb_rd_rows == 2:
                #current_request = re.post(API_BASE_URL, json=current_object)
                print("DEBUG LINE " + str(nb_rd_rows) +"\n")
                print(json.dumps(current_object))
                print("\n\n Current request:\n")
                #print(current_request.reason)
                print("\n\n")

def adapt_type_number(current_element):
    is_number = True
    for char in current_element:
        if not (char >= "0" and char <= "9" or char == ","):
            is_number = False
    if is_number:
        if ',' in current_element:
            return float(current_element.replace(",","."))
        else:
            return int(current_element)
    else:
        return current_element


def test_function(current_element):
    to_add = []
    current_object = {}
    # Case of float
    if current_element[0] >= "0" and current_element[0] <= "9":
        if ',' in current_element:
            current_element = current_element.replace(",",".")
        to_add.append(float(current_element))
    else:
        print("COUCOU")
        is_in_parenthesis = False
        to_add = current_element.split(',')
        special_index = -1
        special_value = ""
        for nb in range(len(to_add)):
            print("IN")
            if is_in_parenthesis == True:
                if special_index >=0:
                    to_add[nb] = special_value + " " + to_add[nb]
            if '(' in to_add[nb]:
                print("OPEN PARENTHESIS")
                if nb >= 1:
                    special_index = nb
                    special_value = to_add[nb].split("(")[0]
                is_in_parenthesis = True
                to_add[nb] = to_add[nb].replace("(","")
            elif ')' in to_add[nb]:
                print("CLOSE PARENTHESIS")
                to_add[nb] = to_add[nb].replace(")","")
                is_in_parenthesis = False
    print("TO_ADD:\n\n")
    print(to_add)

read_csv_file("/Users/aymesr/Desktop/Cours/Cours3A/ProjetGL/dev-wine-helper/wine_helper/data/wine_helper_data_wines.csv")
"""
print("FLOAT: ")
print(type(adapt_type_number("6,890")))
print("\n\n")
print("INT: ")
print(type(adapt_type_number("64554")))
print("\n\n")
print("OTHER: ")
print(type(adapt_type_number("6,890-45563")))
print("\n\n")
"""
