import tempfile
import os
import unittest

from stltovoxel import doExport


class TestStlToVoxel(unittest.TestCase):
    def test_sample(self):
        with tempfile.TemporaryDirectory() as tmpDir:
            # https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl
            doExport('data/Stanford_Bunny.stl', os.path.join(tmpDir, 'stanford_bunny.png'), 100, 1)
            # https://ozeki.hu/p_1116-sample-stl-files-you-can-use-for-testing.html
            doExport('data/Cube_3d_printing_sample.stl', os.path.join(tmpDir, 'Cube_3d_printing_sample.png'), 100, 1)
            doExport('data/Menger_sponge_sample.stl', os.path.join(tmpDir, 'Menger_sponge_sample.png'), 100, 1)
            doExport('data/Eiffel_tower_sample.STL', os.path.join(tmpDir, 'Eiffel_tower_sample.png'), 100, 1)
            # https://reprap.org/forum/read.php?88,6830
            doExport('data/HalfDonut.stl', os.path.join(tmpDir, 'HalfDonut.png'), 100, 1)
            doExport('data/Star.stl', os.path.join(tmpDir, 'Star.png'), 100, 1)
            doExport('data/Moon.stl', os.path.join(tmpDir, 'Moon.png'), 100, 1)

    def test_issue_files(self):
        with tempfile.TemporaryDirectory() as tmpDir:
            # Provided by @silverscorpio in issue #16
            doExport('data/test1.stl', os.path.join(tmpDir, 'test1.png'), 100, 1)
            # Provided by @silverscorpio in PR #18
            doExport('data/test2.stl', os.path.join(tmpDir, 'test2.png'), 100, 1)
            # Provided by @cogitas3d in issue #13
            doExport('data/Model.stl', os.path.join(tmpDir, 'Model.png'), 512, 1)
            doExport('data/Model.stl', os.path.join(tmpDir, 'Model.png'), 1024, 1)

    def test_resolution(self):
        for i in range(1, 100):
            print('resolution:', i)
            with tempfile.TemporaryDirectory() as tmpDir:
                doExport('data/Pyramid.stl', os.path.join(tmpDir, 'Pyramid.xyz'), i, 1)

    def test_sparse_resolution(self):
        i = 1
        while i < 100:
            with tempfile.TemporaryDirectory() as tmpDir:
                doExport('data/Cube_3d_printing_sample.stl', os.path.join(tmpDir, 'Cube_3d_printing_sample.xyz'), i, 1)
                i += 1
                doExport('data/Menger_sponge_sample.stl', os.path.join(tmpDir, 'Menger_sponge_sample.svx'), i, 1)
                i += 1
                doExport('data/Eiffel_tower_sample.STL', os.path.join(tmpDir, 'Eiffel_tower_sample.svx'), i, 1)
                i += 1
