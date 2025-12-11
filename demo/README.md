# Fishwrap Demo / Starter Kit

This directory contains a reference implementation of a Fishwrap publication. Use this as a template to build your own.

## Structure

*   **`config.py`**: The brain of your newspaper. Define your feeds, timezone, and file paths here.
*   **`data/`**: Where your database (`articles_db.json`) and run logs live.
*   **`output/`**: Where the generated newspaper (`index.html`) is saved.
*   **`themes/basic/`**: A clean, unbranded theme to get you started.

## Customization

### Adding Feeds
Open `config.py` and add URLs to the `FEEDS` list:
```python
FEEDS = [
    "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    "https://your-favorite-blog.com/feed.xml"
]
```

### Changing Colors
Edit `themes/basic/css/style.css` to change the CSS variables:
```css
:root {
    --accent-color: #ff0000; /* Change brand color */
}
```

### Adding a Logo
1.  Place your logo in `themes/basic/static/logo.png`.
2.  Update `themes/basic/templates/layout.html` to reference it.
