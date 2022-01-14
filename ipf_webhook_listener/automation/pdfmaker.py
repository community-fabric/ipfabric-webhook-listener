#!/usr/bin/python3
from time import strftime

from fpdf import FPDF, HTMLMixin


class CreatePDF(FPDF, HTMLMixin):
    """Create PDF object."""

    def __str__(self):
        """Describe the object."""
        return 'To create PDF object.'

    def header(self):
        """Create page header."""
        # Position at 1.5 cm from top
        self.set_y(15)
        # Logo
        self.image('images/logoIPF.png', 2, 2, 33)
        # Picture
        self.image('images/headerIPF.png', 120, -15, 100)

    def footer(self):
        """Create page footer."""
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # helvetica italic 8
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(160, 160, 160)
        # Page number
        self.cell(45, 10, 'Page ' + str(self.page_no()), 0, 0, 'L')
        self.cell(100, 10, 'IP Fabric - Network Analysis Report', 0, 0, 'C')
        self.cell(45, 10, strftime("%c"), 0, 0, 'R')


class GeneratePDF:
    """Generate PDF report."""
    def __init__(self):
        self.date_now = strftime("%c")
        self.main_font = 'helvetica'
        self.pdf = CreatePDF(orientation="P", unit="mm", format="A4")
        self.pdf.set_author('author, IP Fabric')
        self.pdf.set_font(self.main_font, '', 14)
        self.pdf.set_text_color(0, 0, 0)
        self.pdf.set_fill_color(1, 33, 74)
        self.pdf.set_draw_color(150, 150, 150)
        self.table_line_height = self.pdf.font_size * 1.4
        self.fonts = {
            'bold': {'rgb': (0, 0, 0), 'style': 'B', 'size': 12},
            'default': {'rgb': (0, 0, 0), 'style': '', 'size': 12},
            'title1': {'rgb': (1, 33, 74), 'style': 'B', 'size': 18},
            'title2': {'rgb': (1, 33, 74), 'style': 'B', 'size': 14},
            'table_title': {'rgb': (230, 230, 230), 'style': 'B', 'size': 12},
        }

    def analysis_report(self, base_dataset):
        """Supply PDF object with data and output into a report file."""
        intent_rules = base_dataset.mine_intent_rules()
        mgmt_data = base_dataset.mine_management()
        platform_data = base_dataset.mine_base_data()
        snapshot_data = base_dataset.snapshots[base_dataset.snapshot_id]
        vendor_data = base_dataset.mine_vendors()

        # Adding PART 0 - First page
        self.pdf.add_page()
        self.pdf.cell(0, 100, '', 0, ln=1, align='C')
        self.pdf.set_font_size(32)
        self.pdf.set_text_color(1, 33, 74)
        self.pdf.cell(0, 20, 'Network Analysis Report', 0, ln=1, align='C')
        self.pdf.set_font_size(16)
        self.pdf.cell(0, 20, self.date_now, 0, ln=1, align='C')

        # Generating links for Table of Content
        link_analysis_summary = self.pdf.add_link()
        link_network_overview = self.pdf.add_link()
        link_management_protocols = self.pdf.add_link()
        link_vendor_mix = self.pdf.add_link()
        link_intent_rules = self.pdf.add_link()
        intent_links = dict()

        # Adding PART 1 - Table of content
        self.pdf.add_page()

        self.add_title('Table of content', 'title1')
        self.add_space()
        self.add_title_link('    1. Network Analysis Report Summary', link_analysis_summary, 'title1')
        self.add_title_link('      1.1 Network Overview', link_network_overview, 'title2')
        self.add_title_link('      1.2 Vendor Mix Overview', link_vendor_mix, 'title2')
        self.add_title_link('      1.3 Management Protocols Summary', link_management_protocols, 'title2')
        self.add_title_link('    2. Defined Intent-Based Rules (Widgets)', link_intent_rules, 'title1')
        self.add_widget_links(intent_rules, intent_links)

        # Adding PART 2 - Platform summary, vendors and management data
        self.pdf.add_page()
        self.add_link(link_analysis_summary)
        self.add_title('1. Network Analysis Report Summary', 'title1')
        self.add_text(
            "This report analyses " +
            str(platform_data['Number of devices']) +
            " devices based on the IP Fabric system's snapshot data; the system compiled the snapshot on " +
            snapshot_data.start.ctime() +
            ". Various detailed network protocols and technology parameters were compared and analyzed for risk, "
            "compliance, and potential security risks-issues divided into multiple categories or groups."
        )
        self.add_space()

        # Adding platform summary data
        self.add_platform_data(platform_data)
        self.add_space()
        self.add_link(link_network_overview)
        self.add_title('1.1 Network Overview', 'title2')
        self.add_text('Fundamental facts about the network infrastructure based on the snapshot created between '
                      + snapshot_data.start.ctime() + ' and ' + snapshot_data.end.ctime())
        self.add_space()

        # Adding vendors data
        self.add_link(link_vendor_mix)
        self.add_title('1.2 Vendor Mix Overview', 'title2')
        self.add_vendor_mix(vendor_data)

        # Adding management protocols data
        self.add_link(link_management_protocols)
        self.add_title('1.3 Management protocols summary', 'title2')
        self.add_text(
            'Network management protocols are responsible for collecting and organizing information about managed '
            'devices on IP networks and changing device behavior. Due to their nature, they form a critical part for '
            'network infrastructure management and therefore is essential to understand how they are implemented and '
            'what management systems are used to operate the network.'
        )
        self.add_space()
        self.add_text(
            'Following tables represents all detected management servers for supported management protocols.'
        )
        self.add_space()
        self.add_mgmt_data(mgmt_data)

        # Adding PART 3 - The Intent-Rules
        self.pdf.add_page()
        self.add_link(link_intent_rules)
        self.add_title('2. Defined Intent-Based Rules', 'title1')
        self.add_intent_rules(intent_rules, intent_links)

        return self.pdf.output(dest='S').encode("latin-1")

    def set_font(self, font):
        self.pdf.set_text_color(font['rgb'][0], font['rgb'][1], font['rgb'][2])
        self.pdf.set_font(self.main_font, font['style'], font['size'])

    def add_title(self, input_title, font):
        self.set_font(self.fonts[font])
        self.pdf.multi_cell(0, 8, input_title, 0, align='L')

    def add_title_link(self, input_title1, input_link1, font):
        self.set_font(self.fonts[font])
        self.pdf.cell(0, 8, input_title1, 0, align='L', ln=1, link=input_link1)

    def add_text(self, input_text):
        self.set_font(self.fonts['default'])
        self.pdf.multi_cell(0, 5, input_text, 0, align='J')

    def add_space(self):
        self.pdf.multi_cell(0, 5, '', 0, align='C')

    def add_link(self, link_name):
        self.pdf.set_link(link_name, y=self.pdf.get_y(), page=self.pdf.page_no())

    def add_widget_links(self, rules, intent_links):
        for group_num, group in enumerate(list(rules.keys()), start=1):
            intent_links[group] = self.pdf.add_link()
            self.add_title_link('      2.{} {}'.format(group_num, group), intent_links[group], 'title2')

    def add_vendor_mix(self, input_data):
        for idx, row in enumerate(input_data):
            if idx == 0:
                self.set_font(self.fonts['table_title'])
                for item in ('Vendor', '#Families', '#Platforms', '#Models', '#Devices Total'):
                    self.pdf.cell(37, self.table_line_height, item, border=1, align="C", fill=True)
                self.pdf.ln(self.table_line_height)
            self.set_font(self.fonts['default'])
            for item in ('vendor', 'familiesCount', 'platformsCount', 'modelsCount', 'devicesCount'):
                self.pdf.cell(37, self.table_line_height, str(row[item]), border=1, align="C")
            self.pdf.ln(self.table_line_height)

    def add_mgmt_data(self, mgmt_input):
        for item in mgmt_input:
            self.set_font(self.fonts['table_title'])
            self.pdf.multi_cell(0, self.table_line_height, item, border=1, align="C", fill=True)
            self.set_font(self.fonts['default'])
            self.pdf.multi_cell(0, self.table_line_height, str(mgmt_input[item]), border=1, align="L")
            self.pdf.ln(self.table_line_height)

    def add_platform_data(self, platform_input):
        for idx, item in enumerate(platform_input):
            if idx != 0:
                self.set_font(self.fonts['default'])
                self.pdf.cell(70, self.table_line_height,item, border=1, align="C")
                self.pdf.cell(116, self.table_line_height, str(platform_input[item]), border=1, align="C")
            else:
                self.set_font(self.fonts['table_title'])
                self.pdf.cell(70, self.table_line_height, item, border=1, align="C", fill=True)
                self.pdf.cell(116, self.table_line_height, platform_input[item], border=1, align="C", fill=True)
            self.pdf.ln(self.table_line_height)

    def set_intent_fill(self, str_val):
        irgb = {
            0: (115, 171, 69, 0),
            10: (93, 156, 210, 255),
            20: (255, 192, 19, 0),
            30: (255, 38, 21, 255),
        }
        if str_val in irgb.keys():
            color = irgb[str_val]
            self.pdf.set_text_color(color[3], color[3], color[3])
            self.pdf.set_fill_color(color[0], color[1], color[2])
        else:
            self.set_font(self.fonts['default'])

    def add_intent(self, input_rule):
        for item in input_rule:
            if item == 'description':
                if input_rule[item] != '':
                    self.add_text(input_rule[item].encode('latin-1', 'replace').decode('latin-1'))
                    self.add_space()
            else:
                self.set_intent_fill(item)
                value_len = len(str(input_rule[item]['value']))
                cell_size = value_len if value_len > 3 else 0
                self.pdf.cell(10 + cell_size, self.table_line_height,
                              str(input_rule[item]['value']), border=1, align="C", fill=True)
                self.pdf.set_text_color(0, 0, 0)
                self.pdf.multi_cell(180 - cell_size, self.table_line_height,
                                    input_rule[item]['description'], border=1, align="L")

    def add_intent_rules(self, intent_input, links_input):
        for group in list(intent_input.keys()):
            if list(intent_input.keys())[0] is not group:
                self.pdf.add_page()
            self.add_link(links_input[group])
            self.add_title('Widget - ' + group, 'title1')
            for intent in list(intent_input[group].keys()):
                self.add_space()
                self.add_title(intent, 'title2')
                self.set_font(self.fonts['default'])
                self.add_intent(intent_input[group][intent])
