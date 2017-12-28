Text-Unidecode
==============

.. image:: https://img.shields.io/travis/kmike/text-unidecode/master.svg
   :target: https://travis-ci.org/kmike/text-unidecode
   :alt: Build Status

text-unidecode is the most basic port of the
`Text::Unidecode <http://search.cpan.org/~sburke/Text-Unidecode-0.04/lib/Text/Unidecode.pm>`_
Perl library.

There are other Python ports of Text::Unidecode (unidecode_
and isounidecode_). unidecode_ is GPL; isounidecode_ doesn't support
Python 3 and uses too much memory.

This port is licensed under `Artistic License`_ and supports both
Python 2.x and 3.x. If you're OK with GPL, use unidecode_ (it has
better memory usage and better transliteration quality).

.. _unidecode: http://pypi.python.org/pypi/Unidecode/
.. _isounidecode: http://pypi.python.org/pypi/isounidecode/
.. _Artistic License: http://opensource.org/licenses/Artistic-Perl-1.0

Installation
------------

::

    pip install text-unidecode

Usage
-----

::

    >>> from text_unidecode import unidecode
    >>> unidecode(u'какой-то текст')
    u'kakoi-to tekst'



