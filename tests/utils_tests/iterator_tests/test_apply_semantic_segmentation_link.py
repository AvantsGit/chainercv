import numpy as np
import unittest

import chainer
from chainer.iterators import SerialIterator
from chainer import testing

from chainercv.utils import apply_semantic_segmentation_link


class DummySemanticSegmentationLink(chainer.Link):
    n_class = 20

    def predict(self, imgs):
        scores = list()

        for img in imgs:
            _, H, W = img.shape
            score = np.random.uniform(0, 1, size=(self.n_class, H, W))
            score /= score.sum(axis=0, keepdims=True)
            scores.append(score)

        return scores


@testing.parameterize(
    {'with_hook': False},
    {'with_hook': True},
)
class TestApplySemanticSegmentationLink(unittest.TestCase):

    def setUp(self):
        self.link = DummySemanticSegmentationLink()

        self.imgs = list()
        for _ in range(5):
            H, W = np.random.randint(8, 16, size=2)
            self.imgs.append(np.random.randint(0, 256, size=(3, H, W)))

    def test_image_dataset(self):
        dataset = self.imgs
        iterator = SerialIterator(dataset, 2, repeat=False, shuffle=False)

        if self.with_hook:
            def hook(pred_scores, gt_values):
                self.assertEqual(len(gt_values), 0)
        else:
            hook = None

        pred_scores, gt_values = apply_semantic_segmentation_link(
            self.link, iterator, hook=hook)

        self.assertEqual(len(pred_scores), len(dataset))
        self.assertEqual(len(gt_values), 0)

    def test_general_dataset(self):
        strs = ['a', 'bc', 'def', 'ghij', 'klmno']
        nums = [0, 1, 2, 3, 4]
        arrays = [np.random.uniform(size=10) for _ in range(5)]
        dataset = chainer.datasets.TupleDataset(
            self.imgs, strs, nums, arrays)
        iterator = SerialIterator(dataset, 2, repeat=False, shuffle=False)

        if self.with_hook:
            def hook(pred_scores, gt_values):
                self.assertEqual(len(gt_values), 3)
        else:
            hook = None

        pred_scores, gt_values = apply_semantic_segmentation_link(
            self.link, iterator, hook=hook)

        self.assertEqual(len(pred_scores), len(dataset))

        self.assertEqual(len(gt_values), 3)
        self.assertEqual(gt_values[0], strs)
        self.assertEqual(gt_values[1], nums)
        self.assertEqual(gt_values[2], arrays)


testing.run_module(__name__, __file__)
