from flask import Blueprint

main = Blueprint('main', __name__)

from .home import *
from .export import *
from .quotes import *
