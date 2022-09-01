from ModularParts.M28_TablePDF import TablePDF
from DecisionProblemData import *

PromSort_assignments = {'c1': [],
                        'c2': ['a14', 'a15', 'a22', 'a23', 'a24', 'a25', 'a27',
                               'a32', 'a34', 'a35', 'a36', 'a37', 'a38', 'a39', 'a40'],
                        'c3': ['a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a9', 'a10',
                               'a11', 'a12', 'a13', 'a16', 'a18', 'a19', 'a20',
                               'a21', 'a26', 'a28', 'a29', 'a30', 'a31', 'a33'],
                        'c4': ['a1', 'a8', 'a17'],
                        'c5': []}

FlowSortI_assignments = {'c1': [],
                         'c2': ['a14', 'a15', 'a22', 'a23', 'a24', 'a25', 'a27',
                                'a32', 'a34', 'a35', 'a36', 'a37', 'a38', 'a39', 'a40'],
                         'c3': ['a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a9', 'a10',
                                'a11', 'a12', 'a13', 'a14', 'a15', 'a16', 'a18',
                                'a19', 'a20', 'a21', 'a22', 'a23', 'a24', 'a26',
                                'a27', 'a28', 'a29', 'a30', 'a31', 'a33', 'a34', 'a37', 'a40'],
                         'c4': ['a1', 'a3', 'a7', 'a8', 'a10', 'a12', 'a13', 'a17', 'a30'],
                         'c5': []}

pdf_1 = TablePDF(alternatives=alternatives,
                 categories=['c1', 'c2', 'c3', 'c4', 'c5'],
                 assignments=PromSort_assignments,
                 file_name='Alternatives_Assignments_PromSort.pdf')

pdf_2 = TablePDF(alternatives=alternatives,
                 categories=['c1', 'c2', 'c3', 'c4', 'c5'],
                 assignments=FlowSortI_assignments,
                 file_name='Alternatives_Assignments_FlowSortI.pdf')

pdf_1.create_PDF_file()
pdf_2.create_PDF_file()
