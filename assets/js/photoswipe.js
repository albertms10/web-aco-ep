// npm i photoswipe --save
// npm i photoswipe-dynamic-caption-plugin --save

// Open caption and author links in a new tab
$(".pswp-caption-content a").each(function () {
  $(this).attr("target", "_blank");
  $(this).attr("rel", "noopener noreferrer");
});

var lightbox = new PhotoSwipeLightbox({
  gallery: ".galeriaDeFotos",
  childSelector: ".pswp-gallery__item",
  pswpModule: PhotoSwipe,

  paddingFn: (viewportSize) => {
    return {
      top: 30,
      bottom: 30,
      left: 70,
      right: 70,
    };
  },
});

const captionPlugin = new PhotoSwipeDynamicCaption(lightbox, {
  captionContent: ".pswp-caption-content",
  type: "auto",
  mobileLayoutBreakpoint: 800,
});

lightbox.init();
