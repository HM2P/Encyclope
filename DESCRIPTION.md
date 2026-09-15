# ENCYCLOPE

**ENCYCLOPE** is a local encyclopedia project designed to let users search, collect, store and read information directly on their computer.

The project uses **Wikipedia as its main source of information**. Articles can be searched online, downloaded and then stored in a local database. Once an article has been saved, it can be searched and read locally without having to download it again.

## Main Features

ENCYCLOPE includes several tools designed to make building a personal encyclopedia simple:

* **Article search** — Search Wikipedia for a person, place, event, scientific subject, technology, culture topic or almost any other subject.
* **Local storage** — Save articles into a local SQLite database.
* **Offline reading** — Read articles that have already been downloaded without requesting them again from Wikipedia.
* **Crawler** — Automatically explore Wikipedia pages and save multiple related articles.
* **Multiple crawlers** — Search for several subjects at the same time.
* **Article search** — Search through all locally stored articles using words or phrases.
* **Article reader** — Open and read complete stored articles.
* **Themes** — See the different subjects used to collect articles.
* **Statistics** — Check the number of stored articles, database size and available capacity.
* **Article deletion** — Delete individual articles, groups of search results or the entire database.
* **Local database** — All collected information is stored using SQLite.

## Crawler System

One of the main features of ENCYCLOPE is its crawler.

Instead of manually downloading every article, the crawler can start from a subject and automatically explore related Wikipedia pages.

For example, a user could start a crawl with:

`Mars`

The crawler can then discover related pages through Wikipedia links and save them into the local database.

It is also possible to launch multiple subjects, such as:

`Mars, Napoleon, Paris, Python`

This allows ENCYCLOPE to progressively build a large personal knowledge database.

## Local Database

ENCYCLOPE uses an SQLite database called `encyclope.db`.

The database stores information such as:

* Article titles
* Article URLs
* Article text
* Short summaries
* Themes
* Creation dates
* Links between articles

The current project is designed to support **up to 10,000 stored articles**.

This limit represents the maximum capacity configured for the current version, not the number of articles already included with the project.

## Simple and Local

ENCYCLOPE is designed to remain simple.

It does not require a complicated online account system. The database is stored locally on the user's computer, making it easy to keep a personal collection of information.

The project is written in **Python** and uses **SQLite** for local storage.

## Beta Version

⚠️ **ENCYCLOPE is currently in beta.**

The project is still under active development, so some features may be incomplete, unstable or contain bugs. Some situations may also cause unexpected errors, especially when downloading or processing certain Wikipedia pages.

The current version should therefore be considered a **development and testing version**, rather than a finished product.

The goal is to continue improving ENCYCLOPE by fixing bugs, improving the crawler, making searches faster and more reliable, improving the database and adding new features.

## Future Development

ENCYCLOPE is still evolving. Future versions may include improvements such as:

* A faster and more powerful crawler
* Better article classification
* Improved search
* Better handling of Wikipedia pages
* More database management tools
* Improved performance
* A graphical interface
* More advanced knowledge organization
* Better connections between related articles

The project may change significantly as development continues.

## Open Source Project

ENCYCLOPE is an experimental personal project created to explore programming, databases, web data collection and the creation of a local knowledge system.

The project is shared publicly so that others can discover it, test it, report bugs and potentially contribute ideas or improvements.

## Important Notice

ENCYCLOPE retrieves information from **Wikipedia**. The project does not create or verify the information contained in the original articles.

The accuracy, completeness and availability of the collected information therefore depend on the original Wikipedia pages and on the crawler's ability to process them correctly.

ENCYCLOPE should be considered a tool for collecting and organizing information, not a replacement for checking the original sources.

---

**ENCYCLOPE — A local encyclopedia built with Python.**

*Beta version — Work in progress.*
