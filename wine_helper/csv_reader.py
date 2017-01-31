import os
import csv
import requests as re
import api_tools as api
import json
from pprint import pprint

API_BASE_URL = "http://wine-helper-fake-api.herokuapp.com/api/wines"

def read_csv_file(file_name):
    """
    Read the file with file_name name, except if it is not a csv file. Add the datas to the API of url API_BASE_URL.
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
                #current_element = current_element.replace("e","e")
                #current_element = current_element.replace("a","a")
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

def search_translation(file_name,line_original_language,line_new_language,to_translate):
    """
    Translate the string to_translate from the first language into the second language. The function look in the file
    of name file_name.
    """
    csv_file = open(file_name, 'rb')
    rd = csv.reader(csv_file, delimiter=';',quoting=csv.QUOTE_ALL)
    nb_row = 0
    for row in rd:
        nb_row += 1
        if line_original_language >= 0 and line_new_language >= 0:
            if row[line_original_language] == to_translate:
                to_translate = row[line_new_language]
                break
    return to_translate


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


#read_csv_file("/Users/aymesr/Desktop/Cours/Cours3A/ProjetGL/dev-wine-helper/wine_helper/data/wine_helper_data_wines.csv")
#print("LE RESULTAT DE ROUGE EST:" + search_translation("/Users/aymesr/Desktop/Cours/Cours3A/ProjetGL/dev-wine-helper/wine_helper/data/translate_file.csv",2,1,"rouge"))
