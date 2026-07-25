from abc import ABC, abstractmethod


class UserActivationTokenRepository(ABC):


    @abstractmethod
    def save(self, token):
        pass


    @abstractmethod
    def find_by_token(self, token):
        pass


    @abstractmethod
    def update(self, token):
        pass