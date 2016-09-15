"""
pi-scanner
Barcode scanner project for the Raspberry Pi.
"""

import sys, argparse
import json
import gspread
from gspread.exceptions import CellNotFound
from oauth2client.client import SignedJwtAssertionCredentials

def _check_positive(value):
    ivalue = int(value)
    if ivalue < 1:
         raise argparse.ArgumentTypeError("[%s] must be a positive integer." % value)
    return ivalue

def _filterByCol(seq, col):
    for element in seq:
        if element.col == col:
            return element
    raise CellNotFound

def main():
    # Parse the command line arguments - https://docs.python.org/2/library/argparse.html
    parser = argparse.ArgumentParser(description='pi-scanner - Barcode scanner project for the Raspberry Pi.', prefix_chars='-')
    parser.add_argument('-i', dest='oauthFile', action='store', required=True, help='OAuth file.')
    parser.add_argument('-sn', dest='sheetName', action='store', required=True, help='The name of the excel sheet.')
    parser.add_argument('-ws', dest='worksheet', action='store', required=True, help='The name of the work sheet.')
    parser.add_argument('-sfc', dest='searchFilterCol', action='store', required=True, help='Column number for search filtering results.', type=_check_positive)

    args = parser.parse_args()

    oauthFile = args.oauthFile
    sheetName = args.sheetName
    worksheet = args.worksheet
    searchFilterCol = args.searchFilterCol

    print('')
    print('========================================')
    print('Input file is [%s].' % oauthFile)
    print('Excel sheet name is [%s].' % sheetName)
    print('Work sheet name is [%s].' % worksheet)
    if searchFilterCol is not None:
        print ('Search filtering on column [%s].' % searchFilterCol)
    print('========================================')

    # Login through oauth (#6) - http://gspread.readthedocs.org/en/latest/oauth2.html
    json_key = json.load(open(oauthFile))
    scope = ['https://spreadsheets.google.com/feeds']

    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope)

    # Open the specified excel sheet and worksheet - http://gspread.readthedocs.org/en/latest/index.html
    gc = gspread.authorize(credentials)
    wks = gc.open(sheetName).worksheet(worksheet)

    while True:    # Read input forever
        barcode = raw_input("\nEnter the barcode: ")
        if barcode == "quit":
            break  # Exit the program

        print('Barcode is [%s].' % barcode)
        try:
            # Search filter by col or nothing
            cell = _filterByCol(wks.findall(barcode), searchFilterCol)
            print('Barcode found at row [%s] column [%s].' % (cell.row, cell.col))



        except CellNotFound:
            wks.add_rows(1)
            row_count = wks.row_count
            # Put the barcode in the search filter row
            if searchFilterCol is not None:
                searchCol = searchFilterCol
            else:
                searchCol = 1
            # Save barcode in the search column
            wks.update_cell(row_count, 1, barcode)

            # Print out where the cell was added
            # Search filter by col or nothing
            if searchFilterCol is not None:
                cell = _filterByCol(wks.findall(barcode), searchFilterCol)
            else:
                cell = wks.find(barcode)
            print('Barcode added at row [%s] column [%s].' % (cell.row, cell.col))

if __name__ == "__main__":
    main()
