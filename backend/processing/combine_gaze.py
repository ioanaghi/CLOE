import math

def is_valid_eye(point, validity):
    return(
        validity == 1
        and all(math.isfinite(value) for value in point)
    )

def combine_gaze(left,right,left_valid,right_valid):
    left_ok = is_valid_eye(left, left_valid)
    right_ok = is_valid_eye(right, right_valid)

    if left_ok and right_ok:
        return (
            (left[0] + right[0]) / 2,
            (left[1] + right[1]) / 2
        )

    if left_ok:
        return left

    if right_ok:
        return right
        
    return None