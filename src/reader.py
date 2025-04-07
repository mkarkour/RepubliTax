import re
from datetime import datetime

import pandas as pd
import pymupdf
import yaml
from dateutil.relativedelta import relativedelta
from pymupdf import Document, Page


class Reader:
    """
    Reader class used to extract and retrieve specific information for a given MTO report.
    """
    def get_raw_text_personal_infos(self, page: Page) -> str:
        """Extract raw text from the personal information section of a PDF page.

        Identifies the relevant section by locating the "BERLIN" header at the top
        and "TAX ON STOCK-EXCHANGE TRANSACTIONS (TST) REPORT" at the bottom,
        then extracts all text between these two markers.

        Args:
            page (Page): A PyMuPDF Page object representing the first PDF page of
            the monthly tax report to process.

        Returns:
            str: Extracted text from the identified personal information section.
            Returns empty string if no text found in the target region.

        Note:
            The coordinates system in PyMuPDF has its origin (0,0) at the top-left
            corner of the page, with y-values increasing downward.
        """
        start, end = "BERLIN", "TAX ON STOCK-EXCHANGE TRANSACTIONS (TST) REPORT"
        upper = page.search_for(start)
        lower = page.search_for(end)

        ry0 = upper[0].y0
        rx0 = page.rect.x0
        rx1 = page.rect.x1
        ry1 = lower[0].y1
        cr = pymupdf.Rect(rx0, ry0, rx1, ry1)
        return page.get_text("text", clip=cr)

    def extract_personal_information(self, page: Page) -> dict[str, str | None]:
        """Extract structured personal information from a PDF page's raw text.

        Uses regular expressions to identify and extract key personal details including:
        - Full name
        - Postal address
        - Securities account number
        - Document date

        Args:
            page (Page): PyMuPDF Page object containing the personal information section

        Returns:
            dict[str, str | None]: Dictionary with extracted information.
            Explanation:
                - full_name: Combined first and last name
                - address: Street address with postal code
                - securities_account: Account number
                - date: Document date in DD.MM.YYYY format
            Missing fields will have None values.

        Note:
            Matching is case-sensitive and depends on specific document formatting
        """
        text = self.get_raw_text_personal_infos(page)
        infos = {}

        patterns = {
            'full_name': r"(\b[A-Z][a-z]+(?:\s[A-Z][a-z]+)*)\n",
            'address': r"(?P<street>.+\n\d{4}\s\w+)",
            'securities_account': r"SECURITIES ACCOUNT\n(\d+)",
            'date': r"\nDATE\n(\d{2}\.\d{2}\.\d{4})"
        }
        for key, pattern in patterns.items():
            if match := re.search(pattern, text):
                if key == 'address':
                    matching_text = match.group(0).replace("\n", " ")
                else:
                    matching_text = match.group(1)

                infos[key] = matching_text

        total_address_list = infos['address'].split()
        infos["address"] = " ".join(total_address_list[:-2])
        infos["postal_code"] = " ".join(total_address_list[-2:])
        infos["complete_address"] = " ".join(total_address_list)

        form_date = datetime.strptime(infos['date'], "%d.%m.%Y") - relativedelta(months=1)
        infos["completion_date"] = datetime.strftime(form_date, "%d.%m.%Y")

        return infos

    def get_raw_text_banking_infos(self, page: Page) -> str:
        """Extract raw text from the banking information section of a PDF page.

        Identifies the section starting at "Where and how does the TST have to be paid?"
        and captures all text from that point to the bottom of the page.

        Args:
            page (Page): PyMuPDF Page object containing banking details

        Returns:
            str: Raw text containing bank account information and payment references
        """
        lower = page.search_for("Where and how does the TST have to be paid?")
        ry0 = lower[0].y0
        rx0 = page.rect.x0
        rx1 = page.rect.x1
        ry1 = page.rect.y1
        cr = pymupdf.Rect(rx0, ry0, rx1, ry1)
        return page.get_text("text", clip=cr)

    def extract_banking_infos(self, page: Page) -> dict[str, str]:
        """Extract structured banking information from a PDF page.

        Parses the following details from raw text:
        - Account holder name
        - IBAN number
        - BIC/SWIFT code
        - Payment reference code

        Args:
            page (Page): PyMuPDF Page object containing banking details

        Returns:
            dict[str, str]: Dictionary with extracted banking information. Typical keys:
                - Name: Account holder name
                - IBAN: International Bank Account Number
                - BIC: Bank Identifier Code
                - Payment Reference: Structured payment reference
            Values are stripped of surrounding whitespace.
        """
        text = self.get_raw_text_banking_infos(page)

        extracted_info = {}

        patterns = {
            'Name': r"Name:\s*(.+)",
            'IBAN': r"IBAN:\s*(.+)",
            'BIC': r"BIC:\s*(.+)",
            'Payment Reference': r"structured as follows:\s*\"(.+)\""
        }

        for key, pattern in patterns.items():
            if match := re.search(pattern, text):
                extracted_info[key] = match.group(1).strip()

        return extracted_info

    def extract_purpose_and_rate(self, page: Page) -> tuple[str, str]:
        """Extract tax purpose and rate from document header.

        Identifies the transaction purpose and applicable tax rate from
        the main header section containing "TAX ON STOCK-EXCHANGE TRANSACTIONS".

        Args:
            page (Page): PyMuPDF Page object containing tax header

        Returns:
            tuple[str, str]|None: (purpose_description, tax_rate_percentage) if found
            Example: ("SECURITIES", "0.12%")

        Note:
            Returns None if the pattern isn't found in the header text
        """
        sf = page.search_for("TAX ON STOCK-EXCHANGE TRANSACTIONS")
        ry0 = sf[0].y0
        rx0 = page.rect.x0
        rx1 = page.rect.x1
        ry1 = sf[0].y1
        cr = pymupdf.Rect(rx0, ry0, rx1, ry1)

        text = page.get_text("text", clip=cr).strip()

        pattern = r"FOR\s+(\w+)\s+\(([\d.]+%)\)"
        match = re.search(pattern, text)

        result = (match.group(1), match.group(2)) if match else None
        return result

    def extract_summary_infos(self, page: Page) -> dict[str, float]:
        """Extract financial summary from the bottom of a transaction table.

        Captures key totals including:
        - Total tax basis
        - Total tax amount
        - Other summary financial metrics

        Args:
            page (Page): PyMuPDF Page object containing summary section

        Returns:
            dict[str, float]: Key-value pairs of summary metrics. Typical keys:
                - "TOTAL TAX BASIS": Sum of all taxable amounts
                - "TOTAL TAX AMOUNT": Total tax liability
                Values converted to floating-point numbers
        """
        sf = page.search_for("TOTAL TAX BASIS")
        ry0 = sf[0].y0
        rx0 = page.rect.x0
        rx1 = page.rect.x1
        ry1 = page.rect.x1
        cr = pymupdf.Rect(rx0, ry0, rx1, ry1)

        lines = page.get_text("text", clip=cr).strip().split("\n")
        return {
            lines[i].rstrip(':').replace(" ", "_"): float(lines[i + 1])
            for i in range(0, len(lines), 2)
        }

    def convert_table_to_df(self, page: Page) -> pd.DataFrame:
        """Convert transaction table from PDF page to structured DataFrame.

        Processes the main transaction table located between:
        1. "TAX ON STOCK-EXCHANGE TRANSACTIONS" header
        2. "TOTAL TAX BASIS" summary section

        Returns:
            pd.DataFrame: Structured transaction data with columns:
                - ASSET_NAME: Security name (cleaned from multi-line formatting)
                - DATE: Transaction date in DD/MM/YYYY format
                - TRANSACTION: Transaction type (BUY/SELL)
                - TRADED_PRICE_IN_EUR: Unit price in euros
                - QUANTITY: Number of units traded
                - TAX_BASIS_IN_EUR: Taxable amount in euros
                - TAX_AMOUNT_IN_EUR: Calculated tax in euros

        Note:
            Requires pandas installation. All numeric columns are converted to float.
            Handles multi-line asset names and cleans formatting artifacts.
        """
        sf = page.search_for("TAX ON STOCK-EXCHANGE TRANSACTIONS")
        sf2 = page.search_for("TOTAL TAX BASIS")

        ry0 = sf[0].y1
        rx0 = page.rect.x0
        rx1 = page.rect.x1
        ry1 = sf2[0].y1
        cr = pymupdf.Rect(rx0, ry0, rx1, ry1)
        text = page.get_text(clip=cr)

        # pattern_to_apply = if "ETF" in text
        pattern = re.compile(
            # COMBINAISON:
            # r"(?P<ASSET_NAME>(?:[A-Z][^\n]*(?:\n\([A-Z][^\n]*\))?|\s*[A-Z][^\n]*)+)\n"
            # LVMH: r"(?P<ASSET_NAME>[A-Z][^\n]+(?:\n[A-Z][^\n]+)?)\n"
            # STOX EUROPE:
            r"(?P<ASSET_NAME>[A-Z].*?(?:\n\([A-Z][^\n]*\))?)\n"
            r"(?P<DATE>\d{2}/\d{2}/\d{4})\n"
            r"(?P<TRANSACTION>[A-Z]+)\n"
            r"(?P<TRADED_PRICE_IN_EUR>\d+\.\d+)\n"
            r"(?P<QUANTITY>\d+\.\d+)\n"
            r"(?P<TAX_BASIS_IN_EUR>\d+\.\d+)\n"
            r"(?P<TAX_AMOUNT_IN_EUR>\d+\.\d+)"
        )

        matches = pattern.findall(text)
        cleaned_data = [
            (t[0].split("\n", 1)[-1] if "TAX AMOUNT IN EUR" in t[0] else t[0],) + t[1:]
            for t in matches
        ]
        df = pd.DataFrame(cleaned_data, columns=[
            "ASSET_NAME",
            "DATE",
            "TRANSACTION",
            "TRADED_PRICE_IN_EUR",
            "QUANTITY",
            "TAX_BASIS_IN_EUR",
            "TAX_AMOUNT_IN_EUR",
        ])

        df["ASSET_NAME"] = df["ASSET_NAME"].str.replace("\n", " ")
        df = df.astype({
            "TRADED_PRICE_IN_EUR": float,
            "QUANTITY": float,
            "TAX_BASIS_IN_EUR": float,
            "TAX_AMOUNT_IN_EUR": float
        })

        return df

    def save_data_to_yaml(self, data) -> None:
        """Save the extracted data into a YAML status file.

        Args:
            data (_type_): Data to keep.

        Raise:

        """
        DATE_FORMAT_FILE = "%Y-%m"
        DATE_FORMAT_DATA = "%d-%m-%Y %H:%M:%S"
        YAML_DUMP_PARAMS = {
            "indent": 4,
            "allow_unicode": True,
            "sort_keys": False,
            "encoding": "utf-8"}

        current_time = datetime.now()

        filename = (
            f"output/status/status_on_{current_time.strftime(DATE_FORMAT_FILE)}.yaml"
        )
        data["page_0"]["checking_date"] = current_time.strftime(DATE_FORMAT_DATA)

        with open(filename, "w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, **YAML_DUMP_PARAMS)

    def extract_full_content(self,
                             doc: Document,
                             safe_to_yaml: str = None) -> dict[str, str]:
        """Extract structured content from a document and optionally saves to a YAML file.

        Args:
        doc: Input document object to process
        safe_to_yaml: Optional path to save extracted data as YAML.
            Filename will include current year-month if used.

        Returns:
            Nested dictionary with keys formatted as 'page_{n}' containing:
            - Page 0: user_infos, tax_authority_infos
            - Other pages: purpose, summary, df (tabular data as records)
        """
        n_pages = doc.page_count
        data = {}
        for p in range(0, n_pages):
            page = doc[p]

            if p == 0:
                user_infos = self.extract_personal_information(page)
                tax_authority_infos = self.extract_banking_infos(page)

                data[f"page_{p}"] = {
                    'user_infos': user_infos,
                    'tax_authority_infos': tax_authority_infos,
                }

            else:
                about_infos = self.extract_purpose_and_rate(page)
                high_level_info = self.extract_summary_infos(page)
                df = self.convert_table_to_df(page)

                data[f"page_{p}"] = {
                    "purpose": about_infos[0],
                    "rate": about_infos[1],
                    "summary": high_level_info,
                    "df": df.to_dict(orient="records")
                }

        total_tax_amount = sum(
            data[f"page_{i}"]["summary"]["TOTAL_TAX_AMOUNT_IN_EUR"]
            for i in range(1, len(data))
        )
        data["page_0"]["total_tax_amount"] = total_tax_amount

        if safe_to_yaml is not None:
            self.save_data_to_yaml(data)

        return data
