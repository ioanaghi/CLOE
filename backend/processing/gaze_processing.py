import math

def is_valid_eye(point,validity):
    if validity !=1:
        return False

    if len(point) != 2:
        return False

    x,y = point

    return math.isfinite(x) and math.isfinite(y)


def combine_gaze (left, right, left_valid, right_valid):
    left_ok=is_valid_eye(left, left_valid)
    right_ok=is_valid_eye(right, right_valid)

    if left_ok and right_ok:
        combined =(
            (left[0] + right[0]) / 2,
            (left[1] + right[1]) / 2
        )
        return combined,"BOTH"

    if left_ok:
        return left,"LEFT"

    if right_ok:
        return right,"RIGHT"

    return None,"NONE"
