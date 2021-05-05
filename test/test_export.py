from stltovoxel import doExport


def test_sample():
    # https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl
    doExport('data/Stanford_Bunny.stl', 'data/Stanford_Bunny.png', 100)
    # https://ozeki.hu/p_1116-sample-stl-files-you-can-use-for-testing.html
    doExport('data/Cube_3d_printing_sample.stl', 'data/Cube_3d_printing_sample.png', 100)
    doExport('data/Menger_sponge_sample.stl', 'data/Menger_sponge_sample.png', 100)
    doExport('data/Eiffel_tower_sample.STL', 'data/Eiffel_tower_sample.png', 100)
    # https://reprap.org/forum/read.php?88,6830
    doExport('data/HalfDonut.stl', 'data/HalfDonut.png', 100)
    doExport('data/Star.stl', 'data/Star.png', 100)
    doExport('data/Moon.stl', 'data/Moon.png', 100)


def test_issue_files():
    # Provided by @silverscorpio in issue #16
    doExport('data/test1.stl', 'data/test1.png', 100)
    # Provided by @silverscorpio in PR #18
    doExport('data/test2.stl', 'data/test2.png', 100)
