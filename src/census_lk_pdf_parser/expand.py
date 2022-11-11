from gig import ent_types
from utils import TSVFile, logx

from census_lk_pdf_parser import regionx

log = logx.get_logger('census_lk_pdf_parser.expand')


def expand_row(data, previous_known_region_id, visited_region_id_list):
    region_id = regionx.get_region_id(
        data, previous_known_region_id, visited_region_id_list
    )
    region_type = ent_types.get_entity_type(region_id) if region_id else None
    return data | dict(
        region_id=region_id,
        region_type=region_type,
    )


def expand(tsv_file):
    log.info(f'Expanding {tsv_file}...')
    data_list = TSVFile(tsv_file).read()

    expanded_data_list = []
    previous_known_region_id = None
    n_missing_ids = 0
    n = len(data_list)
    visited_region_id_list = []
    for i, data in enumerate(data_list):
        region_name = data['region_name']
        if region_name == 'Sri Lnka':
            data['region_name'] = 'Sri Lanka'

        if (i + 1) % 1_000 == 0:
            log.debug(f'{i + 1}/{n} {region_name}')
        expanded_data = expand_row(
            data, previous_known_region_id, visited_region_id_list
        )
        expanded_data_list.append(expanded_data)
        region_id = expanded_data['region_id']

        if region_id:
            previous_known_region_id = region_id
            visited_region_id_list.append(region_id)
        else:
            n_missing_ids += 1

    log.warn(f'IDs could not be found for {n_missing_ids}/{n} Regions.')
    expanded_tsv_file = tsv_file[:-4] + '.expanded.tsv'
    TSVFile(expanded_tsv_file).write(expanded_data_list)
    log.info(f'Wrote {expanded_tsv_file}')
