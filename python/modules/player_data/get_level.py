from modules.core.plugin_client import stats

def get_level(skill):
    """
    Retrieve the player's skill level(s) from stats.
    
    Args:
        skill (str or list): Single skill name (e.g., 'magic') or list of skill names (e.g., ['woodcutting', 'magic']).
    
    Returns:
        int or dict: Single level as int, or dict of {skill: level} for multiple.
    
    Raises:
        ValueError: If skill is invalid or stats fetch fails.
    """
    stats_data = stats()['data']
    if not stats_data:
        raise ValueError("Failed to fetch stats data")
    
    def normalize_skill(s):
        return s.capitalize()
    
    if isinstance(skill, str):
        norm_skill = normalize_skill(skill)
        if norm_skill not in stats_data:
            raise ValueError(f"Skill '{skill}' not found in stats")
        return int(stats_data[norm_skill]['level'])
    
    elif isinstance(skill, list):
        levels = {}
        for s in skill:
            norm_skill = normalize_skill(s)
            if norm_skill not in stats_data:
                raise ValueError(f"Skill '{s}' not found in stats")
            levels[s] = int(stats_data[norm_skill]['level'])
        return levels
    
    else:
        raise ValueError("skill must be a string or list of strings")
    

# Example call for single skill
# level = get_level('magic')
# print(level)
# returns 59

# Example call for multiple skills
# levels = get_level(['woodcutting', 'magic', 'defence', 'strength', 'prayer'])
# print(levels)
# returns {'woodcutting': 1, 'magic': 59, 'defence': 1, 'strength': 30, 'prayer': 80}