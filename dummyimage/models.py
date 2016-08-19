import os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

from dummyimage.forms import DummyImageForm

# TODO: move to settings
FONT_FILE = 'DroidSans.ttf'
FONT_PATH = os.path.join(os.path.dirname(__file__), 'fonts', FONT_FILE)


class DummyImage(object):

    class InvalidParams(Exception):
        def __init__(self, message, form):
            self.form = form
            super(DummyImage.InvalidParams, self).__init__(message)

    @classmethod
    def new(cls, width, height, **kwargs):
        data = kwargs.copy()
        data.update({
            'width': width,
            'height': height,
        })
        form = DummyImageForm(data=data)

        if not form.is_valid():
            raise  cls.InvalidParams("Invalid image params", form)

        # custom text
        text = form.cleaned_data['text']

        # mode. Use RGBA if transparent
        mode = 'RGBA' if form.cleaned_data.get('transparent') else 'RGB'
        width = form.cleaned_data['width']
        height = form.cleaned_data['height']
        size = (width, height)

        # allow transparent color
        if 'RGBA' == mode:
            bgcolor = None
        else:
            bgcolor = form.cleaned_data['bgcolor']

        # color allows short hex format
        image = Image.new(mode, size, bgcolor)
        draw = ImageDraw.Draw(image)

        bordercolor = form.cleaned_data['bordercolor']
        # draw border
        if not form.cleaned_data.get('noborder'):
            draw.polygon([(0, 0), (width - 1, 0), (width - 1, height - 1),
                        (0, height - 1)], outline=bordercolor)

        # draw cross
        if form.cleaned_data.get('cross'):
            draw.line([(0, 0), (width - 1, height - 1)], fill=bordercolor)
            draw.line([(0, height - 1), (width - 1, 0)], fill=bordercolor)

        # draw text centered
        if text:
            text = breakTextIntoLines(text, 15)
            font = ImageFont.truetype(FONT_PATH, 19)
            number_of_lines = len(text)
            line_height = height / (number_of_lines * 2)
            current_line_text_pos_x = line_height

            for line in text:
                center = (width / 2, current_line_text_pos_x)
                text_size = font.getsize(arrayValuesJoin(line))
                text_center = (center[0] - text_size[0] / 2, center[1] - text_size[1] / 2)
                draw.text(text_center, arrayValuesJoin(line), font=font, fill=form.cleaned_data['textcolor'])
                current_line_text_pos_x += line_height * 2

        return image

def breakTextIntoLines(text, characters_in_line):
    """
        Breaks text into lines based on the number of characters allowed in a line

        Example usage
            breakTextIntoLines('some random text', 10) // [['some', 'random'], ['text']]
            breakTextIntoLines('some random', 10) // [['some', 'random']]
    """
    text = text.split()
    lines = [[]]
    curr_line = 1
    for word in text:
        if (arrayValuesLength(lines[curr_line-1]) + len(word)) >= characters_in_line:
            curr_line+=1
            
        try:
            lines[curr_line-1].append(word)
        except IndexError:
            lines.append([word])
            
    return lines
    
def arrayValuesLength(array):
    """
        Helper function for breakTextIntoLines function.
        Returns length of strings in the array
    """
    return len(''.join(map(str,array)))

def arrayValuesJoin(array, delimiter=' '):
    return delimiter.join(map(str,array))