# -*- coding: utf-8 -*-

# Scrapy settings for hkjc project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
# http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'hkjc'

SPIDER_MODULES = ['hkjc.spiders']
NEWSPIDER_MODULE = 'hkjc.spiders'


ITEM_PIPELINES = {
    "hkjc.pipelines.SQLAlchemyPipeline": 10
}

"""
    DATABASE is kwargs dictionary for sqlalchemy.engine.url.URL http://docs.sqlalchemy.org/en/rel_0_9/core/engines.html

    :param drivername: the name of the database backend.
      This name will correspond to a module in sqlalchemy/databases
      or a third party plug-in.

    :param username: The user name.

    :param password: database password.

    :param host: The name of the host.

    :param port: The port number.

    :param database: The database name.

    :param query: A dictionary of options to be passed to the
      dialect and/or the DBAPI upon connect.

"""
DATABASE = {'drivername': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': 'vmac',
            'password': '',
            'database': 'hkraces2'}

#mysql testing
#DATABASE = {'drivername': 'sqlite', 'database': 'db.sqlite'}


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Googlebot/2.1 ( http://www.google.com/bot.html)"

#npt filter dups default 'scrapy.dupefilter.RFPDupeFilter'
# DUPEFILTER_CLASS = 'scrapy.dupefilter.BaseDupeFilter' 

# LOG_FILE = 
