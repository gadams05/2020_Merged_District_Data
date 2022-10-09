population_cols = {
    'total': ['P1_001N'],
    'white': ['P1_003N'],
    'black': ['P1_004N'],
    'native': ['P1_005N'],
    'asian': ['P1_006N'],
    'hawaiian': ['P1_007N'],
    'other': ['P1_008N'],
    'latino': ['P2_002N']
}

population_colors = {
    'total': '#000000',
    'white': '#000000',
    'black': '#000000',
    'native': '#000000',
    'asian': '#000000',
    'hawaiian': '#000000',
    'other': '#000000',
    'latino': '#000000',
}

def get_census_value(key, data):

    if key not in population_cols:
        print(f'missing census key {key} in definition???')
        return 0

    total = 0
    for col in population_cols[key]:
        if col in data:
            total += data[col]
        else:
            print(f'missing census key {key} in data')

    #print(f'census {key} {total}')
    return total

