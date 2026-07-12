from abc import ABC, abstractmethod
from bs4 import BeautifulSoup

class HTMLProcessor(ABC):
    @abstractmethod
    def process(self, html: str) -> BeautifulSoup: ...
