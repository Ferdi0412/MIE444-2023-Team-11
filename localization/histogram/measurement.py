import numpy as np

def measure(current_block: int, probs: np.array, map: np.array):
    """Once current_block configuration found, update probabilities. If probs is None, create matrix using all 1s."""
    probs = probs or np.ones(map.shape)

    # Sensor readings -> Instead of 0 and 1, use these values (error???)
    p_hit  = 0.6
    p_miss = 0.2

    ## Initialize update matrix of "zeros" -> Using ones times p_miss to account for error????
    p_update = np.ones(map.shape, np.float64) * p_miss

    ## Set all positions that could be the current position to p_hit
    p_update[map == current_block] = p_hit

    ## Reset all positions within walls to 0, because these can NEVER occur
    p_update[map == 4] = 0

    ## Update with existing/previous probabilities
    p_update = np.multiply(p_update, probs)
    #|- p_update *= probs

    ## Normalize probabilities
    p_update /= np.sum(p_update)

    return p_update
