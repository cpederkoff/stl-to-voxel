from stltovoxel import doExport


def test_stanford_bunny():
    # https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl
    doExport('data/Stanford_Bunny.stl', 'data/Stanford_Bunny.png', 100)


def test_issue_files():
    # Provided by @silverscorpio in issue #16
    doExport('data/test1.stl', 'data/test1.png', 99)
    # Provided by @silverscorpio in PR #18
    doExport('data/test2.stl', 'data/test2.png', 111)
