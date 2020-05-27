import csv
import sys
import pandas

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    # dictionnary used to convert months into integer
    dictMonth = {
        'Jan': 0,
        'Feb': 1,
        'Mar': 2,
        'Apr': 3,
        'May': 4,
        'June': 5,
        'Jul': 6,
        'Aug': 7,
        'Sep': 8,
        'Oct': 9,
        'Nov': 10,
        'Dec': 11
    }

    # dictionnary used to convert visitor type into integer
    dictVisitorType = {
        'Returning_Visitor': 1,
        'New_Visitor': 0,
        'Other': 0
    }

    # dictionnary used to convert 'boolean' (string from csv) into integer
    dictBool = {
        'FALSE': 0,
        'TRUE': 1
    }

    evidence = list()
    labels = list()

    with open(filename) as csvfile:
        lines = csv.reader(csvfile, delimiter=',')
        # get rid of headers
        headers = next(lines, None)
        for row in lines:
            # convert data types
            line = [int(row[0]),
                    float(row[1]),
                    int(row[2]),
                    float(row[3]),
                    int(row[4]),
                    float(row[5]),
                    float(row[6]),
                    float(row[7]),
                    float(row[8]),
                    float(row[9]),
                    dictMonth[row[10]],
                    int(row[11]),
                    int(row[12]),
                    int(row[13]),
                    int(row[14]),
                    dictVisitorType[row[15]],
                    dictBool[row[16]]]
            evidence.append(line)
            labels.append(dictBool[row[17]])

    return tuple([evidence, labels])


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    # declare model with k = 1
    model = KNeighborsClassifier(n_neighbors=1)

    # fit the model
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificty).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    true_positives = 0
    true_negatives = 0
    sensitivity = 0.0
    specificity = 0.0

    for row in range(len(predictions)):
        # count positives
        if labels[row] == 1:
            true_positives += 1
            # count true positives
            if labels[row] == predictions[row]:
                sensitivity += 1
        # count negatives
        else:
            true_negatives += 1
            # count true negatives
            if labels[row] == predictions[row]:
                specificity += 1

    # calculate ratios
    sensitivity /= true_positives
    specificity /= true_negatives
    return (sensitivity, specificity)


if __name__ == "__main__":
    main()
