import os
import re
from PIL import Image, UnidentifiedImageError

from wilitools import WiliDB, UnexistRecord

from consts import MEDIA_ROOT_DIR

class Form:
    def __init__(self):
        self.errs = {}

    def validate(self) -> bool:
        return True

class CreateAreaForm(Form):
    def __init__(self, db:WiliDB):
        super().__init__()
        self.name:str = None
        self.width:float = None
        self.blueprint = None
        self.blueprint_meta:dict = None
        # self.xmin:float = None
        # self.xmax:float = None
        # self.ymin:float = None
        # self.ymax:float = None
        self._db = db


    def validate(self, request) -> bool:
        self.errs = {}

        d = request.form

        # validate name
        try:
            name = str(d['name'])
        except IndexError:
            self.errs['name'] = 'no input'
        except ValueError:
            self.errs['name'] = 'unexpected input'

        if not 'name' in self.errs:
            if name == '':
                self.errs['name'] = 'empty'

        if not 'name' in self.errs:
            pattern = re.compile('^[a-zA-Z][a-zA-Z0-9_]*')
            match = pattern.match(name)
            if match is None:
                self.errs['name'] = 'contains prohibitted letter'
            else:
                span = match.span()
                if not (span[0] == 0 and span[1] == len(name)):
                    self.errs['name'] = 'contains prohibitted letter'

        if not 'name' in self.errs:
            try:
                self._db.get_area_id(name)
            except UnexistRecord:
                self.name = name
            else:
                self.errs['name'] = 'already using'

        # validate width
        try:
            width = float(d['width'])
        except IndexError:
            self.errs['width'] = 'no input'
        except ValueError:
            self.errs['width'] = 'not number'
        else:
            if width > 0:
                self.width = width
            else:
                self.errs['width'] = 'width <= 0'

        # validate blueprint
        try:
            f = request.files['blueprint']
            blueprint = Image.open(f)
        except IndexError:
            self.errs['blueprint'] = 'no input'
        except UnidentifiedImageError:
            self.errs['blueprint'] = 'unknown file type'
        else:
            self.blueprint = blueprint
            _, ext = os.path.splitext(f.filename)
            w, h = blueprint.size
            self.blueprint_meta = {
                'extension': ext,
                'width': w, 'height': h,
                'original_name': f.filename
            }

        # if len(self.errs) == 0:
        #     # save blueprint
        #     dir = os.path.join(MEDIA_ROOT_DIR, self.name)
        #     os.makedirs(dir, mode=0o777, exist_ok=True)
        #     _, ext = os.path.splitext(f.filename)
        #     self.blueprint_path = os.path.join(dir, 'blueprint' + ext)
        #     f.save(self.blueprint_path)

        #     return True
        # else:
        #     return False
        return len(self.errs) == 0

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

        # return len(self.errs) == 0
