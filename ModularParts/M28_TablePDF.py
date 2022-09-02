from typing import List, Dict
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import os


class TablePDF:
    """This class transforms the sorted classes and represents their category assignment in the form of a table."""

    def __init__(self,
                 alternatives: List[str],
                 categories: List[str],
                 assignments: Dict[str, List[str]],
                 file_name: str):
        """
        :param alternatives: List of alternatives names (strings only)
        :param categories: List of categories names (strings only)
        :param assignments: List of imprecise alternatives assignments of each DM
        :param file_name: PDF document title
        """
        self.alternatives = alternatives
        self.categories = categories
        self.assignments = assignments
        self.out_file_name = file_name

    def __transform_assignments_to_upper_lower_bound_form(self) -> List[Dict[str, List[str]]]:
        """
        Transform assignments input to more preferable form in this method.

        :return: List of Dictionaries for each DM with lower and upper bound for each alternative
        """
        alternatives_bounds = []

        DM_alternatives_bounds = {alternative: [] for alternative in self.alternatives}
        for category_i, to_category_assignments in enumerate(self.assignments.values()):
            for alternative in to_category_assignments:
                DM_alternatives_bounds[alternative].append(self.categories[category_i])
        for (alternative, alternative_assignments) in DM_alternatives_bounds.items():
            if len(alternative_assignments) == 1:
                DM_alternatives_bounds[alternative].append(alternative_assignments[0])
        alternatives_bounds.append(DM_alternatives_bounds)

        return alternatives_bounds

    @staticmethod
    def __create_data_set(data_set, alternatives_bounds):
        """
        This class converts the data to the form used in creating the PDF file.
        """
        for alternative_dict in alternatives_bounds:
            for key in alternative_dict.keys():
                line = [key]
                for value in alternative_dict[key]:
                    line.append(value)
                data_set.append(line)

        return data_set

    def create_PDF_file(self):
        data_set = [['Alternative', 'Lower class', 'Upper class']]
        alternatives_bounds = self.__transform_assignments_to_upper_lower_bound_form()
        data_set = self.__create_data_set(data_set, alternatives_bounds)

        pdf = SimpleDocTemplate(self.out_file_name, pagesize=letter, title=self.out_file_name)

        table = Table(data_set, repeatRows=1)
        style = TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('FONT', (0, 0), (-1, -1), 'Courier', 12),
                            ('FONT', (0, 0), (-1, 0), 'Courier-Bold', 16),
                            ('LINEAFTER', (0, 0), (0, -1), 1, colors.black),
                            ('LINEAFTER', (0, 0), (1, -1), 1, colors.black),
                            ('LINEABOVE', (0, 1), (-1, -1), 1, colors.black)])
        table.setStyle(style)

        documents_elements = [table]
        pdf.build(documents_elements)
