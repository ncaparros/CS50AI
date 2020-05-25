import csv
import itertools
import sys

PROBS = {

    # Unconditional probabilities for having gene
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait given two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait given one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait given no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():

    # Check for proper usage
    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1
    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):
    """
    Load gene and trait data from a file into a dictionary.
    File assumed to be a CSV containing fields name, mother, father, trait.
    mother, father must both be blank, or both be valid names in the CSV.
    trait should be 0 or 1 if trait is known, blank otherwise.
    """
    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):
    """
    Compute and return a joint probability.

    The probability returned should be the probability that
        * everyone in set `one_gene` has one copy of the gene, and
        * everyone in set `two_genes` has two copies of the gene, and
        * everyone not in `one_gene` or `two_gene` does not have the gene, and
        * everyone in set `have_trait` has the trait, and
        * everyone not in set` have_trait` does not have the trait.
    """
    probability = 1
    for person in people:
        # If the person has no known parent, we use unconditional probabilities
        if people[person]["mother"] == None and people[person]["father"] == None:
            if person in one_gene:
                probability *=  PROBS["gene"][1] * PROBS["trait"][1][person in have_trait]
            elif person in two_genes:
                probability *=  PROBS["gene"][2] * PROBS["trait"][2][person in have_trait]
            else:
                probability *=  PROBS["gene"][0] * PROBS["trait"][0][person in have_trait]
        # If the person has known parent
        else:
            mother = people[person]["mother"]
            father = people[person]["father"]
            prob = 1

            # If the person has no gene
            if person not in one_gene and person not in two_genes:
                for parent in {mother, father}:

                    # If parent has one gene, 50% chance of not passing the gene
                    if parent in one_gene:
                        prob *= 0.5

                    # If parent has two genes, 1% chance of passing a mutated gene (no copy of gene)
                    elif parent in two_genes:
                        prob *= PROBS["mutation"]

                    # If parent has no gene, 99% chance of passing 0 copy of the gene
                    else:
                        prob *= (1 - PROBS["mutation"])

            # If the person has one copy of the gene
            elif person in one_gene:
                prob = 0

                # If both parents have one copy of the gene 
                # 50% chance of passing 1 copy and 50% chance of passing 0 (twice, one for each couple mmother, father)
                if mother in one_gene and father in one_gene:
                    #prob = 2 * (0.5 * (1 - PROBS["mutation"]) * 0.5 * PROBS["mutation"])
                    prob = 0.5 * 0.5 + 0.5 * 0.5
                
                # If one parent has two copies of the gene and the other one has one copy
                # 99% chance of passing the gene and 50% chance of not OR 1% chance of passing one copy and 50% chance not
                elif (mother in one_gene and father in two_genes) or (mother in two_genes and father in one_gene):
                    prob = (1 - PROBS["mutation"]) * 0.5 + PROBS["mutation"] * 0.5
                
                # If both parents have two copies of the gene
                # 99% chance of passing it and 1% chance of not, twice (both parent)
                elif mother in two_genes and father in two_genes:
                    prob = 2*((1 - PROBS["mutation"]) * PROBS["mutation"])

                # If one parent has one copy of the gene and the other has no copy
                # 50% chance of passing it and 99% chance of not OR 50% chance of not passing it and 1% of passing a mutated one
                elif ((mother in one_gene and father not in one_gene and father not in two_genes) or 
                (father in one_gene and mother not in one_gene and mother not in two_genes)):
                    prob = 0.5 * (1 - PROBS["mutation"]) + 0.5 * PROBS["mutation"]

                # If one parent has two copies of the gene and the other has no copy
                # 99% chance of passing it and 99% chance of not passing it OR 1% chance of not passing it and 1% chance of passing it (both mutated)
                elif ((mother in two_genes and father not in one_gene and father not in two_genes) or 
                (father in two_genes and mother not in one_gene and mother not in two_genes)):
                    prob = (1 - PROBS["mutation"]) * (1 - PROBS["mutation"]) + PROBS["mutation"] * PROBS["mutation"]
                
                # If no parent has the gene
                # 99% of not passing it, 1% chance of passing a mutated gene, twice
                else:
                    prob = 2*((1 - PROBS["mutation"]) * PROBS["mutation"])

            # If person has two copies of the gene
            else:
                for parent in {mother, father}:
                    # If parent has one gene : 50% chance of passing it
                    if parent in one_gene:
                        prob *= 0.5 
                    
                    # If parent has two genes : 99% chance of passing it
                    elif parent in two_genes:
                        prob *= (1 - PROBS["mutation"])

                    # If parent has no gene : 1% chance of passing a mutated gene
                    else:
                        prob *= PROBS["mutation"]

            if person in one_gene:
                probability *= PROBS["trait"][1][person in have_trait]
            elif person in two_genes:
                probability *= PROBS["trait"][2][person in have_trait]
            else:
                probability *= PROBS["trait"][0][person in have_trait]

            probability *= prob
        
    return probability




def update(probabilities, one_gene, two_genes, have_trait, p):
    """
    Add to `probabilities` a new joint probability `p`.
    Each person should have their "gene" and "trait" distributions updated.
    Which value for each distribution is updated depends on whether
    the person is in `have_gene` and `have_trait`, respectively.
    """
    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1] += p
        elif person in two_genes:
            probabilities[person]["gene"][2] += p
        else:
            probabilities[person]["gene"][0] += p
        
        if person in have_trait:
            probabilities[person]["trait"][True] += p
        else:
            probabilities[person]["trait"][False] += p


def normalize(probabilities):
    """
    Update `probabilities` such that each probability distribution
    is normalized (i.e., sums to 1, with relative proportions the same).
    """
    for person in probabilities:
        # total_trait : sum of probabilities regarding trait for current person
        total_trait = probabilities[person]["trait"][True] + probabilities[person]["trait"][False]
        probabilities[person]["trait"][True] = probabilities[person]["trait"][True] / total_trait
        probabilities[person]["trait"][False] = probabilities[person]["trait"][False] / total_trait

        # total_gene : sum of probabilities regarding gene for current person
        total_gene = probabilities[person]["gene"][0] + probabilities[person]["gene"][1] + probabilities[person]["gene"][2]
        probabilities[person]["gene"][0] = probabilities[person]["gene"][0] / total_gene
        probabilities[person]["gene"][1] = probabilities[person]["gene"][1] / total_gene
        probabilities[person]["gene"][2] = probabilities[person]["gene"][2] / total_gene

if __name__ == "__main__":
    main()
