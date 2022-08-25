import tabula
from utils import logx

log = logx.get_logger('census_lk_pdf_parser.pdf_to_tsv')


def pdf_to_tsv(pdf_file):
    log.info(f'Parsing {pdf_file}...')
    names = [str(i) for i in range(8)]
    dfs = tabula.read_pdf(
        pdf_file,
        pages="1,2,3",
        multiple_tables=False,
        pandas_options=dict(names=names),
    )
    xlsx_file = pdf_file + '.xlsx'
    dfs[0].to_excel(xlsx_file, index=False)


if __name__ == '__main__':
    pdf_to_tsv('data/education.pdf')
