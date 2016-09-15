"""
pi-scanner
Barcode scanner project for the Raspberry Pi.
"""

import sys, argparse
import json
import gspread
from gspread.exceptions import CellNotFound
from oauth2client.client import SignedJwtAssertionCredentials


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

    args = parser.parse_args()

    oauthFile = args.oauthFile
    sheetName = args.sheetName
    worksheet = args.worksheet

    # Hardcoded column numbers for:
    # - the product barcode
    searchFilterCol = 1
    # - the product quantity
    quantityCol = 2
    # - the product name
    nameCol = 3


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
        barcode = raw_input('\nEnter the barcode: ')
        if barcode == 'quit':
            break  # Exit the program

        print('Barcode is [%s].' % barcode)
        try:
            # Search filter by column
            cell = _filterByCol(wks.findall(barcode), searchFilterCol)
            print('Barcode found at row [%s] column [%s].' % (cell.row, cell.col))

            action = raw_input('\nScan or type "ADD" or "REMOVE": ').upper()

            productCount = wks.cell(cell.row, quantityCol).value
            if productCount == '':
                productCount = 0
            else:
                productCount = int(productCount)

            if action == 'ADD':
                while True:
                    try:
                        quantity = int(raw_input('\nScan or type the quantity: '))
                    except ValueError:
                        print 'Quantity must be a positive integer, try again...'
                        continue
                    break
                wks.update_cell(cell.row, quantityCol, productCount + quantity)
            elif action == 'REMOVE':
                wks.update_cell(cell.row, quantityCol, productCount - 1)

        except CellNotFound:
            wks.add_rows(1)
            row_count = wks.row_count
            # Save barcode in the searchFilterCol column
            wks.update_cell(row_count, searchFilterCol, barcode)
            cell = _filterByCol(wks.findall(barcode), searchFilterCol)
            # Print out where the cell was added
            print('Barcode added at row [%s] column [%s].' % (cell.row, cell.col))
            print('************This is a new item please input the following information************')
            name = raw_input('\nEnter the name of the item: ')
            quantity = raw_input('\nEnter the quantity: ')

            wks.update_cell(row_count, nameCol, name)
            wks.update_cell(row_count, quantityCol, quantity)


if __name__ == '__main__':
    main()
