
from utils import logx

log = logx.get_logger('census_lk_pdf_parser.parse')


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
