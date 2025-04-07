import os
from datetime import datetime

import pymupdf
from pymupdf import Document, Page, Rect

from src.types import ExtractedData, PageData, Summary, UserInfo
from src.utils_files import FileUtils


class Writer:
    """Handle text and signature insertion in PDF forms using PyMuPDF.
    """
    def __init__(self):
        """Initializes the Writer class with predefined placeholders and font settings.
        """
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.FORM_DOC = pymupdf.open(os.path.join(current_dir, "../docs/form.pdf"))
        self.PLACEHOLDER = {
            "FIRST_PAGE": {
                "start_month": ("..../", (0, 7)),
                "start_year": ("/.... ", (3, 7)),
                "national_number": (" National number or enterprise number:", (230, 7)),
                "user_name": ("Name and first name or designation:", (230, 7)),
                "address": ("Domicile or head office (complete address):", (230, 7))
            },
            "TAX_TABLE": {
                "pattern": ".l........... , . .",
                "offset": {
                    "tax_basis": (18, 6),
                    "tax_amount": (31, 6),
                    "number": (55, 8)
                }
            },
            "FINAL_PAGE": {
                "location": ("In.................................,", (21, 8)),
                "date": (" .............................. (date)", (12, 8)),
                "name": ("declaration is certified correct and true.", (250, 10))
            }
        }

        self.completion_date = datetime.now()
        self.FONTSIZE = 12
        self.FONTNAME = "helv"

    def _process_number_to_text(
        self,
        number: float
    ) -> str:
        """Convert a numeric value to a string with comma as decimal separator.

        Args:
            number (float): Numeric value to be converted. While annotated as float, the
            method will also handle integer values correctly through string conversion.

        Returns:
            str: String representation of the number with decimal points replaced by
            commas.
        """
        str_number = f"{number}"
        return str_number.replace(".", ",")

    def _get_placeholder_coords(
        self,
        page: Page,
        placeholder_text: str
    ) -> Rect:
        """Find the coordinates of a placeholder text in the PDF.

        Args:
            page (Page): The PDF page to search in.
            placeholder_text (str): The text to locate.

        Raises:
            ValueError: If the placeholder text is not found.

        Returns:
            Rect: The bounding box of the placeholder text.
        """
        results = page.search_for(placeholder_text)
        if not results:
            raise ValueError(
                f"Placeholder text '{placeholder_text}' not found in document"
            )
        return results[0]

    def _get_offset_coords(
        self,
        page: Page,
        placeholder_key: str
    ) -> tuple[dict[str, str], dict[str, Rect]]:
        """Retrieve the adjusted coordinates and bounding boxes for placeholders.

        Args:
            page (Page): The PDF page to search in.
            placeholder_key (str): The key representing the placeholder category.

        Returns:
            tuple[dict[str, str], dict[str, Rect]]: A dictionary with adjusted coordinates
            and another with full bounding boxes.
        """
        specific_zone = self.PLACEHOLDER[placeholder_key]

        coords_to_apply, full_rects = {}, {}
        for type, text_w_offset in specific_zone.items():
            offset = text_w_offset[1]
            text_to_search = text_w_offset[0]

            cr = self._get_placeholder_coords(page, text_to_search)
            coord = (cr.x0 + offset[0], cr.y0 + offset[1])

            coords_to_apply[type] = coord
            full_rects[type] = cr

        return (coords_to_apply, full_rects)

    def _get_coords_tax_table(
        self,
        page: Page
    ) -> list[dict[str, dict[str, tuple[float, float]]]]:
        """Extract and structure coordinate information for tax table elements from a PDF
        page.

        Args:
            page (Page): A page that contains the tax table to fill.

        Returns:
            list[dict[str, dict[str, tuple[float, float]]]]: A list of structured tax
            tables where each table contains:
            - Tax rate categories (0.12%, 0.35%, etc.) mapping to:
                - 'tax_basis': Coordinate pair for tax basis amount
                - 'tax_amount': Coordinate pair for tax amount
            - 'total': Direct coordinate pair for total amount
        """
        pattern = self.PLACEHOLDER["TAX_TABLE"]["pattern"]
        table_rects = page.search_for(pattern)

        structured_tables = []
        for table in [table_rects[i:i + 9] for i in range(0, len(table_rects), 9)]:
            structured_tables.append({
                '0.12%': {'tax_basis': table[0], 'tax_amount': table[1]},
                '0.35%': {'tax_basis': table[2], 'tax_amount': table[3]},
                '1.32%_upper': {'tax_basis': table[4], 'tax_amount': table[5]},
                '1.32%_lower': {'tax_basis': table[6], 'tax_amount': table[7]},
                'total': table[8]
            })
        return structured_tables

    def _insert_text_at_coords(
        self,
        page: Page,
        coords: tuple[float, float],
        text: str,
        fontsize: bool = False
    ) -> None:
        """Insert text at given coordinates.

        Args:
            page (Page): PDF page object to fill in.
            coords (tuple[float, float]): (x, y) coordinates in PDF points where the text
            baseline will start. Follows PDF coordinate system where (0,0) is typically
            the bottom-left corner.
            text (str): Text content to insert. Will be rendered exactly as provided,
            without automatic case conversion or formatting.
        """
        page.insert_text(coords,
                         text,
                         fontsize=self.FONTSIZE if not fontsize else fontsize,
                         fontname=self.FONTNAME)

    def fill_first_box(
        self,
        page: Page,
        user_data: dict[str, str]
    ) -> Page:
        """Populate the first section of a form page with personal user information.

        Args:
            page (Page): The page pdf to fill.
            user_data (dict[str, str]): User information containing:
            - date: String in format 'DD.MM.YYYY'
            - national_number: National identification number
            - full_name: User's complete name
            - address: Street address
            - postal_code: Zip/postal code

        Returns:
            Page: Modified page object with inserted text, enabling method chaining.
        """
        FONTSIZE = 10
        coords, rects = self._get_offset_coords(page, "FIRST_PAGE")

        self._insert_text_at_coords(page,
                                    coords["start_month"],
                                    user_data["completion_date"].split('.')[1],
                                    FONTSIZE)

        self._insert_text_at_coords(page,
                                    coords["start_year"],
                                    user_data["date"].split('.')[-1][2:],
                                    FONTSIZE)

        self._insert_text_at_coords(page,
                                    coords["national_number"],
                                    user_data["national_number"],
                                    FONTSIZE)

        self._insert_text_at_coords(page,
                                    coords["user_name"],
                                    user_data["full_name"].upper(),
                                    FONTSIZE)

        self._insert_text_at_coords(page,
                                    coords["address"],
                                    user_data["address"].upper(),
                                    FONTSIZE)

        self._insert_text_at_coords(page,
                                    (rects["address"].x0 + 230, rects["address"].y1 + 8),
                                    user_data["postal_code"].upper(),
                                    FONTSIZE)
        return page

    def fill_empty_table_first_page(
        self,
        page: Page
    ) -> Page:
        """Fill an empty cell in the tax table on the first page.

        Args:
            page (Page): The PDF page containing the tax table.

        Returns:
            Page: The modified page with the filled cell.
        """
        FONTSIZE = 20
        pattern = self.PLACEHOLDER["TAX_TABLE"]["pattern"]
        rects = page.search_for(pattern)[-1]
        coords = (rects.x0 + 21, rects.y0 + 6)
        self._insert_text_at_coords(page, coords, "/", fontsize=FONTSIZE)
        return page

    def fill_empty_table_second_page(
        self,
        page: Page
    ) -> Page:
        """Fill empty cells in the tax table on the second page.

        Args:
        page (Page): The PDF page containing the tax table.

        Returns:
            Page: The modified page with the filled cells.
        """
        pattern = self.PLACEHOLDER["TAX_TABLE"]["pattern"]
        rects = page.search_for(pattern)
        coords = (rects[-2], rects[-11])

        for c in coords:
            self._insert_text_at_coords(page, (c.x0 + 21, c.y0 + 6), "/", fontsize=20)
        return page

    def fill_tax_table(
        self,
        page: Page,
        pages_data: dict[str, dict[str, dict[str, str]]]
    ) -> Page:
        """Populate tax table entries and calculates total tax amount for the tax table
        document.

        Args:
            page (Page): PDF page object containing the tax table.
            pages_data (dict[str, dict[str, dict[str, str]]]): Structured transaction data
            with:
            - First-level keys: 'page_1', 'page_2', etc.
            - Each page contains:
                'rate': Tax rate category (e.g., '0.12%', '1.32%_upper')
                'summary': Financial summary containing:
                    'TOTAL_TAX_BASIS_IN_EUR': Taxable base amount
                    'TOTAL_TAX_AMOUNT_IN_EUR': Calculated tax amount
                    'TOTAL_TRANSACTIONS': Number of transactions

        Returns:
            Page: Modified page object with populated tax table values.
        """
        table_rects = self._get_coords_tax_table(page)[0]

        total_tax_amount = 0
        for i in range(1, len(pages_data.keys())):
            page_info = pages_data.get(f'page_{i}', {})
            rate = page_info.get("rate")
            summary = page_info.get("summary", {})
            tax_basis = summary.get("TOTAL_TAX_BASIS_IN_EUR", "0")
            tax_amount = summary.get("TOTAL_TAX_AMOUNT_IN_EUR", "0")
            number = summary.get("TOTAL_TRANSACTIONS", "0")

            self._insert_text_at_coords(
                page,
                (
                    table_rects[rate]['tax_basis'].x0 + 18,
                    table_rects[rate]['tax_basis'].y0 + 6
                ),
                self._process_number_to_text(tax_basis))

            self._insert_text_at_coords(
                page,
                (
                    table_rects[rate]['tax_amount'].x0 + 31,
                    table_rects[rate]['tax_amount'].y0 + 6
                ),
                self._process_number_to_text(tax_amount))

            cr = page.search_for(rate.replace("%", " "))
            self._insert_text_at_coords(
                page,
                (
                    cr[0].x0 + 55,
                    cr[0].y0 + 8
                ),
                self._process_number_to_text(number))

            total_tax_amount += float(tax_amount)

        self._insert_text_at_coords(
            page,
            (
                table_rects["total"].x0 + 31,
                table_rects["total"].y0 + 6
            ),
            self._process_number_to_text(total_tax_amount))

        self.fill_empty_table_first_page(page)

        return page

    def fill_total_tax_amount(
        self,
        page: Page,
        total_tax_amount: float
    ) -> Page:
        """Insert the final total tax amount into the designated tax table location.

        Args:
            page (Page): PDF page object containing the tax table.
            total_tax_amount (float): Accumulated sum of all tax amounts from
            individual transactions. Should be a positive numeric value.

        Returns:
            Page: Modified page object with total tax amount inserted.
        """
        pattern = self.PLACEHOLDER["TAX_TABLE"]["pattern"]
        rects = page.search_for(pattern)[-1]

        self._insert_text_at_coords(
            page,
            (rects.x0 + 27, rects.y0 + 6),
            self._process_number_to_text(total_tax_amount))

        self.fill_empty_table_second_page(page)

        return page

    def fill_final_box(
        self,
        page: Page,
        user_name: str,
        location: str = "Brussels",
        date_format: str = "%d-%m-%Y",
        insert_signature: bool | None = None
    ) -> Page:
        """Fill predefined placeholders in the final form with user details.

        Args:
            page (Page): The PDF page to modify.
            user_name (str): The name of the user to insert.
            location (str, optional): The location to insert. Defaults to "Brussels".
            date_format (str, optional): The date format. Defaults to "%d-%m-%Y".
            insert_signature (bool | None, optional): Whether to insert a signature.
            Defaults to None.

        Returns:
            Page: The modified PDF page with the inserted details.
        """
        completion_date = self.completion_date.strftime(date_format)
        coords, rects = self._get_offset_coords(page, "FINAL_PAGE")
        self._insert_text_at_coords(page, coords["location"], location)
        self._insert_text_at_coords(page, coords["date"], completion_date)
        self._insert_text_at_coords(page, coords["name"], user_name)

        if insert_signature is True:
            directory = FileUtils.get_path("../docs")
            image_files = [
                f for f in os.listdir(directory)
                if f.lower().endswith(('.png', '.jpeg', '.jpg'))
            ]

            signature_filename = (
                max(image_files,
                    key=lambda f: os.path.getmtime(os.path.join(directory, f)))
            )

            signature_filename_path = (
                os.path.abspath(os.path.join(directory, signature_filename)))

            pix = pymupdf.Pixmap(signature_filename_path)
            scale = 0.2
            rect_width = pix.width * scale
            rect_height = pix.height * scale
            coord_sign = pymupdf.Rect(
                rects["name"].x0 + 300,
                rects["name"].y0 + 15,
                rects["name"].x0 + 300 + rect_width,
                rects["name"].y0 + 15 + rect_height
            )
            page.insert_image(coord_sign, filename=signature_filename_path)

        return page

    def fill_document(
        self,
        extracted_data: ExtractedData,
        to_sign: bool = False,
        save_it: bool = False
    ) -> Document:
        """Fill a given PDF document with extracted user data.

        Args:
            doc (Document): The PDF document to be modified.
            extracted_data (ExtractedData):
                A dictionary containing structured extracted data. Expected format:
                - 'page_0': Contains user information under 'user_infos'
                - 'page_X': Contains relevant data for each page (e.g., tax details)
            to_sign (bool, optional): If True, inserts a signature on the final page.
            Defaults to False.
            save_it (bool, optional): If True, save the filled document into the output
            folder.

        Returns:
            Document: The modified PDF document with the filled-in data.
        """
        doc = self.FORM_DOC
        page1, page2, _ = doc[0], doc[1], doc[2]
        user_data = extracted_data["page_0"]["user_infos"]

        page1 = self.fill_first_box(page1,
                                    user_data)

        page1 = self.fill_tax_table(page1,
                                    extracted_data)

        page2 = self.fill_final_box(page2,
                                    user_data["full_name"],
                                    insert_signature=to_sign)

        page2 = self.fill_total_tax_amount(page2,
                                           extracted_data["page_0"]["total_tax_amount"])

        if save_it:
            filled_date = self.completion_date.strftime("%m-%Y")
            file_path = f"../output/filled_form/MTO_completed_{filled_date}.pdf"
            doc.save(file_path)

        return doc
