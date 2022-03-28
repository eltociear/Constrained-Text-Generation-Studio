import dearpygui.dearpygui as dpg
import re
from unittest import result
import string
from collections import Counter
import torch
from torch.nn import functional as F
from transformers import (AutoModelForCausalLM, AutoModelForQuestionAnswering,
                          AutoModelForSeq2SeqLM,
                          AutoModelForSequenceClassification, AutoTokenizer,
                          GPT2Tokenizer, LogitsProcessor, LogitsProcessorList,
                          pipeline, top_k_top_p_filtering)

tokenizer = ""
model = ""



def load_model(the_name):
    global tokenizer
    global model
    if not the_name:
        model_name = dpg.get_value("model_name")
    else:
        model_name = the_name
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)

########--------------------------------------------------------------#### Filters ########--------------------------------------------------------------####

def all_letters_included(word, string_list):
    #any(c in letters for c in word)
    if all(c in word[0] for c in string_list):
        return True
    else:
        return False

def any_letters_included(word, string_list):
    #any(c in letters for c in word)
    if any(c in string_list for c in word[0]):
        return True
    else:
        return False

def all_letters_not_included(word, string_list):
    #any(c in letters for c in word)
    if all(c not in word[0] for c in string_list):
        return True
    else:
        return False

def any_letters_not_included(word, string_list):
    ## "e.g. not words with both B and T in them!"
    if any(c not in string_list for c in word[0]):
        return True
    else:
        return False

def equal_to_length(word, word_length):
    if len(word[0]) == word_length:
        return True
    else:
        return False

def greater_than_length(word, word_length):
    if len(word[0]) > word_length:
        return True
    else:
        return False

def less_than_length(word, word_length):
    if len(word[0]) < word_length:
        return True
    else:
        return False

def ends_with(word, ending_string,  start = None, end = None):
    if word[0].endswith(ending_string, start, end):
        return True
    else:
        return False

def starts_with(word, starting_string, start = None, end = None):
    if word[0].startswith(starting_string, start, end):
        return True
    else:
        return False

def string_in_position(word, a_string, position_index):
    if len(word[0]) > position_index:
        if word[0][position_index] == a_string:
            return True 
    else:
        return False

def palindrome(word):
    the_string = word[0]
    if the_string == the_string[::-1]:
        return True
    else:
        return False

def partial_anagram(word, a_string):
    if Counter(word[0]) - Counter(a_string):
         return False
    return True

def full_anagram(word, a_string):
    if Counter(word[0]) == Counter(a_string):
        return True
    else:
        return False

def isogram(word, count = 1):
    ##Allow user to optionally specify list of characters to isolate
    for char in word[0]:
        if word[0].count(char) > count:
            return False
    return True

def reverse_isogram(word, count = 1):
    ##Allow user to optionally specify list of characters to isolate
    for char in word[0]:
        if word[0].count(char) < count:
            return False
    return True


"""

Ideas 

Longest repeating and non overlapping substring in a string


Find longest palindroming substring
def countSubstrings(self, s: str) -> int:
        @cache
        def isPalindrome(i, j):
            return i >= j or s[i] == s[j] and isPalindrome(i + 1, j - 1)
        return sum(isPalindrome(i, j) for i in range(len(s)) for j in range(i, len(s)))

"""

########--------------------------------------------------------------####          ########--------------------------------------------------------------####

temperature = 1.0
number_of_tokens_to_sample = 25000
replace_spaces = False
selection_window = False
upper_case_transform = False
lower_case_transform = False
lstrip_transform = False 
rstrip_transform = False
strip_transform = False
capitalize_first_letter_transform = False
alpha_numaric_transform = False 
alpha_transform = False
digit_transform = False 
ascii_transform = False

lipogram_naughty_word_list = []
weak_lipogram_naughty_word_list = []
reverse_lipogram_nice_word_list = []
weak_reverse_lipogram_nice_word_list = []

"""
        if alpha_numaric_transform:
            resulting_string = ''.join(ch for ch in resulting_string g if ch.isalnum())
        if alpha_transform:
            resulting_string = ''.join(ch for ch in resulting_string g if ch.isalpha())
        if digit_transform:
            resulting_string = ''.join(ch for ch in resulting_string g if ch.isdigit())
        if ascii_transform:
            resulting_string = ''.join(ch for ch in resulting_string g if ch.isascii())
"""


def get_next_word_without_e(sequence):
    all_letters_filtered_list = []
    #print(tokenizer)
    input_ids = tokenizer.encode(sequence, return_tensors="pt")
    # get logits of last hidden state
    next_token_candidates_logits = model(input_ids)[0][:, -1, :]
    if temperature != 1.0:
        next_token_candidates_logits = next_token_candidates_logits / temperature
    # filter
    filtered_next_token_candidates_logits = top_k_top_p_filtering(next_token_candidates_logits, top_k=number_of_tokens_to_sample, top_p=number_of_tokens_to_sample)
    # sample and get a probability distribution
    probs = F.softmax(filtered_next_token_candidates_logits, dim=-1).sort(descending = True)
    #next_token_candidates = torch.multinomial(probs, num_samples=number_of_tokens_to_sample) ## 10000 random samples
    #print(next_token_candidates)
    word_list = []
    #print(probs[0][0][0].item())
        #print(probs[1])## the indicies, probs[0] is the probabilities
    for iter, candidate in enumerate(probs[1][0]):
        probability = probs[0][0][iter].item()
        resulting_string = tokenizer.decode(candidate) #skip_special_tokens=True, clean_up_tokenization_spaces=True)
        ##TODO: Consider implementing transforms inspired by stuff in the itertools/moreitertools libraries
        if upper_case_transform:
            resulting_string = resulting_string.upper()
        if lower_case_transform:
            resulting_string = resulting_string.lower()
        if replace_spaces == True:
            resulting_string = resulting_string.replace(' ', '')
        if lstrip_transform:
            resulting_string = resulting_string.lstrip()
        if rstrip_transform:
            resulting_string = resulting_string.rstrip()
        if strip_transform:
            resulting_string = resulting_string.strip()
        if capitalize_first_letter_transform:
            resulting_string = resulting_string.capitalize()
        word_list.append((resulting_string, probability))

    #all_letters_filtered_list = [word for word in word_list if all_letters_not_included(word=word, string_list = lipogram_naughty_word_list)]

    for word in word_list:
        return_word = True
        if len(lipogram_naughty_word_list) > 0:
            if not all_letters_not_included(word=word, string_list = lipogram_naughty_word_list):
                return_word = False
        if len(weak_lipogram_naughty_word_list) > 0:
            if not any_letters_not_included(word=word, string_list = weak_lipogram_naughty_word_list):
                return_word = False
        if len(reverse_lipogram_nice_word_list) > 0:
            if not all_letters_included(word=word, string_list = reverse_lipogram_nice_word_list):
                return_word = False 
        if len(weak_reverse_lipogram_nice_word_list) > 0:
            if not any_letters_included(word=word, string_list = weak_reverse_lipogram_nice_word_list):
                return_word = False
        if return_word == True:
            all_letters_filtered_list.append(word)
        

    #all_letters_filtered_list = [word for word in word_list if all_letters_not_included(word=word, starting_string= "EN")]
    #list(filter(all_letters_included, word_list))
    #print(probs)
    #print(all_letters_filtered_list[0:50])
    #print(probs)


                
    return all_letters_filtered_list


def add_generated_word_callback(sender, app_data, user_data):
    current_value = dpg.get_value("string")
    new_string = current_value + str(user_data)
    new_value = dpg.set_value("string", new_string)
    edit_string_callback()

def edit_string_callback():
    string_input = dpg.get_value("string")
    returned_words = get_next_word_without_e(string_input)
    #print(returned_words)
    with dpg.popup(parent = "string"):
        dpg.add_text("Options")
        dpg.add_separator()
        if len(returned_words) >= 1:
            for word in returned_words:
                dpg.add_selectable(label=word, user_data = word[0], callback = add_generated_word_callback)
        else:
            dpg.add_text("No results with the current filters")
            #print(dpg.get_value(word))
            #print(dpg.get_value("yum"))
    #dpg.log_debug(value)





def lipogram_callback(sender, app_data, user_data):
    if app_data == True:
        dpg.show_item("Lipogram Options")
    else:
        dpg.hide_item("Lipogram Options")

def load_naughty_strings_callback():
    global lipogram_naughty_word_list
    string_input = dpg.get_value("lipogram_word_list")
    lipogram_naughty_word_list = string_input.split(" ")
    if not dpg.get_value("naughty_applied"):
        dpg.add_text(tag = "naughty_applied", default_value= "Naughty Strings Applied!", parent = "Lipogram Options")
        dpg.add_text(tag = "naughty_filter" , default_value = "Naughty Strings Filter: " + string_input, parent = "main_window", before = "lipogram")
    else:
        dpg.set_value(item = "naughty_filter", value = "Naughty Strings Filter: " + string_input)
    edit_string_callback()

def weak_lipogram_callback(sender, app_data, user_data):
    if app_data == True:
        dpg.show_item("Weak Lipogram Options")
    else:
        dpg.hide_item("Weak Lipogram Options")

def load_weak_naughty_strings_callback():
    global weak_lipogram_naughty_word_list
    string_input = dpg.get_value("weak_lipogram_word_list")
    weak_lipogram_naughty_word_list = string_input.split(" ")
    if not dpg.get_value("weak_naughty_applied"):
        dpg.add_text(tag = "weak_naughty_applied", default_value= "Weak Naughty Strings Applied!", parent = "Weak Lipogram Options")
        dpg.add_text(tag = "weak_naughty_filter" , default_value = "Weak Naughty Strings Filter: " + string_input, parent = "main_window", before = "lipogram")
    else:
        dpg.set_value(item = "weak_naughty_filter", value = "Weak Naughty Strings Filter: " + string_input)
    edit_string_callback()

def reverse_lipogram_callback(sender, app_data, user_data):
    if app_data == True:
        dpg.show_item("Reverse Lipogram Options")
    else:
        dpg.hide_item("Reverse Lipogram Options")

def load_reverse_naughty_strings_callback():
    global reverse_lipogram_nice_word_list
    string_input = dpg.get_value("reverse_lipogram_word_list")
    reverse_lipogram_nice_word_list = string_input.split(" ")
    if not dpg.get_value("reverse_nice_applied"):
        dpg.add_text(tag = "reverse_nice_applied", default_value= "Nice Strings Applied!", parent = "Reverse Lipogram Options")
        dpg.add_text(tag = "reverse_nice_filter" , default_value = "Nice Strings Filter: " + string_input, parent = "main_window", before = "lipogram")
    else:
        dpg.set_value(item = "reverse_nice_filter", value = "Nice Strings Filter: " + string_input)
    edit_string_callback()

def weak_reverse_lipogram_callback(sender, app_data, user_data):
    if app_data == True:
        dpg.show_item("Weak Reverse Lipogram Options")
    else:
        dpg.hide_item("Weak Reverse Lipogram Options")

def load_weak_reverse_naughty_strings_callback():
    global weak_reverse_lipogram_nice_word_list
    string_input = dpg.get_value("weak_reverse_lipogram_word_list")
    weak_reverse_lipogram_nice_word_list = string_input.split(" ")
    if not dpg.get_value("weak_reverse_nice_applied"):
        dpg.add_text(tag = "weak_reverse_nice_applied", default_value= "Weak Nice Strings Applied!", parent = "Weak Reverse Lipogram Options")
        dpg.add_text(tag = "weak_reverse_nice_filter" , default_value = "Weak Nice Strings Filter: " + string_input, parent = "main_window", before = "lipogram")
    else:
        dpg.set_value(item = "weak_reverse_nice_filter", value = "Weak Nice Strings Filter: " + string_input)
    edit_string_callback()

dpg.create_context()
dpg.create_viewport()
dpg.setup_dearpygui()

load_model(the_name="distilgpt2")
#edit_string_callback("This is an example")

with dpg.window(tag = "main_window", label="CTGS - Contrained Text Generation Studio") as window:
    dpg.add_text("Main Settings")
    dpg.add_text("Enter the name of the pre-trained model from transformers that we are using for Text Generation")
    dpg.add_text("This will download a new model, so it may take awhile or even break if the model is too large")
    dpg.add_input_text(tag = "model_name", width = 500, height = 500, default_value="distilgpt2", label = "Huggingface Model Name")
    dpg.add_button(tag="load_model", label="load_model", callback=load_model)
    dpg.add_text("Select which filters you want to enable")
    dpg.add_text("List of enabled filters: ")
    dpg.add_checkbox(tag="lipogram", label = "All Strings Banned", callback=lipogram_callback)

    with dpg.child_window(tag="Lipogram Options", show = False, height = 100, width = 500) as lipogram_selection_window:
        dpg.add_text("Add naughty letters or strings seperated by a space!")
        dpg.add_input_text(tag = "lipogram_word_list", width = 500, height = 500, label = "Banned Strings")
        dpg.add_button(tag="lipogram_button", label="Load Banned Strings", callback=load_naughty_strings_callback)

    dpg.add_checkbox(tag="weak_lipogram", label = "Any Strings Banned", callback=weak_lipogram_callback)

    with dpg.child_window(tag="Weak Lipogram Options", show = False, height = 100, width = 500) as weak_lipogram_selection_window:
        dpg.add_text("Add naughty letters or strings seperated by a space!")
        dpg.add_input_text(tag = "weak_lipogram_word_list", width = 500, height = 500, label = "Banned Strings")
        dpg.add_button(tag="weak_lipogram_button", label="Load Banned Strings", callback = load_weak_naughty_strings_callback)


    dpg.add_checkbox(tag="reverse_lipogram", label = "All Strings Required", callback=reverse_lipogram_callback)

    with dpg.child_window(tag="Reverse Lipogram Options", show = False, height = 100, width = 500) as reverse_lipogram_selection_window:
        dpg.add_text("Add nice letters or strings seperated by a space!")
        dpg.add_input_text(tag = "reverse_lipogram_word_list", width = 500, height = 500, label = "Forced Strings")
        dpg.add_button(tag="reverse_lipogram_button", label="Load Forced Strings", callback = load_reverse_naughty_strings_callback)

    dpg.add_checkbox(tag="weak_reverse_lipogram", label = "Any Strings Required", callback=weak_reverse_lipogram_callback)

    with dpg.child_window(tag="Weak Reverse Lipogram Options", show = False, height = 100, width = 500) as weak_reverse_selection_window:
        dpg.add_text("Add nice letters or strings seperated by a space!")
        dpg.add_input_text(tag = "weak_reverse_lipogram_word_list", width = 500, height = 500, label = "Forced Strings")
        dpg.add_button(tag="weak_reverse_lipogram_button", label="Load Forced Strings", callback = load_weak_reverse_naughty_strings_callback)

    dpg.add_checkbox(tag="string_position", label = "String In Position")

    with dpg.child_window(tag="Letter Position Options", show = False, height = 100, width = 500) as letter_position_selection_window:
        dpg.add_text("Add the position that you want to force a particular letter to appear at!")
        dpg.add_input_text(tag = "string_for_position", width = 500, height = 500, label = "String to include at position")
        dpg.add_input_int(tag = "string_position_int", label = "Position in string to force letter to be at")
        dpg.add_button(tag="string_position_button", label="Load Strings")

    dpg.add_checkbox(tag="string_starts", label = "String Starts With")

    with dpg.child_window(tag="Starting Starts With Options", show = False, height = 100, width = 500) as starting_string_selection_window:
        dpg.add_text("Add the string that the word should start with")
        dpg.add_input_text(tag = "string_start_word", width = 500, height = 500, label = "String for word to start with")
        dpg.add_button(tag="string_start_button", label="Load Starting String", callback=load_naughty_strings_callback)

    dpg.add_checkbox(tag="string_ends", label = "String Ends With")

    with dpg.child_window(tag="Starting Ends With Options", show = False, height = 100, width = 500) as ending_string_selection_window:
        dpg.add_text("Add the string that the word should end with")
        dpg.add_input_text(tag = "string_end_word", width = 500, height = 500, label = "String for word to end with")
        dpg.add_button(tag="string_end_button", label="Load Ending String", callback=load_naughty_strings_callback)

    dpg.add_checkbox(tag="length_constrained", label = "String Length Equal To")

    with dpg.child_window(tag="Length Constrained Options", show = False, height = 100, width = 500) as length_constrained_selection_window:
        dpg.add_text("Specify the length that you want your strings to be constrained to")
        dpg.add_input_int(tag = "length_constrained_number", label = "Number to constrain the length with")
        dpg.add_button(tag="length_constrained_button", label="Load Length Constrained String", callback=load_naughty_strings_callback)

    dpg.add_checkbox(tag="length_gt", label = "String Length Greater Than")

    with dpg.child_window(tag="Length Greater Than Options", show = False, height = 100, width = 500) as length_gt_selection_window:
        dpg.add_text("Specify the length that you want your strings to be greater than")
        dpg.add_input_int(tag = "length_gt_constrained_number", label = "Number to constrain the length to be greater than")
        dpg.add_button(tag="length_gt_constrained_button", label="Load Length Constrained String", callback=load_naughty_strings_callback)


    dpg.add_checkbox(tag="length_lt", label = "String Length Lesser Than")

    with dpg.child_window(tag="Length Lesser Than Options", show = False, height = 100, width = 500) as length_lt_selection_window:
        dpg.add_text("Specify the length that you want your strings to be lesser than")
        dpg.add_input_int(tag = "length_lt_constrained_number", label = "Number to constrain the length to be lesser than")
        dpg.add_button(tag="length_lt_constrained_button", label="Load Length Constrained String", callback=load_naughty_strings_callback)

    dpg.add_checkbox(tag="palindrome_button", label = "Palindrome")
    dpg.add_checkbox(tag="anagram_button", label = "Anagram")
    dpg.add_checkbox(tag="partial_anagram_button", label = "Partial Anagram")
    dpg.add_checkbox(tag="isogram_button", label = "Isogram")
    dpg.add_checkbox(tag="reverse_isogram_button", label = "Reverse Isogram")
    dpg.add_input_text(tag = "string", width = 500, height = 500, multiline=True, default_value = "Type something here!")
    dpg.add_button(label="Predict New Tokens", callback=edit_string_callback)
edit_string_callback()

dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()

