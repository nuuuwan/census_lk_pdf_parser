import tabula
from gig import ents
from utils import TSVFile, logx

log = logx.get_logger('census_lk_pdf_parser.pdf_to_tsv')


def get_region_ids(region_name):
    region_ids = []
    return ','.join(region_ids)


def parse_row(row):
    if len(row) == 8:
        if str(row[-1]) == 'nan':
            gce_ordinary_level, gce_advanced_level = row[4].split(' ')
            return dict(
                region_name=row[0],
                total=row[1],
                primary=row[2],
                secondary=row[3],
                gce_ordinary_level=gce_ordinary_level,
                gce_advanced_level=gce_advanced_level,
                degree_and_above=row[5],
                no_schooling=row[6],
            )

        return dict(
            region_name=row[0],
            total=row[1],
            primary=row[2],
            secondary=row[3],
            gce_ordinary_level=row[4],
            gce_advanced_level=row[5],
            degree_and_above=row[6],
            no_schooling=row[7],
        )

    raise Exception('Unknown format')


def parse(pdf_file):
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


def expand_row(data):
    regions = ents.get_entities_by_name_fuzzy(
        data['region_name'],
        filter_entity_type=None,
        filter_parent_id=None,
        limit=5,
        min_fuzz_ratio=95,
    )
    region_ids = list(
        filter(
            lambda region: region[:3] == 'LK-',
            list(
                map(
                    lambda region: region['id'],
                    regions,
                )
            ),
        )
    )
    data['candidate_region_ids'] = ';'.join(region_ids)
    return data


def expand(tsv_file):
    data_list = TSVFile(tsv_file).read()
    expanded_data_list = list(map(expand_row, data_list))
    expanded_tsv_file = tsv_file[:-4] + '.expanded.tsv'
    TSVFile(expanded_tsv_file).write(expanded_data_list)
    log.info(f'Wrote {expanded_tsv_file}')


if __name__ == '__main__':
    expand(parse('data/education.pdf'))
