from PageGetter import Element

class AnimeCards(Element):
    def __init__(self, tag):
        super().__init__(tag)

    @property
    def image(self):
        img = self.tag.find("img")
        if not img:
            raise "This element don't have image may not be AnimeCard"
        src = img.get("src")
        if not src:
            raise "This element have no image link"
        return src

    @property
    def hrefLink(self):
        return None