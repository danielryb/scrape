import requests
from bs4 import BeautifulSoup, NavigableString
import re
from duckduckgo_search import DDGS
import time

build_dir = "./build"

url = "https://www.ign.com/articles/best-n64-games"

def generate_search_markdown(text : str) -> str:
    global build_dir

    suffix = '/search/%s.md' % (text.replace(' ', '-'))
    file_name = build_dir + suffix
    print(file_name)
    with open(file_name, "w+") as f:
        print('# SEARCH RESULTS (%s)\n---\n' % (text), file=f)

        ddgs = DDGS()

        results = ddgs.images("%s n64 screenshot" % (text), max_results=3)
        for result in results:
            print('\n![alt text](%s "%s")\n' % (result["image"], result['title']),
                  file=f)

        results = ddgs.text(text, max_results=10)
        for result in results:
            print(
                '## [%s](%s)\n' \
                '%s\n' \
                '\n---\n' \
                    % (
                        result['title'],
                        result['href'],
                        result['body']
                    ),
                file=f)

    time.sleep(2)

    return '.%s' % (suffix)

include_data = False
def to_markdown(soup : BeautifulSoup):
    global include_data

    res : list[str] = list()

    text : str = soup.text
    try:
        match soup.attrs['data-cy']:
            case "progressive-image":
                if include_data and 'object-image' in soup.attrs['class']:
                    res.append('\n![alt text](')
                    res.append(soup.attrs['src'])
                    res.append(' "')
                    res.append(text)
                    res.append('")\n')
            case "embed-producerLink":
                if include_data:
                    res.append('\n- **Producer:** ')
                    res.append(text)
                    res.append('\n')
            case "object-publication-time":
                if include_data:
                    res.append('\n- **Release date:** ')
                    res.append(text)
                    res.append('\n')
            case "title2":
                if re.match("(\d+)\. *", text) != None:
                    include_data = True

                    res.append('\n---\n## ')
                    res.append(text)

                    # Add link to search results
                    search = text.split(' ', 1)[1]
                    link = generate_search_markdown(search)
                    # link = 'https://www.google.com'

                    res.append(' [SEARCH](')
                    res.append(link)
                    res.append(')')

                    res.append('\n')
                else:
                    include_data = False
            case "paragraph":
                if include_data:
                    res.append('\n')
                    res.append(text)
                    res.append('\n')
    except KeyError:
        pass

    for content in soup.children:
        if isinstance(content, NavigableString):
            continue
        res.append(to_markdown(content))

    return ''.join(res)

def generate_scrap_markdown() -> str:
    global build_dir
    global url

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    r = requests.get(url, headers=headers)

    soup = BeautifulSoup(r.content, 'html.parser')
    # f.write(r.content)

    article_soup = soup.find("section", {"class": "article-page"})

    # print(article_soup.prettify(), file=f)

    print(len(article_soup.contents))

    file_name = '%s/scrap.md' % (build_dir)
    with open(file_name, "w") as md_f:
        print('# Best N64 games ([scrapped](%s))\n' % (url), file=md_f)
        print(to_markdown(article_soup), file=md_f)
        print('\n---\n## ', file=md_f)

    return './scrap.md'

def generate_markdown_website():
    file_name = '%s/start.md' % (build_dir)
    with open(file_name, "w") as md_f:
        link = generate_scrap_markdown()
        # link = "./scrap.md"
        print('# N64\n---\n', file=md_f)
        print(
            "The Nintendo 64 (N64) is a home video game console developed and marketed by Nintendo. " \
            "It was released in Japan on June 23, 1996, in North America on September 29, 1996, " \
            "and in Europe and Australia on March 1, 1997. " \
            "The successor to the Super Nintendo Entertainment System, it was the last major home console " \
            "to use ROM cartridges as its primary storage format. " \
            "As a fifth-generation console, the Nintendo 64 primarily competed with Sony's PlayStation and " \
            "the Sega Saturn.\n",
            file=md_f)
        print("\n[Top games for N64](%s)\n---\n" % (link), file=md_f)

generate_markdown_website()