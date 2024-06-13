#!/usr/bin/env python3
""" DB module"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from user import Base, User
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm.exc import NoResultFound
from typing import TypeVar
from user import Base, User


class DB:
    """ DB Class"""

    def __init__(self):
        """ Initialize a new DB instance """
        self._engine = create_engine("sqlite:///a.db", echo=False)
        Base.metadata.drop_all(self._engine)
        Base.metadata.create_all(self._engine)
        self.__session = None

    @property
    def _session(self):
        """ Memoized session object """
        if self.__session is None:
            DBSession = sessionmaker(bind=self._engine)
            self.__session = DBSession()
        return self.__session

    def add_user(self, email: str, hashed_password: str) -> User:
        """ Adds a user to the database.

        Param:
        - email (str): The email address of the user.
        - hashed_password (str): The hashed password of the user.

        Returns:
        User: An instance of the User class representing the added user.
        """
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        self._session.commit()
        return user

    def find_user_by(self, **kwargs) -> User:
        """ Finds user using key-word args

            Return: First row found in the users table
        """
        if not kwargs:
            raise InvalidRequestError

        col_names = User.__table__.columns.keys()

        for key in kwargs.keys():
            if key not in col_names:
                raise InvalidRequestError

        user = self._session.query(User).filter_by(**kwargs).first()

        if user is None:
            raise NoResultFound
        return user

    def update_user(self, user_id: int, **kwargs) -> None:
        """ Update users attributes

        Param:
        user_id(int)- The id of the user

        Returns: None
        """
        user = self.find_user_by(id=user_id)

        col_names = User.__table__.columns.keys()
        for key in kwargs.keys():
            if key not in col_names:
                raise ValueError

        for key, value in kwargs.items():
            setattr(user, key, value)

        self._session.commit()
