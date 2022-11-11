from gig import ent_types, ents
from gig.ent_types import ENTITY_TYPE
from utils import logx
from utils.cache import cache

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



@cache('get_region_id', 86400 * 1000)
def get_region_id_inner(
    data, previous_known_region_id, visited_region_id_list, min_fuzz_ratio
):
    region_name = data['region_name']
    if region_name == 'Sri Lanka':
        return 'LK'

    region_id = None
    candidate_region_type = None
    if previous_known_region_id:
        previous_region_type = ent_types.get_entity_type(
            previous_known_region_id
        )
        candidate_region_type = get_next_region_type(previous_region_type)

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
            if candidate_region_id in visited_region_id_list:
                continue

            candidate_region_type = ent_types.get_entity_type(
                candidate_region_id
            )

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
    return region_id


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
        'Meerigama',
        filter_entity_type=None,
        filter_parent_id=None,
        limit=5,
        min_fuzz_ratio=80,
    )
    for candidate_region in candidate_regions:
        print()
        print(candidate_region)
