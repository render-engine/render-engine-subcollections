from collections import defaultdict

import pytest
from render_engine import Collection, Page, Site

from subcollections.plugin import SubCollections, SubCollector


def test_subcollection(tmp_path):
    """Tests that a subcollection will create a page with the pages"""

    class TestPage(Page):
        content = "Some Content"  # Page needs either content or a template

    page1 = TestPage()
    page2 = TestPage()
    page3 = TestPage()

    page1.title = "Page1"
    page2.title = "Page2"
    page3.title = "Page3"

    output_path = tmp_path / "output"

    site = Site()
    site.output_path = output_path

    class TestSubCollector(SubCollector):
        def generate_subcollection(self, collection: Collection):
            """The class that creates subcollections"""
            pages = defaultdict(set)

            for page in collection:
                pages[str(page.title[-1])].add(page)

            return pages

    class TestCollection(Collection):
        pages = [page1, page2, page3]
        plugins = [SubCollections]
        SubCollections = [TestSubCollector]

    site.collection(TestCollection)
    site.render()
    print(site.route_list)

    assert site.route_list["TestCollection_1"]
    assert site.route_list["TestCollection_1"].pages == [page1]
