#import nltk
#from sklearn.feature_extraction.text import CountVectorizer
#from sklearn.cluster import KMeans
#from nltk.metrics import edit_distance
#from nltk.metrics import distance

with open('static\sorted_words.txt', 'r') as f:
    words = [line.strip() for line in f]

from nltk.metrics import edit_distance
from nltk.metrics import distance
from difflib import SequenceMatcher

def custom_distance(word1, word2):
    # Calculate the distances using different algorithms
    lev_distance = distance.edit_distance(word1, word2)
    dlev_distance = distance.edit_distance(word1, word2, transpositions=True)
    jaro_distance = SequenceMatcher(None, word1, word2).ratio()
    jw_similarity = distance.jaro_winkler_similarity(word1, word2)

    # Combine the distances using weights
    distance_sum = lev_distance + dlev_distance + (1 - jaro_distance) + (1 - jw_similarity)
    return distance_sum

def correct_word(word, words):
    # Sort the words in the words array based on their distances from the input word
    closest_words = sorted(words, key=lambda w: custom_distance(w, word))[:26]
    
    # Filter out the closest words that are not in the words array
    closest_words = [w for w in closest_words if w in words][:8]
    
    # Return the closest words
    return closest_words


def replace_word(word):
    # Define all the replacements as a dictionary
    replacements = {
        'yon': 'ion',
        'eux':'e',
        'end':'an',
        'pu': 'pou',
        'eur': 'er',
        'iel': 'yel',
        'troi': 'trwa',
        'moi': 'mwa',
        'toi': 'twa',
        'cy': 'si',
        'clet': 'klet',
        'ett': 'et',
        'huil': 'wi',
        'ail': 'ay',
        'age': 'az',
        'cul': 'kil',
        'cal': 'kal',
        'elle': 'el',
        'zys': 'zis',
        'mau': 'mo',
        'que': 'k',
        'his': 'zis',
        'cir': 'sir',
        'ance': 'ans',
        'plu': 'pli',
        'phy': 'fi',
        'ment': 'man',
        'mme': 'm',
        'ace': 'as',
        'age': 'az',
        'oir': 'war',
        'ence':'ans',
        'q':'k',
        'x':'ks',
        'euse':'ez',
        'eau':'o',
         'aire':'er',
         'iste':'is',
         'istre':'is',
         'ise':'iz',
         'ice':'is',
         'ure':'ir',
         'ade':'ad',
         'nne':'nn',
         'ude':'id',
         'ege':'ez',
         'eil':'ey',
         'aire':'er',
         'ot':'o',
         'aitre':'et',
        'ch':'s',
        'onc':'onk',
        'coi':'kwa',
        'oix':'oi',
        'oi':'wa',
        'able':'ab',
        'ille':'i',
        'igue':'ig',
        'then':'tan',
        'aut':'ot',
        'aid':'ed',
        'huit':'wit',
        'emp':'anp',
        'aitre':'e',
        'oue':'we',
        'ier':'yer',
        'auce':'os',
        #'aim':'in',
        'ai':'e',
        'cui':'kwi',
        'aune':'onn',
        'he':'e'
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


missword='quarantaine'#sime
missword=remove_consecutive_letters(missword)
print(missword)
changedword=replace_word(missword)
print(changedword)
arrdist=correct_word(changedword, words)
print(arrdist)  # Output: 'mango'

def sort_array_by_similarity(array, word):
    sorted_array = sorted(array, key=lambda x: (not x.startswith(word[0]), -sum(c in x for c in word), abs(len(x) - len(word))))
    return sorted_array

sorted_array = sort_array_by_similarity(arrdist, changedword)
print(sorted_array)


