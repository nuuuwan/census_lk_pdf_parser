from census_lk_pdf_parser.expand import expand
from census_lk_pdf_parser.parse import parse

if __name__ == '__main__':
    for pdf_file in ['data/education.pdf']:
        expand(parse(pdf_file))
