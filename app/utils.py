import json, os, random, time
from flask import url_for
from PIL import Image

def getNumber(length=8):
    characters = '1234567890'
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def getImage(image):
    if os.path.exists(url_for('static', filename=image)[1:]) and os.path.isfile(url_for('static', filename=image)[1:]):
        return url_for('static', filename=image+'')
    return url_for('static', filename='images/default.png')

def getImageSize(file, same=True):
    try:
        image = Image.open(file)
        w, h = image.size
        return f'{w}x{w}' if same else f'{w}x{h}'
    except:
        return None

def imagePath(url):
    return f'images/{url}'

def makeDirectory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return True
    return True

def removeFile(path):
    if os.path.exists(path) and os.path.isfile(path):
        os.remove(path)
        return True
    return False

def siteName():
    return ['Vehicle and Passenger Tracking System', 'VP Tracking System'] 

def to_dict(record, table):
    try:
        return [{column: json.loads(getattr(value, column)) \
        if isinstance(getattr(value, column), str) and \
            (getattr(value, column).startswith('{') and getattr(value, column).endswith('}')) \
            or (isinstance(getattr(value, column), str) and getattr(value, column).startswith('[') and getattr(value, column).endswith(']'))\
                else getattr(value, column) for column in \
                    table.__table__.c.keys()} for value in record]
    except:
        return {column: json.loads(getattr(record, column)) \
        if isinstance(getattr(record, column), str) and \
            (getattr(record, column).startswith('{') and getattr(record, column).endswith('}')) \
            or (isinstance(getattr(record, column), str) and getattr(record, column).startswith('[') and getattr(record, column).endswith(']'))\
                else getattr(record, column) for column in table.__table__.columns.keys()\
                    }
    
def uniqueFilename():
    return f"{random.getrandbits(64)}_{int(time.time())}"

def uploadImage(file, location, size=None, old=None, thumb=None, name=None, _type='png'):
    location = url_for('static', filename=location)[1:]
    path = makeDirectory(location)
    if not path:
        raise Exception('Directory could not be created.')

    if old:
        removeFile(os.path.join(location, old))

    filename = name if name else f"{uniqueFilename()}.{_type}"
    filepath = os.path.join(location, filename)
    try:
        image = Image.open(file)
        image = image.convert("RGBA" or "RGB")  # Normalize format
    except Exception as e:
        raise Exception(f"Invalid image uploaded: {e}")

    # Resize if needed
    if size:
        width, height = map(int, size.lower().split('x'))
        image = image.resize((width, height), Image.Resampling.LANCZOS)

    # Save resized image
    image.save(filepath, format=_type.upper())

    # Create thumbnail if specified
    if thumb:
        thumb_width, thumb_height = map(int, thumb.lower().split('x'))
        thumb_image = image.copy()
        thumb_image = thumb_image.resize((thumb_width, thumb_height), Image.Resampling.LANCZOS)
        thumb_image.save(os.path.join(location, 'thumb_' + filename), format=_type.upper())

    return filename

def verificationCode(length):
    if length == 0:
        return 0
    min_val = pow(10, length - 1)
    max_val = 0
    for _ in range(length):
        max_val = (max_val * 10) + 9
    return random.randint(min_val, max_val)

def except_(key, arrs):
        for arr in arrs:
            if key.startswith(arr) and key != 'keywords[]':
                return False
        return True

def parse_val(val):
    if val.lower() == 'true':
        return True
    if val.lower() == 'false':
        return False
    if val.isdigit():
        return int(val)
    try:
        return float(val)
    except ValueError:
        return val  # default: keep as string

def parseIfJson(field):
    try:
        return json.loads(field)
    except:
        return field