import math
import requests
import os
import ssl
from flask import Flask, jsonify, render_template, request, redirect, session, url_for
from pymongo import MongoClient, errors
from pymongo.errors import ConnectionFailure
from nltk.metrics import edit_distance
from nltk.metrics import distance
from difflib import SequenceMatcher
from metaphone import doublemetaphone
import jellyfish
from pymongo.collation import Collation
import re
import configparser
import json
from soundex import find_matching_soundex
print("helllllllllllllllllllllllllllllllllllllllllllllllllllllo")
config = configparser.ConfigParser()
config.read('static\config.ini')
# config.get('DEFAULT', 'api_URL')
apiURL = 'https://api.api-ninjas.com/v1/imagetotext'
# config.get('DEFAULT', 'DBConnectionString')
connectionstring = os.getenv('MONGODB_URI')
print(connectionstring)
# with open('static\sorted_words.txt', 'r') as f:
#    words = [line.strip() for line in f]
words = []
try:
    # Establish a connection to MongoDB with a timeout of 90 seconds
    client = MongoClient(connectionstring, tls=True,
                         tlsAllowInvalidCertificates=True, serverSelectionTimeoutMS=90000)

    # Check if the connection is successful
    client.admin.command('ping')

    # Connection successful
    print("Connected to the MongoDB database.")

    # Access the database and collection
    db = client['KreolDB']
    collection = db['dictionary']

    # Find all documents, excluding the _id field, and sorting by 'word'
    result = collection.find({}, {'_id': 0, 'word': 1}).sort('word', 1)

    # Print the documents to check the structure
    for obj in result:
        print(obj)  # Print the entire document to see its structure

    # Now process the result and handle missing 'word' fields
    word_array = [obj['word'] for obj in result if 'word' in obj]  # Only add 'word' if it exists
    print("Words from the collection:", word_array)

except ConnectionFailure as e:
    # Connection failed
    print("Failed to connect to the MongoDB database:", str(e))
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


@app.route('/api')
def api():
    return render_template('api.html')


@app.route('/api/spellcheck', methods=['GET'])
def apispellcheck():
    user_query = str(request.args.get('word'))  # /api/spellcheck?word=WORD
    user_query = user_query.lower()
    
    # Assuming `processVal()` returns the response object
    response = processVal(user_query)

    json_data = response.data  # Retrieve the response content as bytes
    json_data_str = json_data.decode('utf-8')  # Decode the bytes to a string

    data = json.loads(json_data_str)  # Parse the JSON string

    words = data["words"]  # Access the "words" field
    state = ""
    if user_query.lower() in words:
        state = 'Correct'
    else:
        state = 'Incorrect'
    if state=='Correct':
        words=[]
    data_set = {'Word2Check': user_query, 'State': state, 'Top8': words} 
    return jsonify(data_set)


@app.route("/get_words")
def get_words():

    # Connection string for MongoDB
    # connection_string = "mongodb://localhost:27017/"
    # Name of the database
    database_name = "KreolDB"
    # Name of the collection
    collection_name = "dictionary"

    # Connect to MongoDB
    ##client = MongoClient(connectionstring, ssl_cert_reqs=ssl.CERT_NONE)
    database = client[database_name]
    collection = database[collection_name]
    words = []
    cursor = collection.find({}, {"word": 1})  # Retrieve only the "word" field
    for document in cursor:
        words.append(document["word"])
    return jsonify(sorted(words))


@app.route('/add_word', methods=['POST'])
def add_word():
    ##client = MongoClient(connectionstring, ssl_cert_reqs=ssl.CERT_NONE)
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
    ##client = MongoClient(connectionstring, ssl_cert_reqs=ssl.CERT_NONE)
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
    ## = MongoClient(connectionstring, ssl_cert_reqs=ssl.CERT_NONE)
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
    ##client = MongoClient(connectionstring, ssl_cert_reqs=ssl.CERT_NONE)
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
    ##client = MongoClient(connectionstring, ssl_cert_reqs=ssl.CERT_NONE)

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


@app.route('/upload', methods=['POST'])
def upload():
    # Check if the 'image' file was sent in the request
    uploadstate = 0
    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'An error occurred while uploading image'})

    # Get the image file from the request
    image_file = request.files['image']

    # Save the image file to a desired location
    image_file.save('static/image/ocr_upload/ocrimage.jpg')
    api_url = apiURL
    image_file_descriptor = open('static/image/ocr_upload/ocrimage.jpg', 'rb')
    files = {'image': image_file_descriptor}
    headers = {'X-Api-Key': '4+yKjmRmN9aN0UmpPgV43w==7ZJyto5wHuIOc4ij'}

    r = requests.post(api_url, files=files, headers=headers)
    response = r.json()
    responseapi = ' '.join(item['text'] for item in response)
    print(responseapi)
    image_file_descriptor.close()
    # Replace with the actual file path
    file_path = 'static/image/ocr_upload/ocrimage.jpg'

    try:
        os.chmod(file_path, 0o777)
        os.unlink(file_path)
        #os.remove(file_path)
        print(f"File '{file_path}' deleted successfully.")
    except FileNotFoundError:
        responseapi = f"File '{file_path}' does not exist."
        return jsonify({'success': False, 'message': responseapi})
    except PermissionError as pe:
        responseapi = f"Permission denied. Unable to delete file '{file_path}'."
        return jsonify({'success': False, 'message': responseapi})
    except Exception as e:
        responseapi = f"An error occurred while deleting the file: {e}"
        return jsonify({'success': False, 'message': responseapi})

    # Return a JSON response indicating failure
    return jsonify({'success': True, 'message': responseapi})


@app.route('/table')
def table():
    return render_template('table.html')


@app.route("/processUserInfo", methods=['POST'])
def receive_value():

    # correct_word('puissance', words)
    value = request.form['value']
    return processVal(value)


def custom_distance(word1, word2):
    # Calculate the distances using different algorithms
    dlev_distance = distance.edit_distance(word1, word2, transpositions=True)
    jw_similarity = distance.jaro_winkler_similarity(word1, word2)

    # Combine the distances using weights
    distance_sum = dlev_distance + (1 - jw_similarity)
    return distance_sum


def correct_word(word, words):
    # Sort the words in the words array based on their distances from the input word
    closest_words = sorted(words, key=lambda w: custom_distance(w, word))[:26]
    word = word.lower()
    arraysoundex = find_matching_soundex(word,words)
    # Step 1: Convert arrays to sets
    x_set = set(closest_words) #closest_words to set
    y_set = set(arraysoundex) #arraysoundex to set

    # Step 2: Intersection of sets (X∩Y) #(closest N arraysoundex)
    #intersection_set = x_set.intersection(y_set)
    #print(intersection_set,"#####################intersection##################################")
    # Step 3: Union of intersection set and X (X∩Y) U X #(closest N arraysoundex) Union closest 
    result_set = y_set.union(x_set)

    # Step 4: Convert set back to array
    result_array = list(result_set)
    print(closest_words)
    print(result_array,"#######################################################")
    # Filter out the closest words that are not in the words array
    closest_words = [w for w in closest_words if w in words][:8]


    # Return the closest words
    return closest_words


def replace_word(word):
    # Define all the replacements as a dictionary
    replacements = {
        'rail':'rel',
        'ange':'anze',
        'oindre':'wenn',
        'aign': 'en',
        'é': 'e',
        'è': 'e',
        'ê': 'e',
        'à': 'a',
        'â': 'a',
        'ô': 'o',
        'û': 'u',
        'qui': 'ki',
        'quoi':'kwa',
        'q': 'k',
        'j': 'z',
        'tion': 'sion',
        'tyon': 'sion',
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
        'mau': 'mo',
        'que': 'k',
        'aigre':'eg',
        'cir': 'sir',
        'ance': 'ans',
        'plu': 'pli',
        'phy': 'fi',
        'psy': 'si',
        'ment': 'man',
        'fant':'fan',
        'ace': 'as',
        'oir': 'war',
        'oit':'wat',
        'ence': 'ans',
        'euse': 'ez',
        'eau': 'o',
        'aire': 'er',
        'air':'er',
        'iste': 'is',
        'istre': 'is',
        'ise': 'iz',
        'ice': 'is',
        'ade': 'ad',
        'eil': 'ey',
        # 'oi': 'wa',
        'aitre': 'et',
        'phar': 'far',
        #'ch': 's',
        'onc': 'onk',
        'coin': 'kwin',
        'coi': 'kwa',
        'oix': 'wa',
        'able': 'ab',
        'gile': 'zile',
        'igue': 'ige',
        'then': 'tan',
        'aut': 'ot',
        'aid': 'ed',
        'huit': 'wit',
        'emp': 'anp',
        'oue': 'we',
        # 'aim':'in',
        # 'ai': 'e',
        'auce': 'os',
        'cui': 'kwi',
        'aune': 'onn',
        'aud': 'o',
        'aine': 'enn',
        'auvre': 'ov',
        'auve': 'ov',
        'sul': 'zil',
        'tient': 'sian',
        'tien': 'sian',
        'riene': 'ryenn',
        'rien': 'ryenn',
        'uge': 'uz',
        'syer': 'sir',
        'soi': 'swa',
        'ract': 'rak',
        'train':'trenn',
        'ouch':'ous',
        'hier':'yer',
        'rais':'res',
        'aig': 'eg'
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
        if i < len(s) - 2 and s[i] == s[i + 1] == s[i + 2]:
            result += s[i + 1]
            i += 2
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
        if soundex(word)[-3:] == target_soundex[-3:]:
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


def calculate_jaro_similarity(word, array):
    def jaro_distance(s1, s2):
        # If the strings are equal
        if s1 == s2:
            return 1.0

        # Length of two strings
        len1 = len(s1)
        len2 = len(s2)

        if len1 == 0 or len2 == 0:
            return 0.0

        # Maximum distance upto which matching
        # is allowed
        max_dist = math.floor(max(len(s1), len(s2)) / 2) - 1

        # Count of matches
        match = 0

        # Hash for matches
        hash_s1 = [0] * len(s1)
        hash_s2 = [0] * len(s2)

        # Traverse through the first string
        for i in range(len1):
            # Check if there is any matches
            for j in range(max(0, i - max_dist), min(len2, i + max_dist + 1)):
                # If there is a match
                if s1[i] == s2[j] and hash_s2[j] == 0:
                    hash_s1[i] = 1
                    hash_s2[j] = 1
                    match += 1
                    break

        # If there is no match
        if match == 0:
            return 0.0

        # Number of transpositions
        t = 0
        point = 0

        # Count number of occurrences
        # where two characters match but
        # there is a third matched character
        # in between the indices
        for i in range(len1):
            if hash_s1[i]:
                # Find the next matched character
                # in second string
                while hash_s2[point] == 0:
                    point += 1

                if s1[i] != s2[point]:
                    point += 1
                    t += 1
                else:
                    point += 1

        t /= 2

        # Return the Jaro Similarity
        return ((match / len1 + match / len2 + (match - t) / match) / 3.0)

    def jaro_Winkler(s1, s2):
        jaro_dist = jaro_distance(s1, s2)

        # If the jaro Similarity is above a threshold
        if jaro_dist > 0.7:
            # Find the length of common prefix
            prefix = 0
            suffix = 0
            for i in range(min(len(s1), len(s2))):
                # If the characters match
                if s1[i] == s2[i]:
                    prefix += 1
                # Else break
                else:
                    break

            # Find the length of common suffix
            for i in range(1, min(len(s1), len(s2)) + 1):
                # If the characters match
                if s1[-i] == s2[-i]:
                    suffix += 1
                # Else break
                else:
                    break

            # Maximum of 3 characters are allowed in prefix and suffix
            prefix = min(3, prefix)
            suffix = min(3, suffix)

            # Calculate Jaro-Winkler Similarity
            jaro_dist += 0.1 * prefix * \
                (1 - jaro_dist) + 0.1 * suffix * (1 - jaro_dist)

        return jaro_dist

    def calculate_bigram_score(s1, s2):
        bigram_score = 0
        for i in range(len(s1) - 1):
            bigram = s1[i:i+2]
            if bigram in s2:
                bigram_score += 1
        return bigram_score

    similarity_scores = []
    for element in array:
        jaro_sim = jaro_distance(word, element)
        jaro_winkler_sim = jaro_Winkler(word, element)
        bigram_score = calculate_bigram_score(element, word)
        similarity_scores.append(
            (jaro_sim, jaro_winkler_sim, bigram_score, element))

    sorted_scores = sorted(similarity_scores, key=lambda x: (
        x[0], x[1], x[2]), reverse=True)
    return sorted_scores


def transform_array(array):
    transformed_array = [(sum(t[:3]), t[3]) for t in array]
    transformed_array.sort(reverse=True)
    output = [t[1] for t in transformed_array]
    return output


def smith_waterman_similarity(str1, str2, match_score=2, mismatch_score=-1, gap_penalty=-1):
    rows = len(str1) + 1
    cols = len(str2) + 1

    matrix = [[0] * cols for _ in range(rows)]
    max_score = 0
    max_i, max_j = 0, 0

    for i in range(1, rows):
        for j in range(1, cols):
            if str1[i - 1] == str2[j - 1]:
                score = match_score
            else:
                score = mismatch_score

            matrix[i][j] = max(
                matrix[i - 1][j - 1] + score,
                matrix[i - 1][j] + gap_penalty,
                matrix[i][j - 1] + gap_penalty,
                0  # Stop negative scores
            )

            if matrix[i][j] > max_score:
                max_score = matrix[i][j]
                max_i, max_j = i, j

    return max_score

def metaPhone(word, array):
    metacode_start, metacode_end = doublemetaphone(word)
    print(doublemetaphone(word))
    arr = array
    arrmeta = [(element, doublemetaphone(element)) for element in arr]

    matchingMeta = [element for element, metaphone in arrmeta if jellyfish.jaro_winkler_similarity(
        metaphone[0], metacode_start) > 0]

    sortedMeta = sorted(matchingMeta, key=lambda x: (jellyfish.jaro_winkler_similarity(
        doublemetaphone(x)[0], metacode_start), smith_waterman_similarity(x, word)), reverse=True)

    for word in sortedMeta:
        metaphone = doublemetaphone(word)
        jaro_start_similarity = jellyfish.jaro_winkler_similarity(
            metaphone[0], metacode_start)
        smith_waterman_score = smith_waterman_similarity(word, word)
        print(f"Word: {word}, Metaphone: {metaphone}, \
              Jaro-Winkler Similarity (Start): {jaro_start_similarity},\
                Smith-Waterman Score: {smith_waterman_score}")

    return sortedMeta

def check_last_character(word,state):
    if word[-1] == ")":
        word = word[:-1]
        return word,1
    else:
        return word,0

def processVal(value):
    value = value.replace('@', 'a')
    value = value[0] + value[1:].replace('$', 's')
    value = re.sub(r"[^\w\s'-)]", "", value)
    if value == 'p':
        value='pe'
    if value == 'r':
        value='ar'
    checkifcontainla = 0
    endBracket=0
    value,endBracket=check_last_character(value,endBracket)
    value, checkifcontainla = remove_suffix(value, checkifcontainla)
    incorrectword = value
    if value == 'mon':
        value = "mo'nn"
    if value == 'monn':
        value = "mo'nn"
    if value == 'p':
        value = 'pe'
    if value == 'bsin':
        value = 'bizin'
    if value == 'bisin':
        value = 'bizin'
    if value == 'b':
        value = 'be'

    value = value.replace("oo", "ou")
    value = value.replace("com", "kom")
    if value.startswith("acc"):
        value = "ak" + value[3:]
    if value.startswith("ach"):
        value = "as" + value[3:]
    if value.startswith("du"):
        value = "di" + value[2:]
    if value.startswith("con"):
        value = "kon" + value[3:]
    if value.startswith("frais"):
        value = "fre" + value[5:]
    if value.startswith("super"):
        value = "siper" + value[5:]
    if value.startswith("souper"):
        value = "siper" + value[5:]
    if value.startswith("chir"):
        value = "shir" + value[4:]
    if value.startswith("chou"):
        value = "chaw" + value[4:]
    if value.startswith("cho"):
        value = "so" + value[3:]
    if value.endswith("ait"):
        value = value[:-3] + "et"
    if value.endswith("ais"):
        value = value[:-3] + "e"
    if value.endswith("nyin"):
        value = value[:-4] + "nien"
    if value.endswith("ture"):
        value = value[:-4] + "tir"
    if value.endswith("rium"):
        value = value[:-4] + "ryom"
    if value.endswith("dure"):
        value = value[:-4] + "dir"
    if value.endswith("phine"):
        value = value[:-5] + "fin"
    if value.endswith("phin"):
        value = value[:-5] + "fin"
    if value.endswith("sic"):
        value = value[:-3] + "sik"
    if value.endswith("zic"):
        value = value[:-3] + "zik"
    if value.endswith("au"):
        value = value[:-2] + "o"
    if value.endswith("sible"):
        value = value[:-5] + "zib"
    if value.endswith("saur"):
        value = value[:-4] + "zor"
    if value.endswith("luche"):
        value = value[:-5] + "lis"
    if value.endswith("gent"):
        value = value[:-4] + "zan"
    if value.endswith("tye"):
        value = value[:-3] + "tie"
    if value.endswith("iere"):
        value = value[:-4] + "ier"
    if value.endswith("huit"):
        value = value[:-4] + "wit"
    if value.endswith("uitre"):
        value = value[:-5] + "wit"
    if value.endswith("main"):
        value = value[:-4] + "me"
    if value.endswith("tent"):
        value = value[:-4] + "tan"
    print(value,"after map")
    missword = remove_consecutive_letters(value)
    print(missword,"after consec")
    changedword = replace_word(missword)
    print(changedword,"+++++++++++++++++++++++++++++++")
    value = correct_word(changedword, words)
    js_jw_bg = calculate_jaro_similarity(changedword, value)
    sorted_array = transform_array(js_jw_bg)
    # sorted_array=calculate_jaro_similarity(changedword, value)
    # sorted_array = [element[1] for element in sorted_array]
    # print (sorted_array)
    # sorted_array = sort_array_by_similarity(value, changedword)
    print(sorted_array)
    # matchingsoundex = matching_soundex_words(sorted_array, changedword)
    matchingsoundex = metaPhone(changedword, sorted_array)

    print(matchingsoundex)
    if (len(matchingsoundex) > 0):
        matchingsoundex = merge_arrays_with_duplicates(
            matchingsoundex, sorted_array)
        if (checkifcontainla == 1):
            result = []
            for element in matchingsoundex:
                result.append(element + '-la')
                matchingsoundex = result
        if(endBracket==1):
            result = []
            for element in matchingsoundex:
                result.append(element + ')')
                matchingsoundex = result           
        response = {'words': matchingsoundex}
        return jsonify(response)

    else:
        if (checkifcontainla == 1):
            result = []
            for element in sorted_array:
                result.append(element + '-la')
                sorted_array = result
        if(endBracket==1):
            result = []
            for element in matchingsoundex:
                result.append(element + ')')
                matchingsoundex = result 
        response = {'words': sorted_array}
        return jsonify(response)


#if __name__ == "__main__":
    #app.run(host="0.0.0.0", port=5000)
    # app.run(debug=True)
