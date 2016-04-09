#!/usr/bin/env python
# coding: utf-8

import logging
import os

from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

l = logging.getLogger(__name__)

class Thread(Base):
    __tablename__ = 'thread'

    id = Column(Integer, primary_key=True)
    board = Column(String)
    no = Column(Integer)
    com = Column(String)
    last_no = Column(Integer)
    date_updated = Column(DateTime)
    active = Column(Boolean)

    def __repr__(self):
        return """
        <Thread '%s'
            board='%s'
            no='%s'
            com='%s'
            last_post='%s',
            active='%s')
        >"""\
        % (self.id, self.board, self.no, self.com, self.last_no, self.active)


class RssDB():
    def __init__(self, db_uri, save_path):
        self.db_engine = create_engine(db_uri)
        self.db_session = sessionmaker(bind=self.db_engine)()
        self._check_config(save_path)

    def _check_config(self, save_path):
        if not os.path.exists(save_path):
            try:
                os.mkdir(save_path)
            except OSError:
                pass
        try:
            self.db_session.execute('SELECT * FROM thread')
        except OperationalError:
            self._create_db()

    def _create_db(self):
        Base.metadata.create_all(self.db_engine)
        l.info('Database created')
