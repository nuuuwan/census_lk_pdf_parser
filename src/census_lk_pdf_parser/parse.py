import tabula
from utils import TSVFile, logx
from utils.cache import cache

log = logx.get_logger('census_lk_pdf_parser.parse')
DELIM = '___'
N_HEADER = 5


def parse_int(x):
    if str(x) == 'nan':
        return 0
    x = str(x).replace(',', '')
    return (int)(x)


def parse_gnd_num(x):
    if str(x) == 'nan':
        return '-'
    return str(x)


def extract_cells(row):
    row[0] = str(row[0]).replace(' ', '_')
    row[1] = str(row[1]).replace(' ', '_')
    str_cell_list = list(
        map(
            lambda x: str(x).replace(' ', DELIM),
            row,
        )
    )
    return DELIM.join(str_cell_list).split(DELIM)


def validate(row, cells, d, field_name_list):
    total = d['total']
    total2 = sum(
        list(
            map(
                lambda field_name: d[field_name],
                field_name_list[1:],
            )
        )
    )
    assert total == total2, row


def parse_row(row, has_gnd_num, field_name_list):
    cells = extract_cells(row)
    region_name = cells[0].replace('_', ' ')

    d = {}
    d['region_name'] = region_name
    offset = 0
    if has_gnd_num:
        d['gnd_num'] = parse_gnd_num(cells[1].replace('_', ''))
        offset = 1

    for i, field_name in enumerate(field_name_list):
        d[field_name] = parse_int(cells[i + offset + 1])

    validate(row, cells, d, field_name_list)

    return d


@cache('get_rows', 86400 * 1000)
def get_rows(pdf_file, pages):
    names = [str(i) for i in range(8)]
    df = tabula.read_pdf(
        pdf_file,
        pages=pages,
        multiple_tables=False,
        pandas_options=dict(names=names),
    )[0]

    rows = df.values.tolist()[N_HEADER:]
    n = len(rows)
    log.info(f'Extracted {n} rows from pages {pages} of {pdf_file}')
    return rows


def parse(pdf_file, has_gnd_num, field_names, pages):
    rows = get_rows(pdf_file, pages)
    data_list = []
    for i_row, row in enumerate(rows):
        try:
            data = parse_row(row, has_gnd_num, field_names)
        except BaseException:
            log.error(row)
        data_list.append({'i_row': i_row} | data)

    tsv_file = pdf_file[:-4] + '.tsv'
    TSVFile(tsv_file).write(data_list)
    n_data_list = len(data_list)
    log.info(f'Wrote {n_data_list} rows to {tsv_file}')

    return tsv_file
