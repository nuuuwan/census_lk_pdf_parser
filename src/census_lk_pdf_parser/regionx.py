from gig import ent_types, ents
from gig.ent_types import ENTITY_TYPE


def get_region_id(data, previous_known_region_id, visited_region_id_list, min_fuzz_ratio):
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
                        candidate_region_id[:5]
                        == previous_known_region_id[:5],
                        candidate_region_id[:7]
                        != previous_known_region_id[:7],
                    ]
                ):
                    return candidate_region_id

            # candidate_region_type == ENTITY_TYPE.GND
            else:
                if candidate_region_id[:7] == previous_known_region_id[:7]:
                    return candidate_region_id
    return region_id
