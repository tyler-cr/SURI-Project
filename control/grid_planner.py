#!/usr/bin/env python3

import numpy as np

GRID_CENTER     = 0
GRID_BOTTOM     = 1
GRID_TOP        = 2

def generate_grid_line(
        length: float = 1.0, 
        borders: bool = False, 
        waypoint_count: int = 4, 
        justify: int = GRID_CENTER) -> np.ndarray:
    """
    Generate evenly spaced waypoints along a line segment.
    
    Args:
        length: Total length of the line segment.
        borders: If True, includes edge points (0 and length) depending on justification.
                 If False, excludes edges.
        waypoint_count: Number of waypoints to generate. Must be >= 1.
        justify: Positioning strategy (GRID_CENTER, GRID_BOTTOM, GIRD_TOP).
                Only applies when borders=True. Ignored otherwise.
                 - GRID_BOTTOM: Starts at 0, ends before length.
                 - GRID_TOP: Starts after 0, ends at length.
                 - GRID_CENTER: Spans full length (0 to length) with equal spacing.
    
    Returns:
        np.ndarray: Array of waypoint positions.
    
    Raises:
        ValueError: If waypoint_count < 1 or justify is invalid.
    """

    if waypoint_count < 1:
        raise ValueError(f"waypoint_count must be >= 1, got {waypoint_count}")
    
    denominator = waypoint_count
    numerator = 0

    if borders:
        numerator = 0
        if justify == GRID_BOTTOM:
            waypoints = np.array( [length * ((numerator + i) /denominator) for i in range(denominator)])

        elif justify == GRID_TOP:
            numerator = 1
            waypoints = np.array( [length * ((numerator + i) /denominator) for i in range(denominator)])

        elif justify == GRID_CENTER:
            if denominator == 1:
                return np.array([length * .5])
            denominator = max(1, denominator-1)
            waypoints = np.array( [length * ((numerator + i) /denominator) for i in range(denominator+1)])
        else:
            raise ValueError("justify must be GRID_CENTER, GRID_BOTTOM, or GRID_TOP")

    else:
        numerator = 1    
        denominator += 1
        waypoints = np.array( [length * ((numerator + i) /denominator) for i in range(denominator - 1)])

    return waypoints

def generate_grid_2darray(
        length: float = 1.0, 
        width: float = 1.0, 
        length_borders: bool = False, 
        width_borders: bool = False,
        length_waypoint_count: int = 4,
        width_waypoint_count: int = 4, 
        length_justify: int = GRID_CENTER,
        width_justify: int = GRID_CENTER
        ) -> np.ndarray:
    """
    Generate a 2D grid of (y, x) coordinate pairs for the SURI rover.
    
    This function creates a rectangular grid by combining 1D line generation 
    for both axes using independent border and justification settings. The 
    result is a flattened NumPy array suitable for path planning or 
    batch processing.
    
    Args:
        length: Total length of the grid along the Y-axis.
        width: Total width of the grid along the X-axis.
        length_borders: If True, includes edge points (0 and length) for the Y-axis.
        width_borders: If True, includes edge points (0 and width) for the X-axis.
        length_waypoint_count: Number of waypoints along the Y-axis.
        width_waypoint_count: Number of waypoints along the X-axis.
        length_justify: Positioning strategy for Y-axis (GRID_CENTER, GRID_BOTTOM, GRID_TOP).
        width_justify: Positioning strategy for X-axis (GRID_CENTER, GRID_BOTTOM, GRID_TOP).
        
    Returns:
        np.ndarray: A 2D array of shape (N, 2) containing (y, x) coordinate pairs.
                    N = length_waypoint_count * width_waypoint_count.
                    The array is flattened in row-major order (indexing='ij').
                    
    Example:
        >>> grid = generate_grid_2darray(length=10, width=5, length_waypoint_count=2, width_waypoint_count=2)
        >>> print(grid.shape)
        (4, 2)
        >>> print(grid)
        [[0.  0. ]
         [0.  5. ]
         [10. 0. ]
         [10. 5. ]]
    """
    

    retList = []

    length_array = generate_grid_line(length=length, borders=length_borders, waypoint_count=length_waypoint_count, justify=length_justify)
    width_array = generate_grid_line(length=width, borders=width_borders, waypoint_count=width_waypoint_count, justify=width_justify)

    yy, xx = np.meshgrid(length_array, width_array, indexing='ij')

    return np.column_stack((yy.ravel(), xx.ravel()))

def generate_grid_line_tests():
    for i in range(1,11):
        print(f"Array for {i} waypoint count, justified center, borders = false")
        print(generate_grid_line(waypoint_count=i, borders=False))
        print()

        print(f"Array for {i} waypoint count, justified bottom, borders = true")
        print(generate_grid_line(waypoint_count=i, borders=True, justify=GRID_BOTTOM))
        print()

        print(f"Array for {i} waypoint count, justified center, borders = true")
        print(generate_grid_line(waypoint_count=i, borders=True, justify=GRID_CENTER))
        print()

        print(f"Array for {i} waypoint count, justified top, borders = true")
        print(generate_grid_line(waypoint_count=i, borders=True, justify=GRID_TOP))
        print()

        print()

    # Edge cases
    print("Edge case: waypoint_count=1, borders=True, center")
    print(generate_grid_line(waypoint_count=1, borders=True, justify=GRID_CENTER))

    print("Edge case: waypoint_count=1, borders=False")
    print(generate_grid_line(waypoint_count=1, borders=False))

    print("Edge case: invalid justify")
    try:
        generate_grid_line(justify=999, borders=True)
    except ValueError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    print(generate_grid_2darray(length_waypoint_count=1, width_waypoint_count=1))