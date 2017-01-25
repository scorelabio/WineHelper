import json

#generic function to create button
def create_button(text, payload):
    button = {}
    button['text'] = text
    button['payload'] = payload
    return button

#generic function to create button table
def create_button_table(text):
    table = {}
    table['type'] = 'button'
    table['text'] = text
    table['options'] = []
    return table

#generic function to create criterion
def create_criterion(name, value):
    criterion = {}
    criterion['name'] = name
    criterion['value'] = value
    return criterion

#generic function to create text
def create_text_response(text):
    question = {}
    question['type'] = 'text'
    question['text'] = text
    return question

#function to create whatever option
def create_whatever_button(text):
    button_table = create_button_table(text)
    button_table['options'].append(create_button('Peu importe', 'peu importe '))
    return button_table
