from svgpathtools import svg2paths


def svg_to_points(svg_path, scale=1, step=1):
    """
    Convert a simple SVG file into a list of points.

    Parameters
    ----------
    svg_path : str
        The file path to the SVG file to be converted.
    scale : float, optional
        A scaling factor to apply to each path (default is 1).
    step : int, optional
        Resolution is equal to 1/step. Increasing this number results in lower resolution. (default is 1)

    Returns
    -------
    list of list of tuple
        A list where each element corresponds to a path in the SVG.
        Each path is represented as a list of (x, y) tuples
    """
    paths, _ = svg2paths(svg_path)
    all_points = []
    for path in paths:
        path_points = []
        for i in range(0, len(path), step):
            segment = path[i].scaled(scale)
            path_points.append((segment.point(0).real, segment.point(0).imag))
        all_points.append(path_points)
    return all_points
