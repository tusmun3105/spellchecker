def soundex(word):
    # Map each letter to its Soundex digit
    soundex_mapping = {
        "b": "1", "f": "1", "p": "1", "v": "1",
        "c": "2", "g": "2", "j": "2", "k": "2", "q": "2", "s": "2", "x": "2", "z": "2",
        "d": "3", "t": "3",
        "l": "4",
        "m": "5", "n": "5",
        "r": "6"
    }

    # Convert the word to lowercase
    word = word.lower()

    # Remove non-alphabetic characters
    word = ''.join(c for c in word if c.isalpha())

    if not word:
        return ""

    # Convert the first letter to uppercase
    soundex_code = word[0].upper()

    # Encode the remaining letters using Soundex mapping
    for i in range(1, len(word)):
        if word[i] in soundex_mapping:
            digit = soundex_mapping[word[i]]
            if digit != soundex_code[-1]:
                soundex_code += digit

    # Pad the Soundex code to a length of 4
    soundex_code += "000"
    soundex_code = soundex_code[:4]

    return soundex_code


def find_matching_soundex(word, array):
    word_soundex = soundex(word)

    matching_words = []
    for item in array:
        if soundex(item)  == word_soundex :
            matching_words.append(item)

    return matching_words


# Example word and array
word = "moris"
array = ["kreson", "crraeson","creson","kraison","morus"]

matching_words = find_matching_soundex(word, array)
print(matching_words)
