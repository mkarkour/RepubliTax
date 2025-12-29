import matplotlib.pyplot as plt
import numpy as np
from pymupdf import Page


class PDFDebugViewer:
    """
    Utility class for handling various operations and visualizations to help development.
    """
    @staticmethod
    def show_image(item, title=""):
        """
        Display a pixmap.
        Just to display Pixmap image of "item" - ignore the man behind the curtain.

        Args:
            item: A PyMuPDF page of a specific document.
            title: The title of the image. Default value to nothing.

        Generates an RGB Pixmap from item using a constant DPI and using matplotlib
        to show it inline of the notebook.
        """
        DPI = 150
        pix = item.get_pixmap(dpi=DPI)
        img = np.ndarray([pix.h, pix.w, 3], dtype=np.uint8, buffer=pix.samples_mv)
        plt.figure(dpi=DPI)
        plt.title(title)
        _ = plt.imshow(img, extent=(0, pix.w * 72 / DPI, pix.h * 72 / DPI, 0))

    def find_and_draw_coords(self, page: Page, text_to_search: str):
        """Draw a box around a specific zone.

        Args:
            page (Page): A PyMuPDF page of a specific document.
            text_to_search (str): The text to search and draw the coords.
        """
        coords_text_to_search = page.search_for(text_to_search)

        for rect in coords_text_to_search:
            page.draw_rect(rect, color=(1, 0, 0), width=2)

        self.show_image(page)
