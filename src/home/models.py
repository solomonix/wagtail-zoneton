from __future__ import unicode_literals

from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.models import Orderable, Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet

from base.blocks import BaseStreamBlock


class HomeCarouselRelationship(Orderable, models.Model):
    """
    We use this to create the many-to-many relationship with carousel slides
    Probably not the best way to do it, but maybe other types can use them in 
    the future.
    """
    page = ParentalKey(
        "HomePage", related_name="home_slide_relationship", on_delete=models.CASCADE
    )
    slide = models.ForeignKey(
        "home.CarouselSlide", related_name="slide_home_relationship", on_delete=models.CASCADE
    )
    panels = [FieldPanel("slide")]


class HomeBoxRelationship(Orderable, models.Model):
    """
    Used to handle the relationship between home and boxes
    """
    page = ParentalKey(
        "HomePage", related_name="home_box_relationship", on_delete=models.CASCADE
    )
    box = models.ForeignKey(
        "home.FrontPageBox", related_name="box_home_relationship", on_delete=models.CASCADE
    )
    panels = [FieldPanel("box")]


class HomePage(Page):
    body = RichTextField(blank=True)
    feature_box = models.ForeignKey(
        'FrontPageFeature',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    content_panels = Page.content_panels + [
        InlinePanel(
            "home_slide_relationship",
            heading="Carousel slides",
            label="Slide",
            panels=None,
            min_num=0,
        ),
        InlinePanel(
            "home_box_relationship",
            heading="Top three boxes",
            label="Box",
            panels=None,
            min_num=0,
            max_num=3,
        ),
        FieldPanel('body'),
        FieldPanel('feature_box'),
    ]


@register_snippet
class CarouselSlide(ClusterableModel):
    """
    These are the slides that roll on the home page. The 
    HomePage model will allow for a many-to-many selection.
    """
    name = models.CharField(max_length=100)
    slide_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="+",
        help_text="Try to make this as high-resolution as is reasonable as it will span the full page.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slide_image"),
    ]

    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ["name"]


@register_snippet
class FrontPageFeature(models.Model):
    """
    These are for the featured box on teh front page.
    Only one is displayed at a time, selected from the HomePage model.
    """
    title = models.CharField(max_length=64)
    post_date = models.DateField("Leave this blank if you don't want a date to show", blank=True, null=True)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Feature block body", blank=True, use_json_field=True
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("post_date"),
        FieldPanel("body"),
    ]

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["title"]


@register_snippet
class FrontPageBox(ClusterableModel):
    """
    These are the link boxes at the top of the home page
    """
    title = models.CharField(max_length=64)
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="The image to show in the box. Shoot for 600x400 pixels.",
    )
    link_url = models.URLField("Where does clicking the box go to?")

    panels = [
        FieldPanel("title"),
        FieldPanel("image"),
        FieldPanel("link_url"),
    ]

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["title"]
    

@register_snippet
class ImportantNotice(models.Model):
    """
    These are notices that will be displayed anywhere on the website.
    Designed for cancellations, weather alerts, emergencies, etc.
    """
    ALERT_TYPE_CHOICES = [
        ("alert-standard", "Standard"),
        ("alert-warning", "Warning"),
        ("alert-error", "Emergency"),
        ("alert-info", "Informational"),
        ("alert-success", "Good News"),
        ("modal", "Pop up alert"),
    ]

    name = models.CharField(max_length=128)
    active = models.BooleanField("Is this live on the site?", default=False)
    alert_type = models.CharField(max_length=32, choices=ALERT_TYPE_CHOICES)
    body = StreamField(
        BaseStreamBlock(), verbose_name="Feature block body", blank=True, use_json_field=True
    ) 

    panels = [
        FieldPanel("name"),
        FieldPanel("active"),
        FieldPanel("alert_type"),
        FieldPanel("body"),
    ]

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ["name"]
