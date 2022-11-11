from gig import ent_types, ents
from gig.ent_types import ENTITY_TYPE
from utils import TSVFile, logx

log = logx.get_logger('census_lk_pdf_parser.expand')


def get_region_id(data, previous_known_region_id, min_fuzz_ratio):
    region_name = data['region_name']
    if region_name == 'Sri Lanka':
        return 'LK'

    region_id = None
    candidate_region_type = None
    if previous_known_region_id:
        previous_region_type = ent_types.get_entity_type(
            previous_known_region_id
        )
        if previous_region_type == ENTITY_TYPE.COUNTRY:
            candidate_region_type = ENTITY_TYPE.DISTRICT

        elif previous_region_type == ENTITY_TYPE.DISTRICT:
            candidate_region_type = ENTITY_TYPE.DSD

        elif previous_region_type == ENTITY_TYPE.DSD:
            candidate_region_type = ENTITY_TYPE.GND

    candidate_regions = ents.get_entities_by_name_fuzzy(
        region_name,
        filter_entity_type=candidate_region_type,
        filter_parent_id=None,
        limit=5,
        min_fuzz_ratio=min_fuzz_ratio,
    )

    if candidate_region_type:
        if candidate_regions:
            return candidate_regions[0]['id']
    else:
        for candidate_region in candidate_regions:
            candidate_region_id = candidate_region['id']
            candidate_region_type = ent_types.get_entity_type(
                candidate_region_id
            )

            if candidate_region_type == ENTITY_TYPE.DISTRICT:
                return candidate_region_id

            elif candidate_region_type == ENTITY_TYPE.DSD:
                if all(
                    [
                        candidate_region_id[:5]
                        == previous_known_region_id[:5],
                        candidate_region_id[:7]
                        != previous_known_region_id[:7],
                    ]
                ):
                    return candidate_region_id

            # candidate_region_type == ENTITY_TYPE.GND
            else:
                if (
                    candidate_region_id[:7]
                    == previous_known_region_id[:7]
                ):
                    return candidate_region_id
    return region_id

def expand_row(data, previous_known_region_id):
    for min_fuzz_ratio in [90]:
        region_id = get_region_id(data, previous_known_region_id, min_fuzz_ratio)
        if region_id:
            break

    return {'region_id': region_id} | data


def expand(tsv_file):
    log.info(f'Expanding {tsv_file}...')
    data_list = TSVFile(tsv_file).read()

    expanded_data_list = []
    previous_known_region_id = None
    n_missing_ids = 0
    n = len(data_list)
    for data in data_list:
        expanded_data = expand_row(data, previous_known_region_id)
        # log.debug(expanded_data['region_name'] + ' -> ' + str(expanded_data['region_id']))
        expanded_data_list.append(expanded_data)
        region_id = expanded_data['region_id']
        if not region_id:
            n_missing_ids += 1
            # log.debug(expanded_data)
        if region_id:
            previous_known_region_id = region_id

    log.warn(f'IDs could not be found for {n_missing_ids}/{n} Regions.')

    expanded_tsv_file = tsv_file[:-4] + '.expanded.tsv'
    TSVFile(expanded_tsv_file).write(expanded_data_list)
    log.info(f'Wrote {expanded_tsv_file}')
