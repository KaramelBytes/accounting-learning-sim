"""Optional Chromium regression checks. Start Streamlit before running this script."""
import argparse
import json
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, expect

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from engine import AccountingScenarioEngine


def select(page, combo, label):
    combo.click()
    combo.fill(label)
    page.get_by_role('option', name=label, exact=True).click()


def sidebar_open(page, opened):
    sidebar = page.get_by_test_id('stSidebar')
    # Streamlit keeps the offscreen sidebar in the DOM. Use its settled geometry.
    is_open = sidebar.evaluate('(e) => {const r=e.getBoundingClientRect(); return r.width > 100 && r.x >= -1;}')
    if is_open != opened:
        label = 'keyboard_double_arrow_left' if is_open else 'keyboard_double_arrow_right'
        page.get_by_role('button', name=label, exact=True).click()
        page.wait_for_function('''(opened) => {
            const e=document.querySelector('[data-testid="stSidebar"]');
            const r=e.getBoundingClientRect();
            return opened ? r.width > 100 && r.x >= -1 : r.width < 1 || r.right <= 1;
        }''', arg=opened)
    return sidebar


def choose_topic(page, title):
    sidebar = sidebar_open(page, True)
    select(page, sidebar.get_by_role('combobox'), title)
    sidebar.get_by_role('button', name='✦ Generate New Scenario', exact=True).click()
    expect(page.locator('.scenario-title')).to_have_text(title)


def no_overflow(page):
    return page.evaluate('''() => {
        const main = document.querySelector('[data-testid="stMain"]') || document.querySelector('section.main');
        return document.documentElement.scrollWidth <= innerWidth + 1 && main.scrollWidth <= main.clientWidth + 1;
    }''')


def enclosing_panel(heading):
    # Native container markup differs between Streamlit 1.34 and later releases.
    return heading.locator('xpath=ancestor::*[@data-testid="stVerticalBlock"][1]')


def contrast(page, selector):
    return page.locator(selector).first.evaluate('''e => {
        const rgb = value => value.match(/[\\d.]+/g).slice(0,3).map(Number);
        const lum = a => a.map(v => v/255).map(v => v<=.04045?v/12.92:((v+.055)/1.055)**2.4)
            .reduce((sum,v,i)=>sum+v*[.2126,.7152,.0722][i],0);
        const style=getComputedStyle(e);
        const root=getComputedStyle(document.documentElement);
        const bgHex=root.getPropertyValue('--bg-page').trim().slice(1);
        const backgroundRgb=[0,2,4].map(i=>parseInt(bgHex.slice(i,i+2),16));
        const colorParts=style.color.match(/[0-9.]+/g).map(Number);
        let opacity=colorParts.length>3?colorParts[3]:1;
        for(let node=e;node;node=node.parentElement) opacity*=parseFloat(getComputedStyle(node).opacity);
        const foreground=lum(rgb(style.color).map((v,i)=>v*opacity+backgroundRgb[i]*(1-opacity)));
        const background=lum(backgroundRgb);
        return {ratio:(Math.max(foreground,background)+.05)/(Math.min(foreground,background)+.05),font:parseFloat(style.fontSize),opacity};
    }''')


def review(url, output, widths=None):
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        try:
            for name, width, height, mobile in [('desktop',1440,1000,False), ('tablet',768,1024,True),
                                                ('mobile',390,844,True), ('small-mobile',320,740,True)]:
                if widths and width not in widths:
                    continue
                context = browser.new_context(viewport={'width':width,'height':height}, is_mobile=mobile,
                                              has_touch=mobile, device_scale_factor=1)
                page = context.new_page()
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.goto(url)
                start = page.get_by_role('button', name='Start practicing', exact=True)
                expect(start).to_be_visible()
                page.screenshot(animations='disabled', path=str(output / f'{name}-welcome.png'))
                start.click()
                expect(page.locator('.scenario-title')).to_be_visible()
                expect(page.locator('pre')).to_have_count(0)
                page.get_by_role('button',name='Reveal Analysis',exact=True).click()
                expect(page.get_by_text('Answer each question before revealing the analysis.',exact=True)).to_be_visible()
                report = {'size':name, 'flows':[], 'errors':errors}
                for topic in ['Special Order Decision', 'Credit Sale']:
                    choose_topic(page, topic)
                    if mobile:
                        sidebar_open(page, False)
                    page.locator('.scenario-title').scroll_into_view_if_needed()
                    expect(page.locator('pre')).to_have_count(0)
                    expect(page.locator('.lens-badge')).to_have_count(0)
                    assert no_overflow(page), f'{name}: question overflows'
                    expect(page.locator('.scenario-text')).to_be_visible()
                    page.screenshot(animations='disabled', path=str(output / f'{name}-{topic.split()[0].lower()}-question.png'))
                    labels = contrast(page, '[data-testid="stWidgetLabel"] p')
                    captions = contrast(page, '[data-testid="stCaptionContainer"], [data-testid="stCaption"], .stCaption')
                    assert captions['ratio'] >= 4.5 and captions['font'] >= 14, captions
                    assert labels['ratio'] >= 4.5 and labels['font'] >= 14, labels
                    boxes = page.get_by_role('combobox')
                    if topic == 'Special Order Decision':
                        select(page, boxes.nth(1), 'No — this is a decision, not yet a transaction')
                        select(page, boxes.nth(2), 'Incremental Analysis')
                        entered = '-123456789'
                    else:
                        select(page, boxes.nth(1), 'Debit')
                        select(page, boxes.nth(2), 'Increases')
                        select(page, boxes.nth(3), 'Cash vs. Accrual Timing')
                        entered = '123456789'
                    page.get_by_role('spinbutton').fill(entered)
                    page.get_by_role('spinbutton').press('Tab')
                    page.get_by_role('button', name='Reveal Analysis', exact=True).click()
                    summary = page.get_by_role('heading', name='Profit and cash at a glance', exact=True)
                    expect(summary).to_be_visible()
                    expect(page.get_by_role('heading', name='Full Analysis', exact=True)).to_be_attached()
                    expect(page.locator('.katex')).to_have_count(0)
                    expect(page.locator('pre')).to_have_count(0)
                    expect(page.get_by_role('spinbutton')).to_have_count(0)
                    submitted = page.get_by_test_id('stExpander').filter(has=page.get_by_text('Review your submitted answers',exact=True))
                    expect(submitted.locator('details')).not_to_have_attribute('open', '')
                    alert = page.get_by_test_id('stAlert').filter(has_text='Your answer:')
                    value = f'{float(entered):,.2f}'
                    value = '-$' + value[1:] if value.startswith('-') else '$' + value
                    expect(alert).to_contain_text(re.compile(re.escape(f'Your answer: {value}. Worked answer: ') + r'-?\$[\d,]+\.\d{2}\.'))
                    summary.scroll_into_view_if_needed()
                    page.screenshot(animations='disabled', path=str(output / f'{name}-{topic.split()[0].lower()}-summary.png'))
                    auditor = page.get_by_role('heading', name="The Auditor's View", exact=True)
                    cfo = page.get_by_role('heading', name="The CFO's View", exact=True)
                    auditor_panel, cfo_panel = enclosing_panel(auditor), enclosing_panel(cfo)
                    assert auditor_panel.count() == cfo_panel.count() == 1, 'Missing native analysis containers'
                    expect(auditor_panel).to_contain_text('Income effect (before tax)')
                    expect(cfo_panel).to_contain_text('Cash Flow Today')
                    if topic == 'Credit Sale':
                        expect(auditor_panel.locator('.journal-table')).to_have_count(2)
                        assert page.locator('.journal-table').evaluate_all('''tables=>tables.every(t=>{
                            let r=t.getBoundingClientRect();return r.left>=0&&r.right<=innerWidth+1;
                        })'''), 'Journal table exceeds screen'
                        assert auditor_panel.locator('.amount-debit,.amount-credit').evaluate_all("""amounts=>amounts.every(e=>{
                            const r=e.getBoundingClientRect(),c=e.closest('td').getBoundingClientRect();
                            return r.height<=24&&r.left>=c.left-1&&r.right<=c.right+1;
                        })"""), 'Journal amounts wrap or exceed their cells'
                    auditor.scroll_into_view_if_needed()
                    page.screenshot(animations='disabled', path=str(output / f'{name}-{topic.split()[0].lower()}-analysis.png'))
                    if mobile:
                        cfo.scroll_into_view_if_needed()
                        page.screenshot(animations='disabled', path=str(output / f'{name}-{topic.split()[0].lower()}-cfo.png'))
                    assert no_overflow(page), f'{name}: analysis overflows'
                    report['flows'].append({'topic':topic,'labels':labels,'captions':captions,'currency':value,'passed':True})
                    page.get_by_role('button', name='Next scenario', exact=True).click()
                    expect(page.locator('.scenario-title')).to_have_text(topic)
                    expect(page.get_by_role('spinbutton')).to_have_value('')
                    expect(page.get_by_role('button',name='Reveal Analysis',exact=True)).to_be_attached()
                    expect(page.locator('.comparison-grid')).to_have_count(0)
                    page.wait_for_function("""() => {
                        const r=document.querySelector('.scenario-title').getBoundingClientRect();
                        return r.top>=60&&r.top<innerHeight-60;
                    }""")
                    report['flows'][-1]['next_title_position'] = page.locator('.scenario-title').bounding_box()['y']
                    page.screenshot(animations='disabled', path=str(output / f'{name}-{topic.split()[0].lower()}-next.png'))
                # The regression affected every scenario, so inspect each narrative before reveal.
                if name == 'desktop':
                    for key, title in AccountingScenarioEngine.SCENARIO_CATALOG.items():
                        choose_topic(page, title)
                        expect(page.locator('.scenario-title')).to_have_text(title)
                        expect(page.locator('pre')).to_have_count(0)
                        expect(page.locator('.scenario-text')).not_to_have_text('')
                    report['catalog_checked'] = len(AccountingScenarioEngine.SCENARIO_CATALOG)
                assert not errors, errors
                reports.append(report)
                print(f'{name}: passed', flush=True)
                context.close()
        finally:
            browser.close()
            (output / 'results.json').write_text(json.dumps(reports, indent=2))
    return reports


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url',default='http://127.0.0.1:8501')
    parser.add_argument('--output',type=Path,default=Path('/tmp/accounting-layout-review'))
    parser.add_argument('--widths',type=int,nargs='+',help='Optional subset of 1440, 768, 390, 320')
    args = parser.parse_args()
    review(args.url, args.output, args.widths)
