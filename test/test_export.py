import tempfile
import os
import unittest

from stltovoxel import do_export


class TestStlToVoxel(unittest.TestCase):
    def test_sample(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl
            do_export('data/Stanford_Bunny.stl', os.path.join(tmp_dir, 'stanford_bunny.png'), 100, 1)
            # https://ozeki.hu/p_1116-sample-stl-files-you-can-use-for-testing.html
            do_export('data/Cube_3d_printing_sample.stl', os.path.join(tmp_dir, 'Cube_3d_printing_sample.png'), 100, 1)
            do_export('data/Menger_sponge_sample.stl', os.path.join(tmp_dir, 'Menger_sponge_sample.png'), 100, 1)
            do_export('data/Eiffel_tower_sample.STL', os.path.join(tmp_dir, 'Eiffel_tower_sample.png'), 100, 1)
            # https://reprap.org/forum/read.php?88,6830
            do_export('data/HalfDonut.stl', os.path.join(tmp_dir, 'HalfDonut.png'), 100, 1)
            do_export('data/Star.stl', os.path.join(tmp_dir, 'Star.png'), 100, 1)
            do_export('data/Moon.stl', os.path.join(tmp_dir, 'Moon.png'), 100, 1)

    def test_export_xyz(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl
            do_export('data/Stanford_Bunny.stl', os.path.join(tmp_dir, 'stanford_bunny.xyz'), 100, 1)

    def test_export_svx(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # https://commons.wikimedia.org/wiki/File:Stanford_Bunny.stl
            do_export('data/Stanford_Bunny.stl', os.path.join(tmp_dir, 'stanford_bunny.svx'), 100, 1)

    def test_issue_files(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Provided by @silverscorpio in issue #16
            do_export('data/test1.stl', os.path.join(tmp_dir, 'test1.png'), 100, 1)
            # Provided by @silverscorpio in PR #18
            do_export('data/test2.stl', os.path.join(tmp_dir, 'test2.png'), 100, 1)
            # Provided by @cogitas3d in issue #13
            do_export('data/Model.stl', os.path.join(tmp_dir, 'Model.png'), 512, 1)
            do_export('data/Model.stl', os.path.join(tmp_dir, 'Model.png'), 1024, 1)

    def test_resolution(self):
        for i in range(1, 100):
            print('resolution:', i)
            with tempfile.TemporaryDirectory() as tmp_dir:
                do_export('data/Pyramid.stl', os.path.join(tmp_dir, 'Pyramid.xyz'), i, 1)

    def test_sparse_resolution(self):
        i = 1
        while i < 100:
            with tempfile.TemporaryDirectory() as tmp_dir:
                do_export('data/Cube_3d_printing_sample.stl', os.path.join(tmp_dir, 'Cube_3d_printing_sample.xyz'), i, 1)
                i += 1
                do_export('data/Menger_sponge_sample.stl', os.path.join(tmp_dir, 'Menger_sponge_sample.svx'), i, 1)
                i += 1
                do_export('data/Eiffel_tower_sample.STL', os.path.join(tmp_dir, 'Eiffel_tower_sample.svx'), i, 1)
                i += 1
