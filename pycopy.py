from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from pymongo import MongoClient, errors
from nltk.metrics import edit_distance
from nltk.metrics import distance
from difflib import SequenceMatcher
import difflib
from pymongo.collation import Collation
import re
import time
import configparser
config = configparser.ConfigParser()
config.read('static\config.ini')
connectionstring = config.get('Section1', 'DBConnectionString')
#with open('static\sorted_words.txt', 'r') as f:
#    words = [line.strip() for line in f]
words=[]
client = MongoClient(connectionstring)
db = client['KreolDB']
collection = db['dictionary']
result = collection.find({}, {'_id': 0, 'word': 1}).sort('word', 1)
word_array = [obj['word'] for obj in result]
words=word_array
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("test.html")


@app.route('/test')
def home():
    return render_template('test.html')


@app.route('/admin')
def admin():
    return render_template('admin.html')


@app.route("/get_words")
def get_words():

    # Connection string for MongoDB
    #connection_string = "mongodb://localhost:27017/"
    # Name of the database
    database_name = "KreolDB"
    # Name of the collection
    collection_name = "dictionary"

    # Connect to MongoDB
    client = MongoClient(connectionstring)
    database = client[database_name]
    collection = database[collection_name]
    words = []
    cursor = collection.find({}, {"word": 1})  # Retrieve only the "word" field
    for document in cursor:
        words.append(document["word"])
    return jsonify(sorted(words))


@app.route('/add_word', methods=['POST'])
def add_word():
    client = MongoClient(connectionstring)
    db = client['KreolDB']
    collection = db['dictionary']
    word = request.form.get('word', '').strip()
    if not word:
        return jsonify({'msg': 31})

    existing_word = collection.find_one({'word': word})
    if existing_word:
        return jsonify({'msg': 32})

    new_word = {'word': word}
    collection.insert_one(new_word)

    return jsonify({'msg': 33})


@app.route('/check_word', methods=['POST'])
def check_word():
    client = MongoClient(connectionstring)
    db = client['KreolDB']
    collection = db['dictionary']
    word = request.form.get('word')

    if not word:
        return jsonify({'error': 'Word cannot be empty'})

    existing_word = collection.find_one({'word': word})
    if existing_word:
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})


@app.route('/delete_word', methods=['POST'])
def delete_word():
    client = MongoClient(connectionstring)
    db = client['KreolDB']
    collection = db['dictionary']
    word = request.form.get('word')
    print(word)
    if not word:
        return jsonify({'error': 'Word cannot be empty'})

    # Perform case-insensitive delete using collation
    # Specify locale and strength for case-insensitive comparison
    collation = Collation(locale='en', strength=2)
    result = collection.delete_one(
        {'word': {'$regex': f'^{word}$', '$options': 'i'}}, collation=collation)

    print(result.deleted_count)
    if result.deleted_count > 0:
        return jsonify({'message': 1})
    else:
        return jsonify({'error': 'Word not found in the dictionary'})


@app.route('/get-words-from-mongo', methods=['GET'])
def get_words_from_mongo():
    client = MongoClient(connectionstring)
    db = client['KreolDB']
    collection = db['dictionary']
    result = collection.find({}, {'_id': 0, 'word': 1}).sort('word', 1)
    # word_array = [obj['word'] for obj in result]
    # print (word_array)
    # global words
    # words=word_array
    return jsonify(list(result))


@app.route("/processUser", methods=['POST'])
def uname_upass():

    # Connect to the MongoDB instance
    client = MongoClient(connectionstring)

    # Get a reference to the database
    db = client['KreolDB']

    # Get a reference to the collection
    collection = db['user']

    # Query the collection
    results = collection.find_one(
        {'username': request.form['uname'], 'password': request.form['upass']})

    if (results):
        return jsonify({'success': True, 'redirect_url': url_for('table')})
    else:
        # Return a JSON response indicating failure
        return jsonify({'success': False, 'message': 'Invalid credentials'})


@app.route('/table')
def table():
    return render_template('table.html')


@app.route("/processUserInfo", methods=['POST'])
def receive_value():
    start_time = time.time()
    # correct_word('puissance', words)
    value = request.form['value']
    value=value.replace('@', 'a')
    value = value[0] + value[1:].replace('$', 's')
    value = re.sub(r"[^\w\s'-]", "", value)
    checkifcontainla = 0
    value, checkifcontainla = remove_suffix(value, checkifcontainla)
    incorrectword = value
    missword = remove_consecutive_letters(value)
    changedword = replace_word(missword)
    print(changedword)
    value = correct_word(changedword, words)
    sorted_array = sort_array_by_similarity(value, changedword)
    print(sorted_array)
    matchingsoundex = matching_soundex_words(sorted_array, changedword)

    elapsed_time = time.time() - start_time
    print(f"Execution time: {elapsed_time} seconds")

    print(matchingsoundex)
    if (len(matchingsoundex) > 0):
        matchingsoundex = merge_arrays_with_duplicates(
            matchingsoundex, sorted_array)
        if (checkifcontainla == 1):
            result = []
            for element in matchingsoundex:
                result.append(element + '-la')
                matchingsoundex=result
        response = {'words': matchingsoundex}
        return jsonify(response)

    else:
        if (checkifcontainla == 1):
            result = []
            for element in sorted_array:
                result.append(element + '-la')
                sorted_array=result
        response = {'words': sorted_array}
        return jsonify(response)
    

def custom_distance(word1, word2):
    # Calculate the distances using different algorithms
    lev_distance = distance.edit_distance(word1, word2)
    dlev_distance = distance.edit_distance(word1, word2, transpositions=True)
    jaro_distance = SequenceMatcher(None, word1, word2).ratio()
    jw_similarity = distance.jaro_winkler_similarity(word1, word2)

    # Combine the distances using weights
    distance_sum = lev_distance + dlev_distance + \
        (1 - jaro_distance) + (1 - jw_similarity)
    return distance_sum


def correct_word(word, words):
    # Sort the words in the words array based on their distances from the input word
    closest_words = sorted(words, key=lambda w: custom_distance(w, word))[:26]


    #print(closest_words)
    # Filter out the closest words that are not in the words array
    closest_words = [w for w in closest_words if w in words][:8]


    # Apply a string similarity algorithm (e.g., SequenceMatcher) to get the eight closest words
    #closest_words = difflib.get_close_matches(word, closest_words, n=8)

    # Return the closest words
    return closest_words


def replace_word(word):
    # Define all the replacements as a dictionary
    replacements = {
        'aign':'eny',
        'é':'e',
        'è':'e',
        'ê':'e',
        'à':'a',
        'â':'a',
        'ô':'o',
        'û':'u',
        'manage':'manej',
        'tion': 'sion',
        'yon': 'ion',
        'eux': 'e',
        'end': 'an',
        'pu': 'pou',
        'eur': 'er',
        'iel': 'yel',
        'troi': 'trwa',
        'moi': 'mwa',
        'toi': 'twa',
        'cy': 'si',
        'clet': 'klet',
        'huil': 'wi',
        'ail': 'ay',
        'age': 'az',
        'cul': 'kil',
        'cal': 'kal',
        'zys': 'zis',
        'mau': 'mo',
        'que': 'k',
        'his': 'zis',
        'cir': 'sir',
        'ance': 'ans',
        'plu': 'pli',
        'phy': 'fi',
        'ment': 'man',
        'ace': 'as',
        'age': 'az',
        'oir': 'war',
        'ence': 'ans',
        'q': 'k',
        'euse': 'ez',
        'eau': 'o',
        'aire': 'er',
        'iste': 'is',
        'istre': 'is',
        'ise': 'iz',
        'ice': 'is',
        'ure': 'ir',
        'ade': 'ad',
        'ude': 'id',
        'ege': 'ez',
        'eil': 'ey',
        'aire': 'er',
        'ot': 'o',
        'aitre': 'et',
        'phar':'far',
        'ch': 's',
        'onc': 'onk',
        'coi': 'kwa',
        'oix': 'oi',
        'oi': 'wa',
        'able': 'ab',
        'gile':'zil',
        'ile': 'i',
        'igue': 'ig',
        'then': 'tan',
        'aut': 'ot',
        'aid': 'ed',
        'huit': 'wit',
        'emp': 'anp',
        'aitre': 'e',
        'oue': 'we',
        'ier': 'yer',
        # 'aim':'in',
        'ai': 'e',
        'auce': 'os',
        'cui': 'kwi',
        'aune': 'onn',
        'he': 'e',
        'aud': 'o',
        'aine': 'enn',
        'ain': 'enn',
        'auvre': 'ov',
        'auve': 'ov',
        'sul': 'zil',
        'tient': 'sian',
        'tien': 'sian',
        'j': 'z',
        'riene': 'ryenn',
        'rien': 'ryenn',
        'uge': 'uz',
        'syer': 'zier'

    }

    # Iterate over all the keys in the replacements dictionary and replace the occurrences of each key with its value
    for key in replacements:
        if key in word:
            word = word.replace(key, replacements[key])

    # Return the modified word
    return word


def remove_consecutive_letters(s):
    result = ""
    i = 0
    while i < len(s):
        result += s[i]
        while i < len(s) - 1 and s[i] == s[i+1]:
            i += 1
        i += 1
    return result


def sort_array_by_similarity(array, word):
    sorted_array = sorted(array, key=lambda x: (not x.startswith(
        word[0]), -sum(c in x for c in word), abs(len(x) - len(word))))
    return sorted_array


def soundex(word):
    # Convert word to uppercase
    word = word.upper()

    # Create a dictionary for the Soundex mapping
    soundex_mapping = {
        'BFPV': '1',
        'CGJKQSXZ': '2',
        'DT': '3',
        'L': '4',
        'MN': '5',
        'R': '6'
    }

    # Remove non-alphabetic characters
    word = ''.join(char for char in word if char.isalpha())

    if not word:
        return None

    # Keep the first letter of the word
    soundex_code = word[0]

    # Encode the rest of the word
    for char in word[1:]:
        for key in soundex_mapping:
            if char in key:
                code = soundex_mapping[key]
                if code != soundex_code[-1]:
                    soundex_code += code

    # Remove all occurrences of '0' from the code
    soundex_code = soundex_code.replace('0', '')

    # Pad the code with zeros and truncate to length 4
    soundex_code = (soundex_code + '000')[:4]

    return soundex_code


def matching_soundex_words(word_array, target_word):
    target_soundex = soundex(target_word)

    matching_words = []
    for word in word_array:
        if soundex(word) == target_soundex:
            matching_words.append(word)

    return matching_words


def merge_arrays_with_duplicates(array1, array2):
    merged_array = array1[:]  # Make a copy of array1 to preserve its values

    for item in array2:
        if item not in merged_array:
            merged_array.append(item)

    return merged_array


def remove_suffix(string, string1):
    if string.endswith('la'):
        string1 = 1
        string = string.rstrip('la')
    return string, string1


if __name__ == "__main__":
    app.run(debug=True)
