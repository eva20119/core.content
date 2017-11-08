# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from core.content.testing import CORE_CONTENT_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that core.content is properly installed."""

    layer = CORE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if core.content is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'core.content'))

    def test_browserlayer(self):
        """Test that ICoreContentLayer is registered."""
        from core.content.interfaces import (
            ICoreContentLayer)
        from plone.browserlayer import utils
        self.assertIn(ICoreContentLayer, utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = CORE_CONTENT_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')
        self.installer.uninstallProducts(['core.content'])

    def test_product_uninstalled(self):
        """Test if core.content is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'core.content'))

    def test_browserlayer_removed(self):
        """Test that ICoreContentLayer is removed."""
        from core.content.interfaces import \
            ICoreContentLayer
        from plone.browserlayer import utils
        self.assertNotIn(ICoreContentLayer, utils.registered_layers())
