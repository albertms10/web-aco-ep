module Jekyll
  module Capitalize
    def capitalize_first_word(input)
      firstLetter = input[0].capitalize
      firstLetter << input[1..-1]
    end
    def downcase_first_letter(input)
      firstLetter = input[0].downcase
      firstLetter << input[1..-1]
    end
  end
  module PageID
    def pageID_to_md(input)
      md = input[1...-1]
      md << ".md"
    end
    def md_to_pageID(input)
      pageID = "/"
      pageID << input[0...-3]
      pageID << "/"
    end
  end
  module DateModified
    def file_date(input)
      if ENV['JEKYLL_ENV'] == "production"
          command = "git log -1 --format='%ci' " + input
         `#{command}`
      end
    end
  end
  module DataEnCatala
    def translate_date(input)
      translation = {
        'Monday' => 'dilluns',
        'Tuesday' => 'dimarts',
        'Wednesday' => 'dimecres',
        'Thursday' => 'dijous',
        'Friday' => 'divendres',
        'Saturday' => 'dissabte',
        'Sunday' => 'diumenge',
        'January' => 'de gener',
        'February' => 'de febrer',
        'March' => 'de març',
        'April' => 'd’abril',
        'May' => 'de maig',
        'June' => 'de juny',
        'July' => 'de juliol',
        'August' => 'd’agost',
        'September' => 'de setembre',
        'October' => 'd’octubre',
        'November' => 'de novembre',
        'December' => 'de desembre'
      }
      return input.gsub(/#{translation.keys.join('|')}/, translation)
    end
    def to_date(input)
      if input.respond_to?(:strftime)
        return input
      else
        return Date.parse(input)
      end
    end

    def data_en_catala_curt(input)
      # 10 nov 2021
      if input == nil or input == ""
        return ""
      end
      data = to_date(input)
      data = data.strftime("%d %b %Y")
      translate_date(data)
    end
    def data_en_catala_mitja(input)
      # 10 de novembre de 2021
      if input == nil or input == ""
        return ""
      end
      data = to_date(input)
      data = data.strftime("%d %B de %Y")
      translate_date(data)
    end
    def data_en_catala_llarg(input)
      # diumenge 10 de novembre de 2021
      if input == nil or input == ""
        return ""
      end
      data = to_date(input)
      data = data.strftime("%A %d %B de %Y")
      translate_date(data)
    end
  end

  # https://stackoverflow.com/questions/65904200/how-to-create-assertion-in-jekyll
  module ExceptionFilter
    def raise_error(msg)
        invalid_file = @context.registers[:page]['path']
        err_msg = "On #{invalid_file}: #{msg}"
      raise err_msg
    end
  end
end

Liquid::Template.register_filter(Jekyll::Capitalize)
Liquid::Template.register_filter(Jekyll::PageID)
Liquid::Template.register_filter(Jekyll::DateModified)
Liquid::Template.register_filter(Jekyll::DataEnCatala)
Liquid::Template.register_filter(Jekyll::ExceptionFilter)
