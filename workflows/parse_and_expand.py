import sys

from utils import logx

from census_lk_pdf_parser import expand, parse

log = logx.get_logger('census_lk_pdf_parser')
CONFIG_LIST = [
    dict(
        pdf_file='data/economic-activity.pdf',
        has_gnd_num=True,
        field_name_list=[
            'total',
            'employed',
            'unemployed',
            'economically_not_active',
        ],
    ),
    dict(
        pdf_file='data/education.pdf',
        has_gnd_num=False,
        field_name_list=[
            'total',
            'primary',
            'secondary',
            'gce_ordinary_level',
            'gce_advanced_level',
            'degree_and_above',
            'no_schooling',
        ],
    ),
]

if __name__ == '__main__':
    prod_mode = len(sys.argv) > 1 and sys.argv[1] == '--prod'
    log.info(f'{prod_mode=}')
    pages = 'all' if prod_mode else '1'
    log.info(f'{pages=}')

    for config in CONFIG_LIST:
        expand.expand(
            parse.parse(
                config['pdf_file'],
                config['has_gnd_num'],
                config['field_name_list'],
                pages,
            )
        )
        if not prod_mode:
            break
