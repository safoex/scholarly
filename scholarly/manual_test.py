import scholarly
from ruamel import yaml
import argparse


class AcademicPagesExporter:
    author_query_path = "scholar_query"
    author_id_path = "scholar_id"
    save_dir_path = "_publications"
    google_scholar_citedby_url = "https://scholar.google.com/scholar?oi=bibs&hl=en&cites="
    markdown_with_abstract = \
        """
        <details>
            <summary> <b>"%s"</b>, %s, <i>%s</i>\n%s
            </summary>
            
        %s
        </details>
        """
    publications_page_prefix = \
"""---
layout: archive
title: "Publications"
permalink: /publications/
author_profile: true
---
"""
    publications_path_prefix = "_pages/publications/"
    page_path = "_pages/publications.md"
    config_path = "_config.yml"
    markdown_without_abstract = "<b>\"%s\"</b>, %s, <i>%s</i>\n%s"

    test_dict = {'author': {'name': 'Evgenii Safronov', 'scholar_query': 'Evgenii Safronov, IIT'}}

    def __init__(self, path_to_site=None):
        if path_to_site:
            with open(path_to_site + self.config_path, 'r') as config_yaml_file:
                cfg = yaml.safe_load(config_yaml_file)
        else:
            cfg = self.test_dict

        self.path_to_site = path_to_site or ''
        author_info = cfg['author']
        self.author_query = author_info[self.author_query_path]
        self.name = author_info['name'].strip()
        if self.author_id_path in author_info:
            self.author_id = author_info[self.author_id_path]
        # scholarly.use_proxy(http='socks5://181.101.220.136:1080',
        #                     https='socks5://181.101.220.136:1080')

    def make_publication_markdown_from_scholar(self, pub):
        title = pub['bib']['title']
        abstract = pub['bib']['abstract'] if 'abstract' in pub['bib'] else ""

        year = ""
        if 'year' in pub['bib']:
            year = str(pub['bib']['year'])

        venue = ""
        if 'journal' in pub['bib']:
            if 'year' in pub['bib']:
                venue = str(pub['bib']['year']) + ", "
            venue += pub['bib']['journal']
        elif 'conference' in pub['bib']:
            venue = pub['bib']['conference']

        def emph_author(name):
            if name != self.name:
                return name
            else:
                return "<ins>" + name + "</ins>"

        authors = ', '.join([emph_author(i.strip()) for i in pub['bib']['author'].split(' and ')])

        publisher = ""
        if 'publisher' in pub['bib']:
            publisher = pub['bib']['publisher']
        elif 'journal' in pub['bib']:
            publisher = venue

        def make_link_html(text_, href):
            return "<a href=\"%s\">%s</a>" % (href, text_)

        cited_by = ""
        if 'citedby' in pub:
            cited_by = "cited by: " + make_link_html(pub['citedby'],
                                                     self.google_scholar_citedby_url + pub['id_scholarcitedby'])

        if 'url' in pub['bib']:
            link = 'paper at ' + make_link_html(publisher if len(publisher) else 'page', pub['bib']['url'])
        else:
            link = ""

        read_pdf = ""
        if 'eprint' in pub['bib']:
            read_pdf = "read " + make_link_html('pdf', pub['bib']['eprint'])

        extra = ""
        if len(cited_by):
            extra += cited_by
            if len(link) or len(read_pdf):
                extra += ', '

        if len(link):
            extra += link
            if len(read_pdf):
                extra += ', '

        if len(read_pdf):
            extra += read_pdf

        if len(extra):
            extra = ', ' + extra

        if len(abstract):
            text = self.markdown_with_abstract % (title, authors, venue, extra, abstract)
        else:
            text = self.markdown_without_abstract % (title, authors, extra, venue)

        def filter_out(strs):
            return [''.join(c for c in s if c.isalnum()) for s in strs]

        file_name = '-'.join(filter_out(venue.split())) + '-' + '-'.join(filter_out(title.split()[:3])) + '.md'

        text += "\n\n{% include_relative publications/" + file_name + " %}\n"

        return file_name, text

    def test(self):
        search_query = scholarly.search_author(self.author_query)
        author = next(search_query).fill()

        for publ in author.publications[:1]:
            print(self.make_publication_markdown_from_scholar(publ.fill().__dict__)[1])

    def update_publications(self):
        search_query = scholarly.search_author(self.author_query)
        author = next(search_query).fill()

        text = self.publications_page_prefix
        text += '\n'

        for publ in author.publications:
            p = publ.fill()
            print(p)
            filename, md = self.make_publication_markdown_from_scholar(p.__dict__)

            text += md
            text += '\n'

            filepath = self.path_to_site + self.publications_path_prefix + filename
            with open(filepath, "a+") as _:
                pass

        with open(self.path_to_site + self.page_path, 'w+') as page:
            print(text, file=page)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help="path to github forms website root", type=str, default='')
    parser.add_argument('--test', help="test locally")
    args = parser.parse_args()

    path = args.path

    test = AcademicPagesExporter(None if args.test else path)
    test.update_publications()
