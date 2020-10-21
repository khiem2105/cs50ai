import os
import random
import re
import sys

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
    model = {}
    num_links = len(corpus[page]) #Number of page linked by {page}
    total_pages = len(corpus) #Total number of page
    prob = (1 - damping_factor)/total_pages #Probability of chosing a random page among all pages in the corpus
    model[page] = (1-damping_factor)/prob
    links = corpus[page]
    for link in links:
        model[link] = prob + damping_factor/num_links
    for not_link in corpus:
        if not_link in model:
            continue
        model[not_link] = prob    
    return model    
    # raise NotImplementedError


def sample_pagerank(corpus, damping_factor, n):
    """
    Return PageRank values for each page by sampling `n` pages
    according to transition model, starting with a page at random.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = {}
    #Initialize rank of each page in the corpus to 0.0
    for page in corpus:
        page_rank[page] = 0
    sample = random.choice(list(corpus))
    page_rank[sample] += 1/n
    for i in range(1, n + 1):
        model = transition_model(corpus, sample, damping_factor)
        next_pages = []
        probs = []
        for key, value in model.items():
            next_pages.append(key)
            probs.append(value)
        sample = random.choices(next_pages, weights = probs, k = 1)[0]
        page_rank[sample] += 1/n
    return page_rank        
    # raise NotImplementedError


def iterate_pagerank(corpus, damping_factor):
    """
    Return PageRank values for each page by iteratively updating
    PageRank values until convergence.

    Return a dictionary where keys are page names, and values are
    their estimated PageRank value (a value between 0 and 1). All
    PageRank values should sum to 1.
    """
    page_rank = {}
    total_pages = len(corpus)
    accuracies = {}

    #Initialize each page rank to 1/N
    for page in corpus:
        page_rank[page] = 1/total_pages
        accuracies[page] = 1
    while test_accuracy(accuracies) is False:
        current_state = page_rank
        new_state = {}
        for page in corpus:
            new_state[page] = 0
        for page in corpus:
            for other_page in corpus:
                if other_page == page:
                    continue
                if len(corpus[other_page]) == 0:
                    new_state[page] += damping_factor * (current_state[other_page]/total_pages)
                elif page in corpus[other_page]:
                    new_state[page] += damping_factor * (current_state[other_page]/len(corpus[other_page]))
            new_state[page] += (1 - damping_factor)/total_pages
            accuracies[page] = abs(current_state[page] - new_state[page])
        page_rank = new_state                 
    # raise NotImplementedError
    return page_rank

def test_accuracy(accuracies):
    for accuracy in accuracies.values():
        if accuracy > 0.001:
            return False
    return True        

if __name__ == "__main__":
    main()
