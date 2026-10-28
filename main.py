import PageGetter
from PageGetter import Page
from Element.AnimeCards import AnimeCards
from core.Cache import Cache

MAIN_PAGE_URL = "https://anime-sama.to/"

MainPage = Page(MAIN_PAGE_URL)

AttributeHandler = PageGetter.Attribute()
cards : [AnimeCards] = PageGetter.Attribute.GetAll(MainPage, "a", class_ = "as-carte-lien", recursive=True, toClass=AnimeCards)
cache = Cache()


for i, el in enumerate(cards):
    print(str(i) + " " + str(el) + "; " + el.image)
    cache.Image.get(el.image, throttle=False)

cache.Drop()