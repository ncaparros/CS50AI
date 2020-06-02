import nltk
import sys
import os
import math
import operator

FILE_MATCHES = 1
SENTENCE_MATCHES = 1


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python questions.py corpus")

    # Calculate IDF values across files
    files = load_files(sys.argv[1])
    file_words = {
        filename: tokenize(files[filename])
        for filename in files
    }
    file_idfs = compute_idfs(file_words)

    # Prompt user for query
    query = set(tokenize(input("Query: ")))

    # Determine top file matches according to TF-IDF
    filenames = top_files(query, file_words, file_idfs, n=FILE_MATCHES)

    # Extract sentences from top files
    sentences = dict()
    for filename in filenames:
        for passage in files[filename].split("\n"):
            for sentence in nltk.sent_tokenize(passage):
                tokens = tokenize(sentence)
                if tokens:
                    sentences[sentence] = tokens

    # Compute IDF values across sentences
    idfs = compute_idfs(sentences)

    # Determine top sentence matches
    matches = top_sentences(query, sentences, idfs, n=SENTENCE_MATCHES)
    for match in matches:
        print(match)


def load_files(directory):
    """
    Given a directory name, return a dictionary mapping the filename of each
    `.txt` file inside that directory to the file's contents as a string.
    """
    output = dict()
    for dirpath, dirnames, filenames in os.walk(os.getcwd() + os.sep + directory):
        for filename in filenames:
            with open(os.getcwd() + os.sep + directory + os.sep + filename, encoding="utf8") as f:
                output[filename] = f.read()
    return output


def tokenize(document):
    """
    Given a document (represented as a string), return a list of all of the
    words in that document, in order.

    Process document by coverting all words to lowercase, and removing any
    punctuation or English stopwords.
    """
    output = nltk.word_tokenize(document)
    import string

    # first filter, get rid of punctuation and part of stopwords
    output = list(filter(lambda a: (a not in string.punctuation
                                    and a not in nltk.corpus.stopwords.words("english")
                                    and a != "''"
                                    and a != "``"), output))

    # lowercase all words
    for index, word in enumerate(output):
        output[index] = word.lower()

    # second filter, get rid of stop words i.e. previously with uppercase
    output = list(filter(lambda a: a not in nltk.corpus.stopwords.words("english"), output))
    return output


def compute_idfs(documents):
    """
    Given a dictionary of `documents` that maps names of documents to a list
    of words, return a dictionary that maps words to their IDF values.

    Any word that appears in at least one of the documents should be in the
    resulting dictionary.
    """
    idfs = dict()
    words = set()
    for filename in documents:
        words.update(documents[filename])

    for word in words:
        f = sum(word in documents[filename] for filename in documents)
        idf = math.log(len(documents) / f)
        idfs[word] = idf

    return idfs


def top_files(query, files, idfs, n):
    """
    Given a `query` (a set of words), `files` (a dictionary mapping names of
    files to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the filenames of the the `n` top
    files that match the query, ranked according to tf-idf.
    """
    tfidfs = dict()
    output = list()
    for filename in files:
        tfidfs[filename] = 0
        for word in query:
            tf = files[filename].count(word)
            tfidfs[filename] += tf * idfs[word]

    # sort files by tf-idfs
    output = sorted(tfidfs, key=tfidfs.get, reverse=True)

    return output[:n]


def top_sentences(query, sentences, idfs, n):
    """
    Given a `query` (a set of words), `sentences` (a dictionary mapping
    sentences to a list of their words), and `idfs` (a dictionary mapping words
    to their IDF values), return a list of the `n` top sentences that match
    the query, ranked according to idf. If there are ties, preference should
    be given to sentences that have a higher query term density.
    """
    tfidfs = dict()

    for sentence in sentences:
        tfidfs[sentence] = 0
        cleaned_sentence = tokenize(sentence)
        for word in query:
            if word in cleaned_sentence:
                tfidfs[sentence] += idfs[word]

    # sort sentences by idfs
    sorted_tfidfs = sorted(tfidfs, key=tfidfs.get, reverse=True)

    # get sentences with maximum idfs
    best_sentences = list(k for k in tfidfs.keys() if tfidfs[k] == tfidfs[sorted_tfidfs[0]])

    # if all the sentences with max idfs are less than n, sort them and return the n firsts
    densities = calculate_density(best_sentences, query)

    if len(best_sentences) >= n:
        return densities[:n]
    else:
        # total number of sentences sorted so far
        total = len(best_sentences)

        # while total number of sentences sorted less than n
        while total < n:
            # get next batch of sentences (rank n idfs)
            next_sentences = list(k for k in tfidfs.keys() if tfidfs[k] == tfidfs[sorted_tfidfs[total]])
            total += len(next_sentences)
            next_dentities = calculate_density(next_sentences, query)
            # add new densities to the output
            for next_density in next_dentities:
                densities.append(next_density)
        return densities[:n]


def calculate_density(sentences, query):
    """
    Given a query (set of word), calculate the density of a list of sentences,
    and sort them by descending density.
    Density : sum of the words in the sentence and the query/sum of the words in the sentence
    """
    densities = dict()
    for sentence in sentences:
        cleaned_sentence = tokenize(sentence)
        densities[sentence] = len(list(word for word in cleaned_sentence if word in query))/len(cleaned_sentence)

    sorted_dens = sorted(densities, key=densities.get, reverse=True)
    return sorted_dens


if __name__ == "__main__":
    main()
