from census_lk_pdf_parser import expand, parse

CONFIG_LIST = [
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
]

if __name__ == '__main__':
    for config in CONFIG_LIST:
        expand.expand(
            parse.parse(
                config['pdf_file'],
                config['has_gnd_num'],
                config['field_name_list'],
            )
        )
