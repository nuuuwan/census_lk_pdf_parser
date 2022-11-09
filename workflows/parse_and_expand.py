from census_lk_pdf_parser import (expand, parse, parse_economic_activity,
                                  parse_education)

if __name__ == '__main__':
    for pdf_file, parse_row in [
        ['data/economic-activity.pdf', parse_economic_activity.parse_row],
        ['data/education.pdf', parse_education.parse_row],
    ]:
        expand.expand(parse.parse(pdf_file, parse_row))
