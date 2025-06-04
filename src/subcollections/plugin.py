import pathlib
import typing
from abc import ABC
from collections import defaultdict

from render_engine import Collection, Page, Site
from render_engine.plugins import hook_impl
from slugify import slugify


class SubCollector(ABC):
    """Perhaps an Abstract Base Class to ensure that the callable that SubCollections Uses is present"""

    def generate_subcollection(self, collection: Collection):
        """The class that creates subcollections"""
        pass


class Tags(SubCollector):
    def filter(self, page: Page, tag) -> bool:
        return tag in getattr(page, "tags", [])

    def generate_subcollection(
        self, collection: Collection
    ) -> defaultdict[str, set[Page]]:
        """Iterate through the pages in the collection looking for tags"""

        pages_by_tag = defaultdict(set)

        for page in collection:
            for tag in map(slugify, getattr(page, "tag")):
                pages_by_tag[tag].add(page)

        return pages_by_tag


class SubCollections:

    @hook_impl
    def post_build_collection(
        self,
        collection: Collection,
        site: Site,
        settings: dict[str, typing.Any],
    ) -> None:
        """
        Build After Building the collection

        Create a new collection and render it.
        """

        for subcollection in getattr(collection, "subcollections", default=[]):

            for subcollection_title, pages in subcollection.generate_subcollection():

                output_path = (
                    pathlib.Path(collection.url_for())
                    / subcollection.__class__.__title__
                    / subcollection_title
                )

                class SubCollectorPage(Page):
                    title = subcollection_title
                    template = collection.archive_template
                    routes = [output_path]
                    pages = pages

                site._render_output(output_path, SubCollectorPage)
