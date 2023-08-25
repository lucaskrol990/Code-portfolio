#include <iostream>
#include <fstream>
#include <string>
#include <stdlib.h> // rand
#include <time.h>
#include <cctype>
#include <vector>
#include <algorithm>

using namespace std;

// Function which returns if the word is a valid wordle word
bool validWord(string word, string wordList[], int size);

// Function which makes characters into numbers
int returnVal(char x);

// Function which simulates the game itself
string wordle(string guess, string wordle);


// Function which finds if a specific wordle is valid, based on the letter_info and fixed_info
bool valid_wordle(string wordle, vector<char> fixed_letters, vector<vector<int>> letter_info);

// Function which updates fixed_letters based on a guess
vector<char> update_fixed(vector<char> fixed_letters, string guess, string word);

// Function which updates the letter_info based on a guess
vector<vector<int>> update_info(vector<vector<int>> info_list, string guess, string word);

// Hard mode: function which finds a valid (i.e. possible solution) word that gives the most information
string hard_mode(vector<string> valid_sols, vector<string> valid_wordles, vector<char> fixed_letters, vector<vector<int>> info_list);


int main()
{
  fstream WordleFile;
  WordleFile.open("C:\\Users\\lucas\\OneDrive\\Documenten\\C++\\Test\\Test file\\ValidWordleWords.txt", ios::in);
  // First count the number of lines in the .txt file
  int nlines = 0;
  if (WordleFile.is_open()){ //checking whether the file is open
    string tp;
    while(getline(WordleFile, tp)) {
      nlines++;
    }
    WordleFile.close(); //close the file object.
  }

  // Save all these words in a string array
  string wordleWords[nlines];
  WordleFile.open("C:\\Users\\lucas\\OneDrive\\Documenten\\C++\\Test\\Test file\\ValidWordleWords.txt", ios::in);
  if (WordleFile.is_open()){ //checking whether the file is open
    string tp;
    int i = 0;
    while(getline(WordleFile, tp)){ //read data from file object and put it into string.
       wordleWords[i] = string(tp);
       i++;
    }
    WordleFile.close(); //close the file object.
  }

  // Containing all valid wordle solutions, so will be smaller than nlines after a while
  vector<string> valid_sols;
  valid_sols.reserve(nlines);
  fstream WordleSolutions;
  WordleSolutions.open("C:\\Users\\lucas\\OneDrive\\Documenten\\C++\\Test\\Test file\\WordleSolutions.txt", ios::in);
  if (WordleSolutions.is_open()){ //checking whether the file is open
    string tp;
    while(getline(WordleSolutions, tp)){ //read data from file object and put it into string.
       valid_sols.push_back(string(tp));
    }
    WordleSolutions.close(); //close the file object.
  }

  int nit = valid_sols.size();
  int guesses_needed[nit] = {};
  for (int it = 0; it < nit; it++) {
    cout << it << '\n';
    // Making a copy of valid sols for this iteration
    vector<string> valid_sols_temp;
    valid_sols_temp.reserve(valid_sols.size());
    for (int i = 0; i < valid_sols.size(); i++) {
      valid_sols_temp.push_back(valid_sols[i]);
    }

    // Containing all valid wordles, so will be smaller than nlines after a while
    vector<string> valid_wordles;
    valid_wordles.reserve(valid_wordles.size());
    for (int i = 0; i < nlines; i++) {
      valid_wordles.push_back(wordleWords[i]);
    }

    // Information on the letters
    vector<int> per_letter_info = {0, 1, 2, 3, 4};
    vector<vector<int>> letter_info(26, per_letter_info);
    vector<char> fixed_letters = {'0', '0', '0', '0', '0'};

  // Initialize 1 word as the word to guess
//    srand(9000 * (9 + time(0)) * (10 - time(0))); // some extra randomization
//    int idxWord = rand() % valid_sols_temp.size();
    string theWordle = valid_sols[it];

    // The game itself
    int nround = 6;
    int round = 0;
    bool won = false;
    string guesses[nround];
    string words[nround];
    string word = "salet";

    while (round < nround) {
      if (validWord(word, wordleWords, nlines)) {
        words[round] = word;
        guesses[round] = wordle(word, theWordle);
        fixed_letters = update_fixed(fixed_letters, guesses[round], words[round]);
        letter_info = update_info(letter_info, guesses[round], words[round]);
        valid_wordles.erase(remove_if(valid_wordles.begin(), valid_wordles.end(),
              [fixed_letters, letter_info](string str) {return !valid_wordle(str, fixed_letters, letter_info);}), valid_wordles.end());

        // Removes the invalid wordles from the valid_sols vector
        valid_sols_temp.erase(remove_if(valid_sols_temp.begin(), valid_sols_temp.end(),
                  [fixed_letters, letter_info](string str) {return !valid_wordle(str, fixed_letters, letter_info);}), valid_sols_temp.end());


        won = true;
        for (int i = 0; i < 5; i++) {
          if (guesses[round][i] == '_' || guesses[round][i] == '?') {
            won = false;
          }
        }
        round++;
      }
      if (won) {
        guesses_needed[it] = round;
        break;
      }
      word = hard_mode(valid_sols_temp, valid_wordles, fixed_letters, letter_info);
    }
    if (!won) {
      guesses_needed[it] = round;
    }
  }

  double sum = 0;
  int lost = 0;
  for (int i = 0; i < nit; i++) {
      sum += guesses_needed[i];
      if (guesses_needed[i] == 6) {
        lost += 1;
      }
  }
  double avg_guesses = sum / nit;
  cout << "The average number of guesses needed was " << avg_guesses << '\n';
  cout << "You lost " << lost << " games\n";
  return 0;
}

// Hard mode: function which finds a valid (i.e. possible solution) word that gives the most information
string hard_mode(vector<string> valid_sols, vector<string> valid_wordles, vector<char> fixed_letters, vector<vector<int>> info_list) {
  vector<int> score_pos(5, 0); // The score of a letter per position
  vector<vector<int>> score_letter(26, score_pos); // For every letter, the score per position

  // We only need to assign scores to the letters that are not already fixed
  vector<int> idx = {};
  for (int i = 0; i < fixed_letters.size(); i++) {
    if (fixed_letters[i] == '0') {
      idx.push_back(i);
    }
  }

  // Give a score per letter, per position, for how much information it reveals about the valid sols
  // If a letter (x) appears in the valid sols at position (y) the scores given are as follows:
  // (y) \\ (x)      || no info about (x) yet || (x) is in the word
  // Might be at (y) ||          1            ||         5
  int number_of_yellows[valid_sols.size()];
  for (int i = 0; i < valid_sols.size(); i++) {
    for (int j = 0; j < idx.size(); j++) {
      if (info_list[returnVal(valid_sols[i][idx[j]])].size() == valid_sols[0].size()) { // We have no information about this letter yet
        score_letter[returnVal(valid_sols[i][idx[j]])][idx[j]] += 1;
      } else { // We know it is a yellow letter, so this position is more interesting
        score_letter[returnVal(valid_sols[i][idx[j]])][idx[j]] += 5;
      }
    }
  }

  vector<int> score_words(valid_wordles.size(), 0);
  // Now we can loop through the valid wordles and look at their scores
  for (int i = 0; i < valid_wordles.size(); i++) { // Loop through valid wordles
    for (int j = 0; j < idx.size(); j++) { // Loop through their non-fixed letters
      score_words[i] += score_letter[returnVal(valid_wordles[i][idx[j]])][idx[j]];
    }
  }

  return valid_wordles[distance(begin(score_words), max_element(begin(score_words), end(score_words)))];
}

// Function which makes characters into numbers
int returnVal(char x)
{
    return (int)x - 97;
}

// Function which updates fixed_letters based on a guess
vector<char> update_fixed(vector<char> fixed_letters, string guess, string word) {
  for (int i = 0; i < word.size(); i++) { // Loop through characters of the word
    if (guess[i] != '_' && guess[i] != '?') {
      if (fixed_letters[i] == '0') {
        fixed_letters[i] = word[i];
      }
    }
  }
  return fixed_letters;
}

// Function which updates the letter_info based on a guess
vector<vector<int>> update_info(vector<vector<int>> info_list, string guess, string word) {
  for (int i = 0; i < word.size(); i++) { // Loop through characters of the word
    // First we check if the character is used previously in the word:
    // if it was we know _ does not necessarily mean that the character is not in there
    bool second_char = false;
    for (int j = 0; j < i; j++) {
      if (word[i] == word[j]) {
        second_char = true;
        for (int k = 0; k < info_list[returnVal(word[i])].size(); k++) {
          if (i == info_list[returnVal(word[i])][k]) {
            info_list[returnVal(word[i])].erase(info_list[returnVal(word[i])].begin()+k);
          }
        }
      }
    }
    if (!second_char) {
      if (guess[i] == '_') { // Character is not included in the word
        info_list[returnVal(word[i])] = {}; // No valid position for the character
      } else if (guess[i] == '?') { // Character is included somewhere else in the word
        // So we have to remove it from the valid positions list if it is in there
        int j = 0;
        while(j < info_list[returnVal(word[i])].size()) {
          if (i == info_list[returnVal(word[i])][j]) {
            info_list[returnVal(word[i])].erase(info_list[returnVal(word[i])].begin()+j);
          }
          j++;
        }
      }
    }
  }
  return info_list;
}

// Function which returns if the word is a valid wordle word
bool validWord(string word, string wordList[], int size) {
  if (word.length() == 5) {
    for (int i = 0; i < size; i++) {
      if (word == wordList[i]) {
        return true;
      }
    }
    cout << "Invalid word\n";
    return false;
  } else {
    cout << "Invalid word length \n";
    return false;
  }
}

// Function which finds if a specific wordle is valid, based on the letter_info and fixed_info
bool valid_wordle(string wordle, vector<char> fixed_letters, vector<vector<int>> letter_info) {
  vector<int> idx_check = {}; // Do not include the fixed letter indices in the possible letter check

  // First we check if the fixed letters are in the right spot
  for (int i = 0; i < fixed_letters.size(); i++) {
    if (fixed_letters[i] != '0') {
      if (wordle[i] != fixed_letters[i]) {
        return false; // Can't be a valid wordle if the fixed letter is not at this place
      }
    } else {
      idx_check.push_back(i);
    }
  }

  // Then we check that, for the other letters in the wordle, this letter is possible in this spot
  for (int i = 0; i < idx_check.size(); i++) {
    if (letter_info[returnVal(wordle[idx_check[i]])].size() == 0) {
      return false; // This letter does not appear at all in the word, instant return false
    }
    bool letter_possible = false;
    for (int j = 0; j < letter_info[returnVal(wordle[idx_check[i]])].size(); j++) {
      if (idx_check[i] == letter_info[returnVal(wordle[idx_check[i]])][j]) {
        letter_possible = true; // Wordle letter is in a spot possible
      }
    }
    if (!letter_possible) { // Wordle letter was never in a spot possible
      return false;
    }
  }
  return true;
}

// Function which simulates the game itself
string wordle(string guess, string wordle) {
	bool idxGuessed[wordle.length()] = {false};
	bool idxPlaced[wordle.length()] = {false};
	string output(wordle.length(), ' ');
	// First we find the correctly placed letters
	for (int i = 0; i < wordle.length(); i++) {
    if (guess[i] == wordle[i]) {
			// If the letter is at this position, output letter
			output[i] = guess[i];
			idxGuessed[i] = true;
			idxPlaced[i] = true;
    }
	}

	// For the incorrectly placed letters, we will assign a ? if they appear somewhere else in the wordle
	// Here we check how often each letter appears in the wordle for the remaining letters
	int timesAppear[26] = {0};
	for (int i = 0; i < wordle.length(); i++) {
    if (idxGuessed[i] == false) {
			int index = tolower(wordle[i]) - 'a';
			timesAppear[index] += 1;
    }
	}

	// Then we assign the ? if the letter appear somewhere else in the wordle.
	// Note: if we guess the same letter twice and it appear only once again, we will only check the first one as correct
	for (int i = 0; i < wordle.length(); i++) {
    if (idxPlaced[i] == false) {
      int index = tolower(guess[i]) - 'a';
			if (timesAppear[index] > 0) {
				output[i] = '?';
				idxPlaced[i] = true;
				timesAppear[index] -= 1;
			}
    }
	}

  // For the remaining letters, we just output _
  for (int i = 0; i < wordle.length(); i++) {
    if (idxPlaced[i] == false) {
			output[i] = '_';
    }
  }

  return output;
}
