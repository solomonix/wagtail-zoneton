from __future__ import unicode_literals

from django.contrib import messages
from django.db import models
from django.shortcuts import redirect, render
from modelcluster.contrib.taggit import ClusterTaggableManager
from modelcluster.fields import ParentalKey
from taggit.models import Tag, TaggedItemBase
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin, route
from wagtail.fields import StreamField
from wagtail.models import Orderable, Page
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from base.blocks import BaseStreamBlock


class EventsPageTag(TaggedItemBase):
    """
    This model allows us to create a many-to-many relationship between
    the EventsPage object and tags. There's a longer guide on using it at
    https://docs.wagtail.org/en/stable/reference/pages/model_recipes.html#tagging
    """

    content_object = ParentalKey(
        "EventsPage", related_name="tagged_items", on_delete=models.CASCADE
    )


class EventsPage(Page):
    """
    A Scheduled Event
    This event can be part of a series defined in the RecurringEvents snippet
    If so, it can retain the template or be changed to override it.
    """

    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This is NOT in the event, but the banner at the top of the page. Will just be a color if blank"
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This is the image associated with the event. Target about 800x450 pixels.",
    )
    body = StreamField(
        BaseStreamBlock(), verbose_name="Page body", blank=True, use_json_field=True
    )
    category = models.ForeignKey(
        'EventsCategory',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    tags = ClusterTaggableManager(through=EventsPageTag, blank=True)
    start_date = models.DateField("Event date", blank=False, null=False)
    start_time = models.TimeField("Start time", blank=True, null=True)
    end_time = models.TimeField("Ending time", blank=True, null=True)
    location = models.CharField("Where is the event?", max_length=256, blank=True, null=True)
    contact = models.CharField("Who/where to contact about the event", max_length=256, blank=True, null=True)
    open_to = models.CharField("Who is the event open to (EA, MM, FC, public, etc.)", max_length=128, blank=True, null=True)
    event_type = models.CharField("What type of event is this? (business meeting, festival, fundraiser, etc.)", max_length=64, blank=True, null=True)
    dress_code = models.CharField("Is there a dress code? What is it?", max_length=128, blank=True, null=True)
    admission_fee = models.CharField("Is there an admission fee?", max_length=64, blank=True, null=True)
#    recurring_series = models.ForeignKey(
#        'RecurringEvents',
#        blank=True,
#        null=True,
#        on_delete=models.CASCADE,
#        related_name="+",
#    )
    recurring_override = models.BooleanField("Set this so the schedule event creater doesn't override settings.", default=False)

    content_panels = Page.content_panels + [ 
        FieldPanel("header_image"),
        FieldPanel("image"),
        FieldPanel("category"),
        MultiFieldPanel(
            [
                FieldPanel("start_date"),
                FieldPanel("start_time"),
                FieldPanel("end_time"),
            ],
            heading="Scheduling Information",
        ),
        MultiFieldPanel(
            [
                FieldPanel("location"),
                FieldPanel("contact"),
                FieldPanel("open_to"),
                FieldPanel("event_type"),
                FieldPanel("dress_code"),
                FieldPanel("admission_fee"),
            ],
            heading="Extra Information",
            classname="collapsible",
        ),
        FieldPanel("body"),
        FieldPanel("tags"),
        MultiFieldPanel(
            [
#                FieldPanel("recurring_series"),
                FieldPanel("recurring_override"),
            ],
            heading="Recurring Event Overrides",
            classname="collapsible collapsed",
        ),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("body"),
    ]

    @property
    def get_tags(self):
        """
        Return all of the tags that are related to the events post into a list
        so we can access on the template.
        We're additionally adding a URL to access the EventsPage object with that tag
        """
        tags = self.tags.all()
        for tag in tags:
            tag.url = "/" + "/".join(
                s.strip("/") for s in [self.get_parent().url, "tags", tag.slug]
            )
        return tags

    # Specify the parent to an EventsPage as being EventsIndexPage
    parent_page_types = ["EventsIndexPage"]

    # Specifies what content types can exist as children of EventsPage
    # Empty list means that no child content types are allowed.
    subpage_types = []


class EventsIndexPage(RoutablePageMixin, Page):
    """
    Index page for events.
    We need to alter the page model's context to return the child page objects,
    the EventsPage objects, so that it works as an index page
    RoutablePageMixin is used to allow for a custom sub-URL for the tag views
    defined above.
    """

    introduction = models.TextField(help_text="Text to describe the events page", blank=True, null=True)
    header_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="This is NOT in the list but the header banner at the top of the page. Will be a color if blank.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("introduction"),
        FieldPanel("header_image"),
    ]
    
    # Specifies that only EventsPage objects can live under this index page
    subpage_types = ["EventsPage"]

    # Defines a method to access the children of the page (e.g. EventsPage objects).
    # On the demo site this was used on the HomePage.
    def children(self):
        return self.get_children().specific().live()
    
    # Overrides the context to list all child items, that are live, by the 
    # descending start date.
    # https://docs.wagtail.org/en/stable/getting_started/tutorial.html#overriding-context
    def get_context(self, request):
        context = super(EventsIndexPage, self).get_context(request)
        context["events"] = (
            EventsPage.objects.descendant_of(self).live().order_by("-start_date")
        )
        return context
    
    # This defines a custom view that utilizes tags. This view will return all 
    # related EventsPages for a given tag or redirect back to the EventsIndexPage.
    # More information on RoutablePages is at
    # https://docs.wagtail.org/en/stable/reference/contrib/routablepage.html
    @route(r"^tags/$", name="tag_archive")
    @route(r"^tags/([\w-]+)/$", name="tag_archive")
    def tag_archive(self, request, tag=None):
        try:
            tag = Tag.objects.get(slug=tag)
        except Tag.DoesNotExist:
            if tag:
                msg = 'There are no events tagged with "{}"'.format(tag)
                messages.add_message(request, messages.INFO, msg)
            return redirect(self.url)
        
        events = self.get_events(tag=tag)
        context = {"tag": tag, "events": events}
        return render(request, "events/events_index_page.html", context)
    
    def serve_preview(self, request, mode_name):
        # Needed for previews to work
        return self.serve(request)
    
    # Returns the child EventsPage objects for this EventsPageIndex.
    # If a tag is used then it will filter the events by tag.
    def get_events(self, tag=None):
        events = EventsPage.objects.live().descendant_of(self)
        if tag:
            events = events.filter(tags=tag)
        return events
    
    # Returns the list of Tags for all child events of this index page
    def get_child_tags(self):
        tags = []
        for event in self.get_events():
            # Not tags.append() because we don't want a list of lists
            tags += event.get_events
        events = sorted(set(tags))
        return tags


@register_snippet
class EventsCategory(index.Indexed, models.Model):
    """
    These are the categories that events can be posted under, intended
    to separate different types of calendar items.
    """
    name = models.CharField(max_length=100)

    panels = [
        FieldPanel('name'),
    ]

    search_fields = [
        index.SearchField('name'),
    ]

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Event categories'

