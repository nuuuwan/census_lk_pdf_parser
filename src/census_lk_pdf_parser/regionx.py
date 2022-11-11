from gig import ent_types, ents
from gig.ent_types import ENTITY_TYPE
from utils import logx

log = logx.get_logger('census_lk_pdf_parser.regionx')


def get_district_id(region_id):
    return region_id[:5]


def get_dsd_id(region_id):
    return region_id[:7]


def get_next_region_type(previous_region_type):
    if previous_region_type == ENTITY_TYPE.COUNTRY:
        return ENTITY_TYPE.DISTRICT

    if previous_region_type == ENTITY_TYPE.DISTRICT:
        return ENTITY_TYPE.DSD

    if previous_region_type == ENTITY_TYPE.DSD:
        return ENTITY_TYPE.GND

    return None


def get_unvisited_region_id(candidate_regions, visited_region_id_list):
    for candidate_region in candidate_regions:
        candidate_region_id = candidate_region['id']
        if candidate_region_id in visited_region_id_list:
            continue
        return candidate_region_id
    return None


def get_region_id_inner(
    data, previous_known_region_id, visited_region_id_list, min_fuzz_ratio
):
    region_name = data['region_name']

    # CASE 1: region_type == 'country'
    if region_name == 'Sri Lanka':
        return 'LK'

    if previous_known_region_id:
        previous_region_type = ent_types.get_entity_type(
            previous_known_region_id
        )

    if previous_region_type:
        candidate_region_type = get_next_region_type(previous_region_type)

    # CASE 2: previous_region_type in ['country', 'district', 'dsd']
    if candidate_region_type:
        candidate_regions = ents.get_entities_by_name_fuzzy(
            region_name,
            filter_entity_type=candidate_region_type,
            filter_parent_id=previous_known_region_id,
            limit=5,
            min_fuzz_ratio=min_fuzz_ratio,
        )
        return get_unvisited_region_id(
            candidate_regions, visited_region_id_list
        )

    # CASE 3: previous_region_type = 'gnd'
    # CASE 3a: Next row is a gnd
    dsd_id = get_dsd_id(previous_known_region_id)
    candidate_regions = ents.get_entities_by_name_fuzzy(
        region_name,
        filter_entity_type='gnd',
        filter_parent_id=dsd_id,
        limit=5,
        min_fuzz_ratio=min_fuzz_ratio,
    )
    region_id_case3a = get_unvisited_region_id(
        candidate_regions, visited_region_id_list
    )
    if region_id_case3a:
        return region_id_case3a

    # CASE 3b: Next row is NOT a gnd
    candidate_regions = ents.get_entities_by_name_fuzzy(
        region_name,
        filter_entity_type=None,
        filter_parent_id=None,
        limit=5,
        min_fuzz_ratio=min_fuzz_ratio,
    )

    for candidate_region in candidate_regions:
        candidate_region_id = candidate_region['id']
        if candidate_region_id in visited_region_id_list:
            continue
        candidate_region_type = ent_types.get_entity_type(candidate_region_id)

        if candidate_region_type == ENTITY_TYPE.DISTRICT:
            return candidate_region_id

        elif candidate_region_type == ENTITY_TYPE.DSD:
            if all(
                [
                    get_district_id(candidate_region_id)
                    == get_district_id(previous_known_region_id),
                    get_dsd_id(candidate_region_id)
                    != get_dsd_id(previous_known_region_id),
                ]
            ):
                return candidate_region_id

        # candidate_region_type == ENTITY_TYPE.GND
        else:
            if get_dsd_id(candidate_region_id) == get_dsd_id(
                previous_known_region_id
            ):
                return candidate_region_id
    return None


def get_region_id(data, previous_known_region_id, visited_region_id_list):
    for min_fuzz_ratio in [90, 80]:
        region_id = get_region_id_inner(
            data,
            previous_known_region_id,
            visited_region_id_list,
            min_fuzz_ratio,
        )
        if region_id:
            return region_id
    return None


if __name__ == '__main__':
    candidate_regions = ents.get_entities_by_name_fuzzy(
        'Medagama III',
        filter_entity_type='gnd',
        filter_parent_id='LK-1224',
        limit=10,
        min_fuzz_ratio=60,
    )
    for candidate_region in candidate_regions:
        print()
        print(candidate_region)
    #
    # region_id = get_region_id_inner(
    #     dict(region_name='Kolonnawa'),
    #     previous_known_region_id='LK-1103175',
    #     visited_region_id_list=[],
    #     min_fuzz_ratio=90,
    # )
    # print(region_id)
