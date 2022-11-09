
from utils import logx

log = logx.get_logger('census_lk_pdf_parser.parse')

def parse_int(x):
    if str(x) == 'nan':
        return 0
    x = str(x).replace(',', '')
    return (int)(x)

def parse_gnd_num(x):
    if str(x) == 'nan':
        return '-'
    return str(x)


def parse_row(row):
    print(row)
    if len(row) == 8:
        if str(row[5]) == 'nan':
            if str(row[3]) == 'nan':
                return dict(
                    region_name=row[0],
                    gnd_num=parse_gnd_num(row[1]),
                    total=parse_int(row[2]),
                    employed=0,
                    unemployed=0,
                    economically_not_active=parse_int(row[4]),
                )
            else:
                row2_splits = row[3].split(' ')
                return dict(
                    region_name=row[0],
                    gnd_num=parse_gnd_num(row[1]),
                    total=parse_int(row[2]),
                    employed=parse_int(row2_splits[0]),
                    unemployed=parse_int(row2_splits[1]),
                    economically_not_active=parse_int(row[4]),
                )
        else:
            return dict(
                region_name=row[0],
                gnd_num=parse_gnd_num(row[1]),
                total=parse_int(row[2]),
                employed=parse_int(row[3]),
                unemployed=parse_int(row[4]),
                economically_not_active=parse_int(row[5]),
            )

    raise Exception('Unknown format')
