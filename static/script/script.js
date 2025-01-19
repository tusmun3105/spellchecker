function splitSentence(sentence) {
  // Split the sentence into words by space
  const words = sentence.split(' ');

  // Return the list of words
  return words;
}

function removeStartingPunctuations(s) {
  let i = 0;
  while (i < s.length && [',', '.', '?', '!', ':', ';'].includes(s[i])) {
    i++;
  }
  return s.slice(i);
}

function extractPunctuation(arr) {
  const new_arr = [];
  const punctuations = ['.', ',', ';', ':', '!', '?'];
  for (const s of arr) {
    // Split the string into sentences using regex
    const sentences = s.split(/(?<=[.!?])\s+/);

    for (const sentence of sentences) {
      // Split the sentence into words using whitespace
      const words = sentence.split(' ');

      for (let i = 0; i < words.length; i++) {
        const word = words[i];
        // Check if the last character of the word is punctuation
        if (punctuations.includes(word.slice(-1))) {
          // Add the word without its last character
          new_arr.push(word.slice(0, -1));
          // Add the punctuation character to the next position in the array
          new_arr.push(word.slice(-1));
        } else {
          // Add the word to the array without modification
          new_arr.push(word);
        }
      }
    }
  }
  return new_arr;
}
function splitWords(arr) {
  const words = [];
  for (const string of arr) {
    let current_word = "";
    for (const char of string) {
      if (/\s/.test(char) || /[.,?!]/.test(char)) {
        if (current_word) {
          words.push(current_word);
          current_word = "";
        }
        if (/[.,?!]/.test(char)) {
          words.push(char);
        }
      } else {
        current_word += char;
      }
    }
    if (current_word) {
      words.push(current_word);
    }
  }
  return words;
}
function arrayToString(arr) {
  let result = '';
  for (let i = 0; i < arr.length; i++) {
    const elem = arr[i];
    if (i === 0) {
      // add the first element without a space before it
      result += elem;
    } else if (elem === '?' || elem === '!' || elem === '.') {
      // add the question mark, exclamation mark, or period as a separate element without a space before it
      result += elem;
    } else if (elem.match(/[a-zA-Z0-9-]/) && !arr[i - 1].match(/[a-zA-Z0-9-]/)) {
      // add a space before the current element if the previous element is non-alphanumeric
      result += ' ' + elem;
    } else if (elem.match(/[a-zA-Z0-9-]/) && arr[i - 1].match(/[a-zA-Z0-9-]/) && elem !== '-') {
      // add a space before the current element if the previous element is alphanumeric and the current element is not a hyphen
      result += ' ' + elem;
    } else {
      // add the current element without a space before it if the current element is punctuation or a hyphen
      result += elem;
    }
  }
  return result;
}

function removeSpaceAfterHyphen(sentence) {
  return sentence.replace(/-\s/g, '-');
}


// function findPositions(array1, array2) {
//   const positions = [];
//   for (let i = 0; i < array2.length; i++) {
//     const element = array2[i];
//     const elementwithoutla = element.replace(/-la/g, "");
//     if (array1.includes(element.toLowerCase()) === false && array1.includes(elementwithoutla.toLowerCase()) === false) {
//       if (element.charAt(0) !== element.charAt(0).toUpperCase()) {
//         positions.push(i);
//       }

//     }
//   }
//   return positions;
// }
// function findPositions(array1, array2) {
//   var positions = [];
//   var set1 = array1
  
//   for (let i = 0; i < array2.length; i++) {
//     const element = array2[i];
//     const elementWithoutLa = element.replace(/-la/g, "").toLowerCase();
//     console.log(element);
//     console.log(elementWithoutLa);
//     if (!set1.has(elementWithoutLa) && !set1.has(element.toLowerCase())) {
//       if (element.charAt(0) !== element.charAt(0).toUpperCase()) {
//         positions.push(i);
//       }
//     }
//   }
  
//   return positions;
// }
function findPositions(array1, array2) {
  var positions = [];
  var set1 = new Set(array1);  // Keep original case in the set
  
  for (let i = 0; i < array2.length; i++) {
    const element = array2[i];
    const elementWithoutLa = element.replace(/-la/g, "");
    
    console.log(element);
    console.log(elementWithoutLa);
    
    // Compare in lowercase only
    if (!set1.has(elementWithoutLa.toLowerCase()) && !set1.has(element.toLowerCase())) {
      // Check if the first character is not uppercase
      if (element.charAt(0) !== element.charAt(0).toUpperCase()) {
        positions.push(i);  // Add position to the result
      }
    }
  }
  
  return positions;
}

function underlineElements(array1, array2) {
  for (let i = 0; i < array2.length; i++) {
    if (array2[i] < array1.length) {
      if (isNaN(array1[array2[i]])) {
        array1[array2[i]] = "<span class='suggestclass'  id='error" + i + "' style='text-decoration-line: underline; text-decoration-style: dashed; text-underline-position: under; text-decoration-color: red;'>" + array1[array2[i]] + "</span><span class='suggestclass'  id='suggestions" + i + "'></span>";
      }
    }
  }
  return array1;
}
function shiftLastBracket(arr){
  for(var i=0;i<arr.length-1;i++){
    var str=arr[i];
    const lastChar = str.charAt(str.length - 1);
    if(lastChar === "("){
        arr[i]= arr[i].slice(0, -1);
        arr[i+1]="("+arr[i+1];
    }
}
return arr;
}


function concatenateElementsWithHyphen(array) {
  var concatenatedArray = [];
  var currentElement = '';

  for (var i = 0; i < array.length; i++) {
    if (array[i].endsWith('-')) {
      currentElement += array[i];
    } else {
      currentElement += array[i];
      concatenatedArray.push(currentElement);
      currentElement = '';
    }
  }

  if (currentElement !== '') {
    concatenatedArray.push(currentElement);
  }

  return concatenatedArray;
}

function arrayToString(arr) {
  let result = '';
  for (let i = 0; i < arr.length; i++) {
    const elem = arr[i];
    if (i === 0) {
      // add the first element without a space before it
      result += elem;
    } else if (elem.match(/[a-zA-Z0-9]/) && !arr[i - 1].match(/[a-zA-Z0-9]/)) {
      // add a space before current element if previous element is non-alphanumeric
      result += ' ' + elem;
    } else if (elem.match(/[a-zA-Z0-9$£]/) && arr[i - 1].match(/[a-zA-Z0-9]/)) {
      // add a space before current element if previous element is alphanumeric
      result += ' ' + elem;
    } else {
      // add current element without a space before it if current element is punctuation
      result += elem;
    }
  }
  return result;
}

function removeAdjacentPunctuations(arr) {
  const cleanedArr = [];
  let prevPunct = false;  // flag to keep track of whether the previous element was a punctuation mark
  for (let i = 0; i < arr.length; i++) {
    if (['.', ',', '?', '!', ':', ';'].includes(arr[i])) {
      // if the previous element was not a punctuation mark, add the current punctuation mark
      if (!prevPunct) {
        cleanedArr.push(arr[i]);
      }
      prevPunct = true;
    } else {
      cleanedArr.push(arr[i]);
      prevPunct = false;
    }
  }
  return cleanedArr;
}



function extractDigits(str) {
  // Use a regular expression to match the digits in the string
  let matches = str.match(/\d+/);

  if (matches) {
    // If there is a match, parse the matched string as an integer
    return parseInt(matches[0]);
  } else {
    // If there is no match, return null or some other default value
    return null;
  }
}


function capAfterDot(str) {
  const punctuation = ['.', ',', ';', ':', '!', '?', '-', '—', '(', ')', '[', ']'];
  let result = '';
  for (let i = 0; i < str.length; i++) {
    let char = str[i];
    if (punctuation.includes(char) && char !== '.') {
      result += char + ' ';
    } else {
      result += char;
    }
  }
  result = result.replace(/\.(\w)/g, (match, p1) => '. ' + p1.toUpperCase()); // add space after period and capitalize next letter
  return result;
}

function capitalizeAfterPunctuation(arr) {
  const punctuationMarks = ['.', '!', '?']; // Add more punctuation marks if needed
  const result = [];

  let capitalizeNext = false;

  for (let i = 0; i < arr.length; i++) {
    const current = arr[i];

    if (capitalizeNext && current.length > 0) {
      const capitalized = current.charAt(0).toUpperCase() + current.slice(1);
      result.push(capitalized);
      capitalizeNext = false;
    } else {
      result.push(current);
    }

    if (punctuationMarks.includes(current)) {
      capitalizeNext = true;
    }
  }

  return result;
}
