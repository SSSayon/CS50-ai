import os
import random
import re
import sys
import copy

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
    a set of all other pages in the corpus that are linked to by the page.
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
    if not corpus[page]:
        return dict.fromkeys(corpus.keys(), 1 / len(corpus))
    
    result = dict.fromkeys(corpus.keys(), (1 - damping_factor) / len(corpus))
    num_pages = len(corpus[page])
    for linked_page in corpus[page]:
        result[linked_page] += damping_factor / num_pages

    return result


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    pageranks = dict.fromkeys(corpus.keys(), 0)

    curr_page = random.choice(list(corpus.keys()))
    pageranks[curr_page] += 1

    for i in range(n - 1):
        transition = transition_model(corpus, curr_page, damping_factor)
        keys = list(transition.keys())
        values = list(transition.values())

        curr_page = random.choices(keys, values, k=1)[0]
        pageranks[curr_page] += 1

    for page in pageranks:
        pageranks[page] /= n

    return pageranks


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    corpus_ = copy.deepcopy(corpus)
    for page in corpus_:
        if not corpus_[page]:
            corpus_[page] = corpus_.keys()
    
    N = len(corpus_)
    pageranks = dict.fromkeys(corpus_.keys(), 1 / N)

    def pages_links_to(page) -> set:
        pages = set()
        for _page in corpus_:
            if page in corpus_[_page]:
                pages.add(_page)

        return pages

    def pagerank(page) -> float:
        return ((1 - damping_factor) / N + 
                damping_factor * sum([pageranks[_page] / len(corpus_[_page]) for _page in pages_links_to(page)]))

    flag = False
    while not flag:
        flag = True
        new_pageranks = dict()
        for page in pageranks:
            new_pageranks[page] = pagerank(page)
            if (new_pageranks[page] - pageranks[page] > 0.001 or 
                    pageranks[page] - new_pageranks[page] > 0.001):
                flag = False
        pageranks = new_pageranks

    return pageranks


if __name__ == "__main__":
    main()
