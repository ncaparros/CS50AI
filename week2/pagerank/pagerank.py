import os
import random
import re
import sys
import math

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Return a probability distribution over which page to visit next,
    given a current page.

    With probability `damping_factor`, choose a link at random
    linked to by `page`. With probability `1 - damping_factor`, choose
    a link at random chosen from all pages in the corpus.
    """
    transition_model = dict()

    # pages linked in current page
    nexts = corpus.get(page)

    # if there is no link in the current page, equal probability between all pages of the corpus
    if len(nexts) == 0:
        for key in corpus.keys():
            transition_model[key] = 1/len(corpus)
    else:
        # initialized with the equal probability on landing on a random page
        for next_page in nexts:
            transition_model[next_page] = damping_factor/len(nexts)

        # probability of choosing a page linked on the current one
        for page in corpus.keys():
            if page not in transition_model:
                transition_model[page] = 0
            transition_model[page] += (1 - damping_factor)/len(corpus.keys())

    # normalize results
    sum_trans = sum(transition_model.values())

    for key in transition_model.keys():
        transition_model[key] = round((transition_model[key]/sum_trans), 4)

    return transition_model


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    # generate a random index for first page
    index = random.randint(0, len(corpus) - 1)
    page = list(corpus.keys())[index]

    page_ranks = dict()

    # initialize all ranks
    for key in corpus.keys():
        page_ranks[key] = 0

    # first page was chosen
    page_ranks[page] += 1/n

    # n iterations, but first page already chosen
    for i in range(n - 1):
        # get transition model
        trans_model = transition_model(corpus, page, damping_factor)

        page = getRandomPage(trans_model)
        # page was chosen
        page_ranks[page] += 1/n

    return page_ranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pagerank_dict = dict()
    # initialize first ranks, equal probability
    for key in corpus.keys():
        pagerank_dict[key] = round(1 / len(corpus), 4)

    max_value = 1
    while max_value > 0.001:
        max_value = 0
        for key in corpus.keys():
            new_value = 0

            # get pages pointing toward current page
            links_towards = get_pages_pointing_towards(corpus, key)

            for page in links_towards:
                if page != key:
                    new_value += pagerank_dict[page] / len(corpus[page])

            # new rank of the page
            new_value = ((1 - damping_factor)/len(corpus)) + damping_factor * new_value

            # get max value of the change
            if max_value < pagerank_dict[key] - new_value:
                max_value = new_value

            pagerank_dict[key] = new_value

    # normalize results
    total_value = sum(pagerank_dict.values())
    # round results
    for key in pagerank_dict.keys():
        pagerank_dict[key] = round(pagerank_dict[key]/total_value, 4)

    return pagerank_dict


def get_pages_pointing_towards(corpus, page):
    """
    Return the pages pointing towards page
    """
    result = list()
    for key in corpus.keys():
        if page in corpus[key]:
            result.append(key)
    return result


def getRandomPage(transition_model):
    """
    Return a random page knowing a transition model
    """
    rand = random.randint(0, math.floor(sum(transition_model.values())*100))
    cell = 0
    for page in transition_model.items():
        cell += page[1]*100
        if rand <= cell:
            return page[0]

    print(rand)
    print(round(sum(transition_model.values())*100))
    print(cell)


if __name__ == "__main__":
    main()
