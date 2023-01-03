from __future__ import unicode_literals

from django.contrib import messages 
from django.db import models
from django.shortcuts import redirect, render
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from base.blocks import BaseStreamBlock
from base.models import Person


class NewsPersonRelationship(Orderable, models.Model):
    """
    This is needed to define a relationship between a `Person` (author) and the blog post.
    A two-way relationship using a ParentalKey and a ForeignKey
    """
    page = ParentalKey(
        "NewsPage", related_name="news_person_relationship", on_delete=models.CASCADE
    )
    person = models.ForeignKey(
        "base.Person", related_name="person_news_relationship", on_delete=models.CASCADE
    )
    panels = [FieldPanel("person")]


class NewsPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the NewsPage object and tags. There's a longer guide on using it at
    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging
    """

    content_object = ParentalKey(
        "NewsPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class NewsPage(Page):
    """
    A News Article
    We access the Person object with an inline panel that references the
    ParentalKey's related_name in NewsPersonRelationship. More docs:
    https://docs.wagtail.org/en/stable/topics/pages.html#inline-models
    """

    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This is NOT in the article, but the banner at the top of the page. Will just be color if blank",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This is the image associate with the post. Target about 212x145 pixels.",
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )
    category = models.ForeignKey(
        'NewsCategory',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    tags = ClusterTaggableManager(through=NewsPageTag, blank=True)
    date_published = models.DateField("Date article published", blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("header_image"),
        FieldPanel("image"),
        FieldPanel("category"),
        FieldPanel("body"),
        FieldPanel("date_published"),
        InlinePanel(
            "news_person_relationship",
            heading="Authors",
            label="Author",
            panels=None,
            min_num=1,
        ),
        FieldPanel("tags"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    def authors(self):
        """
        Returns the NewsPage's related people. Again note that we are using
        the ParentalKey's related_name from the NewsPersonRelationship model
        to access these objects. This allows us to access the Person objects
        with a loop on the template. If we tried to access the news_person_
        relationship directly we'd print `blog.BlogPersonRelationship.None`
        """
        return Person.objects.filter(live=True, person_news_relationship__page=self)

    @property
    def get_tags(self):
        """
        Similar to the authors function above we're returning all the tags that
        are related to the news post into a list we can access on the template.
        We're additionally adding a URL to access NewsPage objects with that tag
        """
        tags = self.tags.all()
        for tag in tags:
            tag.url = "/" + "/".join(
                s.strip("/") for s in [self.get_parent().url, "tags", tag.slug]
            )
        return tags

    # Specifies parent to NewsPage as being NewsIndexPages
    parent_page_types = ["NewsIndexPage"]

    # Specifies what content types can exist as children of BlogPage.
    # Empty list means that no child content types are allowed.
    subpage_types = []


class NewsIndexPage(RoutablePageMixin, Page):
    """
    Index page for news.
    We need to alter the page model's context to return the child page objects,
    the NewsPage objects, so that it works as an index page
    RoutablePageMixin is used to allow for a custom sub-URL for the tag views
    defined above.
    """

    introduction = models.TextField(help_text="Text to describe the news page", blank=True)
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This is NOT in the list, but the header banner at the top of the page. Will be a color if blank.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("header_image"),
    ]

    # Speficies that only BlogPage objects can live under this index page
    subpage_types = ["NewsPage"]

    # Defines a method to access the children of the page (e.g. BlogPage
    # objects). On the demo site we use this on the HomePage
    def children(self):
        return self.get_children().specific().live()

    # Overrides the context to list all child items, that are live, by the
    # date that they were published
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(NewsIndexPage, self).get_context(request)
        context["posts"] = (
            NewsPage.objects.descendant_of(self).live().order_by("-date_published")
        )
        return context

    # This defines a Custom view that utilizes Tags. This view will return all
    # related BlogPages for a given Tag or redirect back to the BlogIndexPage.
    # More information on RoutablePages is at
    # https://docs.wagtail.org/en/stable/reference/contrib/routablepage.html
    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):

        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no news posts tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)

        posts = self.get_posts(tag=tag)
        context = {"tag": tag, "posts": posts}
        return render(request, "blog/news_index_page.html", context)

    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)

    # Returns the child NewsPage objects for this NewsPageIndex.
    # If a tag is used then it will filter the posts by tag.
    def get_posts(self, tag=None):
        posts = NewsPage.objects.live().descendant_of(self)
        if tag:
            posts = posts.filter(tags=tag)
        return posts

    # Returns the list of Tags for all child posts of this BlogPage.
    def get_child_tags(self):
        tags = []
        for post in self.get_posts():
            # Not tags.append() because we don't want a list of lists
            tags += post.get_tags
        tags = sorted(set(tags))
        return 


@register_snippet
class NewsCategory(index.Indexed, models.Model):
    """
    These are the categories that news can be posted under, intended 
    to separate Lodge News from Obituaries
    """
    name = models.CharField(max_length=100)

    panels =  [
        FieldPanel('name'),
    ]

    search_fields = [
        index.SearchField('name'),
    ]

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'News categories'
