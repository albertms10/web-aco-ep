module Jekyll
  class EnllacExternTag < Liquid::Tag

    def initialize(tag_name, text, tokens)
      super
      @text = text
    end

    def render(context)
      "&nbsp;<a href=\"#{@text}\" target=\"_blank\" rel=\"noopener noreferrer\"><i class=\"me-1 bi bi-box-arrow-up-right\" style=\"position: relative; bottom: 0.01em;\"></i></a>"
    end
  end
end

Liquid::Template.register_tag('enllac_extern', Jekyll::EnllacExternTag)