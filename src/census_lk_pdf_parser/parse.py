import os

import tabula
from utils import TSVFile, logx

log = logx.get_logger('census_lk_pdf_parser.parse')


def parse(pdf_file, parse_row):
    tsv_file = pdf_file[:-4] + '.tsv'
    log.warn(f'{tsv_file} already exits')

    log.info(f'Parsing {pdf_file}...')
    names = [str(i) for i in range(8)]
    df = tabula.read_pdf(
        pdf_file,
        pages="all",
        multiple_tables=False,
        pandas_options=dict(names=names),
    )[0]

    data_list = []
    N_HEADER = 5
    for row in df.values.tolist()[N_HEADER:]:
        data = parse_row(row)
        data_list.append(data)

    tsv_file = pdf_file[:-4] + '.tsv'
    TSVFile(tsv_file).write(data_list)
    n_data_list = len(data_list)
    log.info(f'Wrote {n_data_list} rows to {tsv_file}')

    return tsv_file
