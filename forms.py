import os
import re
from PIL import Image, UnidentifiedImageError

from .consts import MEDIA_ROOT_DIR

class Form:
    def __init__(self, form_dict:dict):
        self.errs = {}

    def validate(self) -> bool:
        return True


class CreateAreaForm(Form):
    def __init__(self):
        super().__init__()
        self.name:str = None
        self.width:float = None
        self.blueprint_path:str = None
        # self.xmin:float = None
        # self.xmax:float = None
        # self.ymin:float = None
        # self.ymax:float = None


    def validate(self, request) -> bool:
        self.errs = {}

        d = request.form

        try:
            name = str(d['name'])
        except IndexError:
            self.errs['name'] = 'no input'
        except ValueError:
            self.errs['name'] = 'unexpected input'
        else:
            pattern = re.compile('^[a-zA-Z][a-zA-Z0-9_]*')
            span = pattern.match(name).span()
            if span[0] == 0 and span[1] == len(name):
                self.name = name
            else:
                self.errs['name'] = 'need: 1st letter is a-z or A-Z & 2nd~ letter is a-z, A-Z, 0-9 or _'

        try:
            width = float(d['width'])
        except IndexError:
            self.errs['width'] = 'no input'
        except ValueError:
            self.errs['width'] = 'must be number'
        else:
            if width > 0:
                self.width = width
            else:
                self.errs['width'] = 'need: width > 0'

        if len(self.errs) == 0:
            f = request.files['blueprint']
            try:
                Image.open(f)
            except UnidentifiedImageError:
                self.errs['blueprint'] = 'unknown file type'
            else:
                os.mkdir(os.path.join(MEDIA_ROOT_DIR, self.name))
                _, ext = os.path.splitext(f.filename)
                self.blueprint_path = os.path.join(MEDIA_ROOT_DIR, self.name, 'blueprint' + ext)
                f.save(self.blueprint_path)

        # try:
        #     self.xmin = float(form_dict['xmin'])
        # except IndexError:
        #     self.errs['xmin'] = 'no input'
        # except ValueError:
        #     self.errs['xmin'] = 'input must be number'

        # try:
        #     self.xmax = float(form_dict['xmax'])
        # except IndexError:
        #     self.errs['xmax'] = 'no input'
        # except ValueError:
        #     self.errs['xmax'] = 'input must be number'

        # try:
        #     self.ymin = float(form_dict['ymin'])
        # except IndexError:
        #     self.errs['ymin'] = 'no input'
        # except ValueError:
        #     self.errs['ymin'] = 'input must be number'

        # try:
        #     self.ymax= float(form_dict['ymax'])
        # except IndexError:
        #     self.errs['ymax'] = 'no input'
        # except ValueError:
        #     self.errs['ymax'] = 'input must be number'

        # if self.ymin and self.ymax and self.ymin > self.ymax:
        #     self.errs['y'] = 'need ymin < ymax'

        # if self.xmin and self.xmax and self.xmin > self.xmax:
        #     self.errs['x'] = 'need xmin < xmax'

        return len(self.errs) == 0
