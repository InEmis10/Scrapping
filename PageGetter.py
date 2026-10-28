import requests
from bs4 import BeautifulSoup
import uuid

DEFAULT_HEADERS = {}

class Page:
    def __init__(self, url="google.com", headers=DEFAULT_HEADERS):
        self.url = url
        self.res = requests.get(url, headers)
        self.html : BeautifulSoup = BeautifulSoup(self.res.text, "html.parser")
        self.headers = headers

    def refresh(self):
        self.res = requests.get(self.url)

class Element:
    def __init__(self, tag):
        self.tag = tag

    @property
    def uuid(self) -> uuid.UUID:
        return uuid.uuid5(uuid.NAMESPACE_URL, str(self.tag))

    def getHash(self):
        return self.uuid

    def __getattr__(self, attr):
        return getattr(self.tag, attr)

    def __repr__(self):
        return f"<{self.tag.name} class={self.tag.get('class')}> - {self.uuid}"

class Attribute:
    Paragraph="p"
    Div="div"
    Button="button"
    Script="script"
    def __init__(self):
        pass

    @staticmethod
    def GetAll(page: Page, name: str | None = None, class_: str | list | None = None,
               attrs: dict | None = None, recursive: bool = True, toClass=Element):

        if toClass is not None and not issubclass(toClass, Element):
            raise "Error: toClass passed must be subclass of Element"

        kwargs = {}
        if class_ is not None:
            kwargs["class_"] = class_

        element = page.html.find_all(name, attrs=attrs or {},  recursive=recursive, **kwargs)
        return [toClass(el) for el in element]
