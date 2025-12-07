import html
from weasyprint import HTML, CSS
from press import _config
from press import utils

# PDF-Specific CSS (Classic Newspaper)
PDF_CSS = """
@page {
    size: Letter;
    margin: 0.5in;
    @top-center {
        content: "The Gemini Gazette";
        font-family: "Playfair Display", serif;
        font-size: 9pt;
        color: #666;
    }
    @bottom-center {
        content: counter(page);
        font-family: "Libre Franklin", sans-serif;
        font-size: 9pt;
    }
}

body {
    font-family: "Merriweather", "Georgia", serif;
    font-size: 9pt;
    line-height: 1.3;
    color: #111;
    margin: 0;
    padding: 0;
}

h1, h2, h3 {
    font-family: "Playfair Display", serif;
    font-weight: 700;
    margin: 0 0 5px 0;
}

/* Masthead */
.masthead {
    text-align: center;
    border-bottom: 3px double #000;
    margin-bottom: 20px;
    padding-bottom: 10px;
}
.masthead h1 { font-size: 3.5rem; margin-bottom: 5px; text-transform: uppercase; letter-spacing: -1px; }
.meta-bar { 
    display: flex; justify-content: space-between; 
    font-family: "Libre Franklin", sans-serif; font-size: 8pt; text-transform: uppercase; border-bottom: 1px solid #000; padding-bottom: 2px; margin-bottom: 5px;
}

/* Section Breaks */
.section-break {
    break-before: page;
}
.section-header {
    border-bottom: 2px solid #000;
    margin-bottom: 15px;
    display: flex; justify-content: space-between; align-items: baseline;
}
.section-header h2 { font-size: 24pt; text-transform: uppercase; }

/* Lead Story */
.lead-story {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px solid #000;
    /* column-span: all; */ /* Removed as this caused an issue with WeasyPrint 57.0 (likely older versions have bugs) */
}
.lead-story h3 { font-size: 18pt; margin-bottom: 8px; }

/* Grid / Columns */
.articles-container {
    column-count: 3;
    column-gap: 20px;
    column-fill: balance;
    text-align: justify;
}

article {
    break-inside: avoid; /* Essential for print */
    margin-bottom: 15px;
    padding-bottom: 10px;
    border-bottom: 1px dotted #ccc;
}
article h3 { font-size: 11pt; line-height: 1.1; margin-bottom: 4px; }
p { margin-bottom: 6px; text-indent: 1em; }
p:first-of-type { text-indent: 0; }

/* Comments */
.comment-section {
    background: #f0f0f0;
    padding: 5px;
    font-size: 8pt;
    margin-top: 5px;
    border: 1px solid #ddd;
}
.comment { margin-bottom: 4px; border-bottom: 1px solid #ccc; padding-bottom: 2px; }

"""

def process_article_content(article):
    # Re-use the HTML renderer's logic but maybe stricter truncation?
    # For now, let's duplicate the cleanup logic to avoid circular imports or complex deps
    # Ideally this moves to utils completely.
    title = html.escape(article.get('title', 'No Title'))
    full_text = article.get('full_content', '')
    comments_list = article.get('comments_full', [])
    
    is_defector = 'defector.com' in article.get('source_url', '')
    
    processed_text = utils.strip_all_html_and_links(full_text)
    if processed_text.lower().startswith(title.lower()):
         processed_text = processed_text[len(title):].lstrip('.- ')
         
    # Stricter truncation for PDF (approx 2000 chars max per article to fit columns)
    processed_text = utils.smart_truncate(processed_text, max_length=2000)
    
    content_html = ""
    if processed_text:
        paras = processed_text.split('\n\n')
        para_html = "".join([f"<p>{html.escape(p)}</p>" for p in paras if p.strip()])
        content_html += f'<div class="std-content">{para_html}</div>'
        
    comm_html = ""
    if comments_list:
        for c in comments_list[:4]: # Fewer comments for print
            c_clean = utils.strip_all_html_and_links(c)
            comm_html += f'<div class="comment">{html.escape(c_clean)}</div>'
        if comm_html:
            comm_html = f'<div class="comment-section"><b>Discussion</b>{comm_html}</div>'

    return title, content_html, comm_html

def render(data, stats, vol_issue_str, date_str, output_path):
    """
    Renders the issue to a PDF file using WeasyPrint.
    """
    
    # 1. Build the HTML structure (optimized for PDF)
    html_body = ""
    
    # Masthead
    html_body += f"""
    <div class="masthead">
        <div class="meta-bar">
            <span>{vol_issue_str}</span>
            <span>{date_str}</span>
            <span>Late Edition</span>
        </div>
        <h1>The Gemini Gazette</h1>
        <div style="text-align:center; font-style:italic;">"Often Wrong, Never in Doubt"</div>
    </div>
    """
    
    # Sections
    for i, section_def in enumerate(_config.SECTIONS):
        sid = section_def['id']
        articles = data.get(sid, [])
        if not articles: continue
        
        # Section Break
        if i > 0:
            html_body += '<div class="section-break"></div>'
            
        html_body += f"""
        <div class="section-header">
            <h2>{section_def['title']}</h2>
        </div>
        """
        
        # Lead Story
        if articles:
            lead = articles[0]
            l_title, l_content, l_comm = process_article_content(lead)
            html_body += f"""
            <div class="lead-story">
                <h3>{l_title}</h3>
                {l_content}
                {l_comm}
            </div>
            """
            
            # Remaining stories in columns
            if len(articles) > 1:
                html_body += '<div class="articles-container">'
                for art in articles[1:]:
                    title, content, comm = process_article_content(art)
                    html_body += f"""
                    <article>
                        <h3>{title}</h3>
                        {content}
                        {comm}
                    </article>
                    """
                html_body += '</div>'

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Libre+Franklin:wght@400;700&family=Merriweather:ital,wght@0,300;0,400;0,700;1,300&display=swap" rel="stylesheet">
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    # 2. Compile with WeasyPrint
    print("Compiling PDF with WeasyPrint...")
    try:
        # Note: We pass the CSS string directly
        HTML(string=full_html).write_pdf(output_path, stylesheets=[CSS(string=PDF_CSS)])
        print(f"PDF successfully generated: {output_path}")
        return True
    except Exception as e:
        print(f"WeasyPrint failed: {e}")
        return False